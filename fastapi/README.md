# Install dependencies
poetry install

# Run the development server
poetry run fastapi dev app/main.py

# Or using uvicorn directly
poetry run uvicorn app.main:app --reload

# Format code
poetry run black app/ tests/

# Sort imports
poetry run isort app/ tests/

# Type checking
poetry run mypy app/

# Run tests
poetry run pytest

# Create first migration
poetry run alembic revision --autogenerate -m "Initial migration"

# Apply migrations
poetry run alembic upgrade head