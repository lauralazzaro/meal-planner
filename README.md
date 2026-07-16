# Meal Planner

![CI](https://github.com/lauralazzaro/meal-planner/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A personal meal planning app built to practice and demonstrate Python/FastAPI 
development skills.


## Features

- Weekly meal planning with reusable dishes
- Ingredient pool organized by category
- Shopping list management

## Tech Stack

- **Backend**: Python 3.12 + FastAPI
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy + Alembic (migrations)
- **Containerization**: Docker + Docker Compose
- **Frontend**: React + Tailwind CSS *(in progress)*

## Project Structure

Backend follows a **domain-driven structure** — each module (`ingredients/`, 
`dishes/`) contains its own `models.py`, `schemas.py`, `crud.py`, and `router.py`.

## Getting Started

### Prerequisites
- Docker + Docker Compose

### Setup

1. Clone the repository
2. Create a `.env` file in the root directory:
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=meal_planner_db
DATABASE_URL=postgresql://your_user:your_password@db:5432/meal_planner_db
UID=1000
GID=1000
3. Start the containers:
```bash
   docker compose up --build -d
```
4. Apply migrations:
```bash
   docker compose exec backend alembic upgrade head
```
5. Visit `http://localhost:8000/docs` for the interactive API documentation.

## Status

Active development — backend in progress, frontend not yet started.

## License

MIT
