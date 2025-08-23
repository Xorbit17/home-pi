# from datetime import datetime, time, timedelta
# from zoneinfo import ZoneInfo
# from django.db.models import Q
# from dashboard.models.calendar import CalendarOccurrence
# from constants import LOCAL_TZ

# def _day_bounds(dt_local):
#     start = datetime.combine(dt_local.date(), time(0,0,0, tzinfo=LOCAL_TZ))
#     end = start + timedelta(days=1)
#     return start, end

# def today_events():
#     now = datetime.now(LOCAL_TZ)
#     start_local, end_local = _day_bounds(now)
#     start_utc = start_local.astimezone(ZoneInfo("UTC"))
#     end_utc = end_local.astimezone(ZoneInfo("UTC"))
#     qs = (CalendarOccurrence.objects
#           .filter(instance_start__gte=start_utc,
#                   instance_start__lt=end_utc,
#                   canceled=False)
#           .order_by("-all_day", "instance_start"))  # all-day first
#     return list(qs)

# def next_7_days():
#     now = datetime.now(LOCAL_TZ)
#     start_local, _ = _day_bounds(now)  # midnight today
#     end_local = start_local + timedelta(days=7)
#     start_utc = start_local.astimezone(ZoneInfo("UTC"))
#     end_utc = end_local.astimezone(ZoneInfo("UTC"))
#     qs = (CalendarOccurrence.objects
#           .filter(instance_start__gte=start_utc,
#                   instance_start__lt=end_utc,
#                   canceled=False)
#           .order_by("-all_day", "instance_start"))
#     return list(qs)
