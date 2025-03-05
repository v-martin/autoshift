# AutoShift

AutoShift is a Django-based application designed to automate the process of scheduling worker shifts and managing warehouse capacity. It provides an efficient way to assign shifts to workers while ensuring that warehouse capacity constraints are met.

## Features

- **Worker Shift Management**: Automatically assign shifts to workers based on availability and constraints.
- **Warehouse Capacity Control**: Define minimum and maximum worker capacity for each day of the week.
- **User Management**: Custom user model with support for avatars, email, and phone numbers.
- **Dockerized Setup**: Easy-to-use Docker and Docker Compose configuration for local development.

## Technologies Used

- **Backend**: Django
- **Database**: PostgreSQL
- **Containerization**: Docker, Docker Compose
- **Dependency Management**: Poetry

### Prerequisites

- Docker and Docker Compose installed on your machine.
- Python 3.12 (optional for local development).
