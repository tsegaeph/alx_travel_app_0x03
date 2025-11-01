# ALX Travel App

A Django-based travel listing application with REST API support, PostgreSQL database integration, and Swagger API documentation.

## Overview
ALX Travel App allows users to view travel listings with details such as title, description, location, and price. It provides a REST API for managing listings and includes Swagger documentation for easy testing and reference.

## Features
- Create, Read, Update, and Delete (CRUD) travel listings
- REST API endpoints
- Swagger documentation available at `/swagger/`
- PostgreSQL database for data storage
- Admin interface for managing listings

## Technologies Used
- Python 3.10+
- Django 5.2
- Django REST Framework
- PostgreSQL
- drf-yasg (Swagger for API documentation)
- django-cors-headers
- Celery & RabbitMQ (for async tasks)

## Setup Instructions

```bash
// 1.Clone the repository

git clone <your-repo-url>
cd alx_travel_app
Install dependencies

pip install -r requirements.txt


// 2.Create a .env file in the project root

DEBUG=True
SECRET_KEY=<your-secret-key>
DB_NAME=alxtravel
DB_USER=postgres
DB_PASSWORD=<your-db-password>
DB_HOST=127.0.0.1
DB_PORT=5432


// 3.Apply migrations

python manage.py makemigrations
python manage.py migrate


// 4.Create a superuser

python manage.py createsuperuser


// 5.Run the development server

python manage.py runserver
