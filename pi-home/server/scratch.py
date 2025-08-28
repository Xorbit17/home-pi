from datetime import datetime
from django.utils import timezone

# Suppose ts is your UNIX timestamp, e.g.:
ts = 1756378800

# Step 1: Create a naive datetime from the timestamp (in local system time)
dt_naive = datetime.fromtimestamp(ts)

# Step 2: Make it aware—assuming it's in UTC
dt_aware = timezone.make_aware(dt_naive)

print(str(dt_aware))
