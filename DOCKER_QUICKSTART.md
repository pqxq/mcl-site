# Docker Quickstart

## Development (Docker Compose)

The fastest way to get a local environment running:

```bash
docker compose build --no-cache
docker compose up
```

The development server starts at `http://localhost:8000/` and reloads automatically when you edit files (the project directory is mounted as a volume).

To stop:

```bash
docker compose down
```

## Development (Docker CLI)

If you prefer not to use Compose, build and run the development image directly:

```bash
docker build -t mcl-site:dev -f Dockerfile.dev .

docker run -it \
  -p 8000:8000 \
  -e DEBUG=True \
  -e DJANGO_SETTINGS_MODULE=mcl_site.settings.dev \
  -e PYTHONUNBUFFERED=1 \
  -v "$(pwd)":/app \
  mcl-site:dev \
  bash -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
```

## Port Reference

| Service | Container port | Host port | URL |
|---|---|---|---|
| Django dev server | 8000 | 8000 | http://localhost:8000 |
| Wagtail admin | 8000 | 8000 | http://localhost:8000/admin |

## Common Tasks

### Create an admin user

```bash
# Docker Compose
docker compose exec web python manage.py createsuperuser

# Docker CLI (find CONTAINER_ID with: docker ps)
docker exec -it <CONTAINER_ID> python manage.py createsuperuser
```

### Run migrations

```bash
docker compose exec web python manage.py migrate
```

### View logs

```bash
docker compose logs -f web
```

## Environment Variables

Copy `.env.example` to `.env` and set at minimum:

```env
DEBUG=True
DJANGO_SETTINGS_MODULE=mcl_site.settings.dev
SECRET_KEY=your-secret-key-here
PYTHONUNBUFFERED=1
```

To load the file automatically in Compose, add `env_file: .env` to the `web` service in `docker-compose.yml`.

## Key Files

| File | Purpose |
|---|---|
| `Dockerfile` | Production image — Gunicorn + PostgreSQL |
| `Dockerfile.dev` | Development image — Django dev server + SQLite |
| `docker-compose.yml` | Compose configuration (runs the dev image) |
| `startup.sh` | Production entrypoint: runs migrations then starts Gunicorn |

## Troubleshooting

### Permission denied when connecting to Docker daemon

Add your user to the `docker` group, then start a new shell session:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Port 8000 already in use

Map to a different host port:

```bash
docker run -p 8080:8000 mcl-site:dev
# Visit http://localhost:8080
```

### Container won't start / stuck

```bash
docker compose down        # stop and remove containers
docker compose down -v     # also remove volumes
docker compose build --no-cache
docker compose up
```

## Production

Use the main `Dockerfile` (not `Dockerfile.dev`) for production builds. Pass all required environment variables at runtime:

```bash
docker build -t mcl-site:prod .

docker run -p 8000:8000 \
  -e DJANGO_SETTINGS_MODULE=mcl_site.settings.production \
  -e SECRET_KEY=<your-secret-key> \
  -e DATABASE_URL=postgres://user:pass@db:5432/mcl_site \
  mcl-site:prod
```

See [README.md](README.md) for the full deployment checklist.
