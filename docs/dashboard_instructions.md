# AutoShift Dashboard Instructions

## Running the Dashboard

1. Make sure all requirements are installed and your `.env` file is set up correctly.

2. Start the application using Docker Compose:
   ```
   docker-compose up -d
   ```

3. If this is your first time running the application, you need to:
   - Apply migrations:
     ```
     docker-compose exec app python manage.py migrate
     ```
   - Create a superuser:
     ```
     docker-compose exec app python manage.py createsuperuser
     ```
   - Collect static files:
     ```
     docker-compose exec app python manage.py collectstatic --noinput
     ```

4. Visit the dashboard at http://localhost:8000/dashboard/

5. If you need test data, you can run the commands from the `dashboard_creation_guide.md` file.

## Troubleshooting

### Static Files Not Loading

If stylesheets or JavaScript files aren't loading:

1. Make sure you've collected static files:
   ```
   docker-compose exec app python manage.py collectstatic --noinput
   ```

2. Check that the STATIC_URL and STATIC_ROOT settings are correctly configured in settings.py.

3. Verify that your web server (Nginx, if used) is configured to serve static files.

### Charts Not Displaying Data

1. Check the browser's console for JavaScript errors.

2. Ensure the statistics API endpoint (`/api/shifts/statistics/`) is working correctly:
   - Visit http://localhost:8000/api/shifts/statistics/ in your browser while logged in.
   - Verify the response contains valid data.

3. Ensure your database has shift data. You can create test data as described in `dashboard_creation_guide.md`.

### Not Authorized to View Dashboard

1. Make sure you're logged in. The dashboard requires authentication.

2. If using a non-admin account, ensure the user has appropriate permissions.

### Server Errors

1. Check the logs for any error messages:
   ```
   docker-compose logs app
   ```

2. Ensure all required environment variables are set in your `.env` file.

## Making Modifications

If you want to customize the dashboard:

1. The dashboard template is located at `shifts/templates/shifts/dashboard.html`
2. The dashboard JavaScript is at `static/js/dashboard.js`
3. CSS styles are in `static/css/dashboard.css`

After making changes to static files, run the following:
```
docker-compose exec app python manage.py collectstatic --noinput
```

## Taking Screenshots

For presentation purposes, you can take screenshots as described in `dashboard_creation_guide.md`. 