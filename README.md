# Simple FastAPI Project

## Local Run
Install dependencies
```bash
pip install uv
```
```bash
uv sync
```
Add `.env` file with the following content:
```yaml
SECRET_KEY=change-me
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret123
POSTGRES_DB=fastapi_db
DATABASE_URL=postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}
```
Add this code to `commons/constants.py`:
```python
from dotenv import load_dotenv

load_dotenv()
```
Run PostgreSQL database using Docker
```bash
compose -f 'docker-compose.yml' up -d --build 'db'
```
Run the API
```bash
cd src
uv run uvicorn app:app --reload
```

## Docker Run
Add `.env` file with the following content:
```yaml
SECRET_KEY=change-me
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret123
POSTGRES_DB=fastapi_db
DATABASE_URL=postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
```
Run docker compose
```bash
docker compose up --build
```

## API Client
Open the `bruno/Simple_FastAPI_Project` on bruno API Client and use the collection.
Download Bruno API Client: [Download Bruno API Client](https://www.usebruno.com/downloads)

## Tests

Run tests
```bash
uv run pytest
```

## API Documentation

Open the API documentation [here](src/openapi.json)
