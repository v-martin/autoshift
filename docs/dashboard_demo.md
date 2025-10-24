# AutoShift Dashboard Demo Guide

This guide will help you set up and demonstrate the AutoShift dashboard with test data for presentations or showcasing the system.

## Quick Start

Follow these steps to get the dashboard up and running with demo data:

1. Ensure your development environment is set up:
   ```bash
   docker-compose up -d
   ```

2. Run the test data creation command:
   ```bash
   docker-compose exec app python manage.py create_test_data --clear
   ```

3. Open the dashboard in your browser:
   ```
   http://localhost:8000/dashboard/
   ```

## Features to Showcase

### 1. Weekly Shift Distribution

The bar chart shows how shifts are distributed throughout the week. Point out:
- Busier weekdays vs. quieter weekends
- The ability to identify staffing bottlenecks
- How the visualization helps with planning

### 2. Warehouse Staff Distribution

The pie chart shows how staff are distributed across warehouses. Highlight:
- Easily identify understaffed or overstaffed warehouses
- Compare relative staffing levels between locations
- Use the data to balance workforce distribution

### 3. Shift Calendar

The weekly calendar view provides a visual representation of shift density:
- Color-coded indicators (blue for low, yellow for medium, red for high)
- Quick visual identification of busy days
- Week-at-a-glance overview of scheduling

### 4. Shift Table

The detailed table shows individual shifts. Emphasize:
- Complete listing of all shifts
- Indicator showing which shifts were created by the optimization engine
- Filtering and sorting capabilities

## Customizing the Demo

### Different Data Distributions

You can modify the test data generation script to showcase different scenarios:

1. Heavy Weekend Staffing:
   - Edit `shifts/management/commands/create_test_data.py`
   - Change the line with `num_shifts = 15 if day not in ["saturday", "sunday"] else 8` to
     `num_shifts = 5 if day not in ["saturday", "sunday"] else 20`

2. Warehouse Imbalance:
   - In the same file, modify the warehouse selection to bias toward specific warehouses
   - For example, add weighting to warehouse selection

### Showcase Optimization

To highlight the optimization capabilities:

1. Create a baseline of unoptimized shifts
2. Run the optimization API endpoint
3. Refresh the dashboard to show the improvements
4. Point out the optimized tag on shifts

## Presentation Tips

1. **Tell a Story**: Start with a problem (manual scheduling is inefficient), demonstrate the solution (AutoShift dashboard), and show the outcome (optimized schedules).

2. **Use Real-World Scenarios**: Frame the demo around realistic problems warehouse managers face.

3. **Focus on Business Value**: Emphasize time savings, efficiency improvements, and better resource allocation.

4. **Interactive Elements**: Allow the audience to suggest scenarios and show how the system would handle them.

5. **Highlight Analytics**: Show how the dashboard provides insights that would be difficult to obtain manually.

## Getting Screenshots

For presentation materials, capture these key views:

1. Full dashboard
2. Each chart individually
3. Before/after optimization comparison
4. Mobile view (use browser developer tools to simulate)

Save these screenshots to the `docs/screenshots/` directory for use in presentations and documentation. 