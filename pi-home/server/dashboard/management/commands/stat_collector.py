from __future__ import annotations
from django.core.management.base import BaseCommand
from dashboard.models.application import MinuteSystemSample 
import psutil
from django.utils import timezone
from datetime import timedelta
import time
import json
from django.core.serializers.json import DjangoJSONEncoder

def sleep_until_monotonic(target_mono: float):
    while True:
        now = time.monotonic()
        dt = target_mono - now
        if dt <= 0:
            return
        # short chunks so Ctrl+C / SIGTERM stays responsive if you add it later
        time.sleep(min(dt, 0.05))

def next_minute_start(t=None):
    t = t or timezone.now()
    t0 = t.replace(second=0, microsecond=0)
    return t0 + timedelta(minutes=1)

def collect_one_minute():
    """Exact 60 ticks paced by monotonic time; non-blocking CPU %; returns 1-minute averages."""
    # Align to the next :00 wall clock
    minute_start = next_minute_start()
    # Compute the *monotonic* time that corresponds to that wall-clock boundary
    wall_now = timezone.now()
    mono_now = time.monotonic()
    # seconds until next minute boundary according to wall clock
    wait_s = (minute_start - wall_now).total_seconds()
    target0 = mono_now + max(0.0, wait_s)
    sleep_until_monotonic(target0)

    # Minute window: [minute_start, minute_start + 60s)
    # We'll tick precisely once per second using monotonic targets.
    TICKS = 60
    target = target0  # first tick boundary

    # prime CPU measurement (establishes baseline)
    psutil.cpu_percent(interval=None)

    cpu_vals = []
    mem_used_vals, mem_avail_vals = [], []
    swap_used_vals = []
    rx_bps_vals, tx_bps_vals = [], []

    mem_total = None
    swap_total = None

    # network baseline
    last_io = psutil.net_io_counters()
    last_mono = time.monotonic()

    for i in range(TICKS):
        # advance the next tick boundary by exactly 1.0s monotonic
        target += 1.0
        sleep_until_monotonic(target)

        # CPU: non-blocking; value is % since previous call (≈1 second window)
        cpu = psutil.cpu_percent(interval=None)
        cpu_vals.append(cpu)

        # Memory / Swap
        vm = psutil.virtual_memory()
        if mem_total is None:
            mem_total = int(vm.total)
        mem_used_vals.append(int(vm.used))
        mem_avail_vals.append(int(vm.available))

        sm = psutil.swap_memory()
        if swap_total is None:
            swap_total = int(sm.total) if sm.total else None
        if sm.total:
            swap_used_vals.append(int(sm.used))

        # Network B/s from monotonic-timed deltas
        now_mono = time.monotonic()
        io = psutil.net_io_counters()
        dt = max(1e-6, now_mono - last_mono)   # protect division
        drx = io.bytes_recv - last_io.bytes_recv
        dtx = io.bytes_sent - last_io.bytes_sent
        if drx >= 0:
            rx_bps_vals.append(drx / dt)
        if dtx >= 0:
            tx_bps_vals.append(dtx / dt)
        last_io, last_mono = io, now_mono

    def avg(vals):
        return (sum(vals) / len(vals))

    return {
        "minute": minute_start,
        "cpu_percent_avg": avg(cpu_vals) or 0.0,
        "mem_total": mem_total or 0,
        "mem_used_avg": int(avg(mem_used_vals) or 0),
        "mem_available_avg": int(avg(mem_avail_vals) or 0),
        "swap_total": swap_total,
        "swap_used_avg": int(avg(swap_used_vals)) if swap_used_vals else None,
        "rx_bps_avg": avg(rx_bps_vals),
        "tx_bps_avg": avg(tx_bps_vals),
    }

class Command(BaseCommand):
    help = "Starts long running service that gathers system stats"

    def handle(self, *args, **options):
        while True:
            row = collect_one_minute()
            MinuteSystemSample.objects.update_or_create(
                minute=row["minute"],
                defaults=row,
            )
                

