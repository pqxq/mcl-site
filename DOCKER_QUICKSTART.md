# Running MCL Site with Docker

## Option 1: Quick Start (Recommended for Development)

### With `docker-compose.yml` (already created):

```bash
# Navigate to project root
cd /home/cvt/Prog/mcl-site

# Build and run with Docker Compose
sudo docker compose build --no-cache
sudo docker compose up
```

**Expected output:**
```
web_1  | Watching for file changes with StatReloader
web_1  | Starting development server at http://0.0.0.0:8000/
```

Then visit: `http://localhost:8000/`

---

## Option 2: Using Docker CLI Directly

```bash
cd /home/cvt/Prog/mcl-site

# Build the image using the production Dockerfile
sudo docker build -t mcl-site:dev -f Dockerfile.dev .

# Run the container
sudo docker run -it \
  -p 8000:8000 \
  -e DEBUG=True \
  -e DJANGO_SETTINGS_MODULE=mcl_site.settings.dev \
  -e PYTHONUNBUFFERED=1 \
  -v $(pwd):/app \
  mcl-site:dev \
  bash -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
```

---

## Option 3: Without Docker (Already Running)

The app is already running on **http://localhost:8000/**

If you stopped it, restart with:
```bash
cd /home/cvt/Prog/mcl-site
.venv/bin/python manage.py runserver
```

---

## Port Mapping

| Service | Internal | External | URL |
|---------|----------|----------|-----|
| Django Dev Server | 8000 | 8000 | http://localhost:8000 |
| Admin Panel | 8000 | 8000 | http://localhost:8000/admin |

---

## Create Admin User in Docker

```bash
# Using docker compose
sudo docker compose exec web python manage.py createsuperuser

# Or using docker CLI (replace CONTAINER_ID)
sudo docker exec -it <CONTAINER_ID> python manage.py createsuperuser
```

---

## Key Files

- **Dockerfile** - Production image (uses gunicorn + PostgreSQL)
- **Dockerfile.dev** - Development image (uses runserver, SQLite)
- **docker-compose.yml** - Orchestration file (runs dev container)
- **startup.sh** - Azure deployment startup script

---

## Environment Variables

For `docker-compose.yml` you can add to `.env` file:

```env
DEBUG=True
DJANGO_SETTINGS_MODULE=mcl_site.settings.dev
PYTHONUNBUFFERED=1
SECRET_KEY=your-secret-key-here
```

Then reference in compose:
```yaml
env_file: .env
```

---

## Troubleshooting

### Permission Denied Error
If you get `permission denied while trying to connect to the docker API`:

```bash
# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Then retry without sudo
docker compose up
```

### Port Already in Use
If port 8000 is already in use:

```bash
# Use a different port
sudo docker run -p 8080:8000 mcl-site:dev
# Visit http://localhost:8080
```

### Container Stuck
```bash
# Stop all containers
docker compose down

# Remove volumes
docker compose down -v

# Rebuild
docker compose build --no-cache
```

---

## Development Workflow

1. **Start container**
   ```bash
   sudo docker compose up
   ```

2. **Edit code** - Changes auto-reload (mounted volume)

3. **Create superuser**
   ```bash
   sudo docker compose exec web python manage.py createsuperuser
   ```

4. **Run migrations**
   ```bash
   sudo docker compose exec web python manage.py migrate
   ```

5. **Access admin**
   ```
   http://localhost:8000/admin/
   ```

6. **View logs**
   ```bash
   sudo docker compose logs -f web
   ```

7. **Stop container**
   ```bash
   sudo docker compose down
   ```

---

## Production Deployment

For Azure/production, use the main `Dockerfile`:

```bash
sudo docker build -t mcl-site:prod -f Dockerfile .
sudo docker run -p 8000:8000 \
  -e DJANGO_SETTINGS_MODULE=mcl_site.settings.production \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=postgresql://user:pass@db:5432/mcl_site \
  mcl-site:prod
```

---

## Next Steps

Choose one option above and run the commands. The app will be accessible at **http://localhost:8000/**
