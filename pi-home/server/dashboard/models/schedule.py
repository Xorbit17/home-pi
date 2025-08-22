# app/models/schedule.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from zoneinfo import ZoneInfo
from constants import MODE_CHOICES, NEWS_MODE, PHOTO_MODE, WEEKDAY_CHOICES

def _minutes_since_midnight(t: time) -> int:
    """Treat 00:00 as 24:00 when used as an 'end' bound (handled by caller)."""
    return t.hour * 60 + t.minute

def _end_minutes(end_t: time) -> int:
    """Interpret end=00:00 as end-of-day (24:00)."""
    mins = _minutes_since_midnight(end_t)
    return 24 * 60 if mins == 0 else mins

@dataclass
class _Window:
    start_min: int    # inclusive
    end_min: int      # exclusive
    mode: str

# ==== Models =================================================================

class Display(models.Model):
    """
    A physical e-ink frame (or logical display).
    You can have multiple with independent schedules.
    """
    name = models.CharField(max_length=100, unique=True)
    hostname = models.CharField(
        max_length=255,
        unique=True,
        help_text="Pi's hostname used by the device and to identify it when it calls home.",
    )
    host = models.CharField(
        max_length=255,
        help_text="How the server reaches the device, e.g. 'http://hallway-pi:8080' or 'http://192.168.1.52:8080'",
    )
    timezone = models.CharField(max_length=64, default="Europe/Brussels")
    default_mode = models.CharField(max_length=16, choices=MODE_CHOICES, default=PHOTO_MODE)
    override_mode = models.CharField(max_length=16, choices=MODE_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Display"
        verbose_name_plural = "Displays"

    def __str__(self) -> str:
        return self.name

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)

    def clear_expired_override(self, now: Optional[datetime] = None) -> None:
        now = (now or timezone.now())
        if self.override_mode and self.override_expires_at and now >= self.override_expires_at:
            self.override_mode = None
            self.override_expires_at = None
            self.save(update_fields=["override_mode", "override_expires_at"])

class WeeklyRule(models.Model):
    """
    A single window for a specific weekday.
    Example: Mon 00:00-09:00 -> news; Mon 09:00-12:00 -> photo; etc.
    Duplicate multiple rules per weekday to build the day's schedule.
    """
    display = models.ForeignKey(Display, on_delete=models.CASCADE, related_name="weekly_rules")
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)  # 0=Mon .. 6=Sun
    start_time = models.TimeField(help_text="Inclusive local start")
    end_time = models.TimeField(help_text="Exclusive local end; use 00:00 for 'until midnight'")
    mode = models.CharField(max_length=16, choices=MODE_CHOICES, default=PHOTO_MODE)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Weekly Rule"
        verbose_name_plural = "Weekly Rules"
        indexes = [
            models.Index(fields=["display", "weekday", "active"]),
        ]
        ordering = ["display", "weekday", "start_time"]

    def __str__(self) -> str:
        st = self.start_time.strftime("%H:%M")
        et = self.end_time.strftime("%H:%M") if self.end_time != time(0, 0) else "24:00"
        return f"{self.display} [{self.get_weekday_display()}] {st}-{et} → {self.mode}"

    # ---- validation: overlaps on same weekday/display ----
    def clean(self):
        if self.start_time == self.end_time:
            raise ValidationError("start_time and end_time cannot be equal.")

        # Overlap check (same display+weekday, active rules)
        start_min = _minutes_since_midnight(self.start_time)
        end_min = _end_minutes(self.end_time)

        qs = WeeklyRule.objects.filter(display=self.display, weekday=self.weekday, active=True)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        for other in qs:
            o_start = _minutes_since_midnight(other.start_time)
            o_end = _end_minutes(other.end_time)
            # intervals [start, end)
            overlap = not (end_min <= o_start or o_end <= start_min)
            if overlap:
                raise ValidationError(
                    f"Overlaps with rule: {other.start_time.strftime('%H:%M')}-"
                    f"{other.end_time.strftime('%H:%M') if other.end_time != time(0,0) else '24:00'}"
                )

    # ---- resolution utilities -------------------------------------------------

    @staticmethod
    def _windows_for_day(display: Display, weekday: int) -> list[_Window]:
        rules = (WeeklyRule.objects
                 .filter(display=display, weekday=weekday, active=True)
                 .order_by("start_time"))
        windows: list[_Window] = []
        for r in rules:
            s = _minutes_since_midnight(r.start_time)
            e = _end_minutes(r.end_time)
            windows.append(_Window(start_min=s, end_min=e, mode=r.mode))
        return windows

    @staticmethod
    def resolve_mode(display: Display, at: Optional[datetime] = None) -> str:
        """
        Decide which mode should be active right now for this display.
        Honors temporary overrides; falls back to default_mode if no rule matches.
        """
        # Clear expired override if needed
        display.clear_expired_override()

        # If an override is active, it wins
        if display.override_mode and display.override_expires_at:
            now_utc = timezone.now()
            if now_utc < display.override_expires_at:
                return display.override_mode

        # Evaluate local schedule
        local_now = (at or timezone.now()).astimezone(display.tz)
        weekday = local_now.weekday()
        minutes = local_now.hour * 60 + local_now.minute

        windows = WeeklyRule._windows_for_day(display, weekday)
        for w in windows:
            if w.start_min <= minutes < w.end_min:
                return w.mode

        # If nothing matched (e.g., schedule gaps), default
        return display.default_mode

    @staticmethod
    def next_boundary_for_display(display: Display, now_local: Optional[datetime] = None) -> Optional[datetime]:
        """
        Find the next *local* datetime when the schedule changes (next window start).
        Used to set override expiry conveniently.
        """
        if now_local is None:
            now_local = timezone.now().astimezone(display.tz)

        weekday = now_local.weekday()
        minutes = now_local.hour * 60 + now_local.minute

        # Helper to build a local datetime for a given day/minute
        def as_dt(day_offset: int, minute_mark: int) -> datetime:
            target_date = (now_local.date() + timedelta(days=day_offset))
            hh, mm = divmod(minute_mark, 60)
            return datetime(target_date.year, target_date.month, target_date.day, hh, mm, tzinfo=display.tz)

        # Today: any window starting later today?
        todays = WeeklyRule._windows_for_day(display, weekday)
        for w in todays:
            if w.start_min > minutes:
                return as_dt(0, w.start_min)

        # Otherwise, find the first window tomorrow or later (scan up to a week)
        for step in range(1, 8):
            wd = (weekday + step) % 7
            wins = WeeklyRule._windows_for_day(display, wd)
            if wins:
                return as_dt(step, wins[0].start_min)

        return None  # no rules at all
