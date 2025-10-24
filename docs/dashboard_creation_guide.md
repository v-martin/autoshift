# Creating Dashboard Screenshots for Documentation

Follow these steps to capture screenshots of your AutoShift dashboard for documentation:

## Setup Test Data

1. Create some test data to populate your dashboard:

```
# Access Django shell
docker-compose exec app python manage.py shell

# In the shell, create test data
from user.models import User
from warehouses.models import Warehouse
from shifts.models import Shift
from django.utils import timezone
import datetime

# Create warehouses if needed
warehouse1 = Warehouse.objects.create(name="North Warehouse", location="123 North St")
warehouse2 = Warehouse.objects.create(name="South Warehouse", location="456 South St")
warehouse3 = Warehouse.objects.create(name="East Warehouse", location="789 East St")

# Create users if needed
admin_user = User.objects.create_superuser(
    email="admin@example.com", 
    password="adminpassword",
    username="admin",
    role="admin"
)

worker1 = User.objects.create_user(
    email="worker1@example.com", 
    password="worker1password",
    username="worker1",
    role="worker"
)

worker2 = User.objects.create_user(
    email="worker2@example.com", 
    password="worker2password",
    username="worker2",
    role="worker"
)

# Create shifts
current_time = timezone.now().time()
start_time = datetime.time(9, 0)
end_time = datetime.time(17, 0)

# Monday shifts
Shift.objects.create(day_of_week="monday", start_time=start_time, end_time=end_time, user=worker1, warehouse=warehouse1)
Shift.objects.create(day_of_week="monday", start_time=start_time, end_time=end_time, user=worker2, warehouse=warehouse2)

# Tuesday shifts
Shift.objects.create(day_of_week="tuesday", start_time=start_time, end_time=end_time, user=worker1, warehouse=warehouse2)
Shift.objects.create(day_of_week="tuesday", start_time=start_time, end_time=end_time, user=worker2, warehouse=warehouse3)

# Wednesday shifts
Shift.objects.create(day_of_week="wednesday", start_time=start_time, end_time=end_time, user=worker1, warehouse=warehouse3)
Shift.objects.create(day_of_week="wednesday", start_time=start_time, end_time=end_time, user=worker2, warehouse=warehouse1)

# Create some optimized shifts
Shift.objects.create(day_of_week="thursday", start_time=start_time, end_time=end_time, user=worker1, warehouse=warehouse1, is_optimized=True)
Shift.objects.create(day_of_week="friday", start_time=start_time, end_time=end_time, user=worker2, warehouse=warehouse2, is_optimized=True)
Shift.objects.create(day_of_week="saturday", start_time=start_time, end_time=end_time, user=worker1, warehouse=warehouse3, is_optimized=True)
```

## Capturing Screenshots

1. Log in to your application with the admin account.
2. Navigate to http://localhost:8000/dashboard/
3. Use browser developer tools to ensure the page looks good at various screen sizes.
4. Take screenshots of:
   - The full dashboard
   - Each chart section
   - The shifts table
   - Any interactive elements

5. Save screenshots to the `docs/` directory, naming them clearly:
   - `dashboard_overview.png` - Full dashboard view
   - `weekly_shift_chart.png` - The weekly shift distribution chart
   - `warehouse_staff_chart.png` - The warehouse staff distribution chart
   - `shift_table.png` - The shifts table

## Adding Screenshots to Documentation

1. Reference screenshots in the README.md and other documentation.
2. For the main dashboard example in README.md, use the full dashboard view.
3. Consider creating a more detailed dashboard guide with all screenshots for in-depth documentation. 