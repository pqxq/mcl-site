# Mykolaiv Classical Lyceum №9 — Website

A Django/Wagtail CMS website for Mykolaiv Classical Lyceum №9 (Миколаївський ліцей №9), Ukraine. Includes a staff directory, news feed, class schedule, admissions form, and public document management.

## Features

| Feature | Description |
|---|---|
| **Content Management** | Wagtail-powered CMS with a structured page tree |
| **Staff Directory** | Teacher profiles with subjects, education, and experience |
| **News** | Date-filtered news with full-text search |
| **Class Schedule** | Weekly schedule with per-group filtering |
| **Admissions** | Online application form for prospective students |
| **Public Documents** | Managed document library with a dedicated public route |
| **Responsive Layout** | Bootstrap 5.3 mobile-first design |
| **SEO** | Built-in Wagtail SEO settings and OpenGraph support |

## Tech Stack

- **Backend**: Django 5.2, Python 3.11
- **CMS**: Wagtail 8.0
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5.3, custom CSS with CSS variables
- **Icons**: Bootstrap Icons
- **Typography**: DM Sans (headings), IBM Plex Sans (body)
- **Static files**: WhiteNoise
- **Server**: Gunicorn

## Project Structure

```
mcl_site/              # Project configuration
├── settings/
│   ├── base.py        # Shared settings
│   ├── dev.py         # Development overrides (SQLite, DEBUG=True)
│   └── production.py  # Production settings (PostgreSQL, security headers)
├── templates/         # Global templates (base.html, 404.html, 500.html)
└── static/css/style.css

admissions/            # Application form
documents/             # Public documents library
gallery/               # Photo gallery
home/                  # Home page and About page
news/                  # News index and articles
schedule/              # Class groups and weekly schedule
search/                # Site-wide search
staff/                 # Staff index and individual profiles
```

## Local Development

### Prerequisites

- Python 3.11+
- pip
- (Optional) PostgreSQL for a production-equivalent local setup

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/pqxq/mcl-site.git
   cd mcl-site
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Linux / macOS
   # venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env — at minimum set a unique SECRET_KEY
   ```

   Development defaults in `dev.py` work without a `.env` file if you just want to get running quickly.

5. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

6. **Set up the initial page tree**

   Creates the Home, News, Admissions, About, and other top-level pages:

   ```bash
   python manage.py setup_site
   ```

7. **Create an admin account**

   ```bash
   python manage.py createsuperuser
   ```

8. **Start the development server**

   ```bash
   python manage.py runserver
   ```

   The site is available at `http://localhost:8000/`. The Wagtail admin is at `/admin/`.

### Docker (alternative)

See [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) for Docker Compose and standalone container instructions.

## Configuration

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Django secret key. Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | No | Set to `False` in production |
| `DATABASE_URL` | Production | PostgreSQL connection string, e.g. `postgres://user:pass@host:5432/dbname` |
| `ALLOWED_HOSTS` | Production | Comma-separated list of allowed hostnames |
| `DJANGO_SETTINGS_MODULE` | No | Defaults to `mcl_site.settings.dev` |
| `WAGTAILADMIN_BASE_URL` | No | Full base URL used in Wagtail email links |
| `AZURE_ACCOUNT_NAME` | Optional | Azure Blob Storage account name (for media in production) |
| `AZURE_ACCOUNT_KEY` | Optional | Azure Blob Storage account key |
| `AZURE_CONTAINER` | Optional | Blob container name (default: `media`) |

### Static and Media Files

Static files live in `mcl_site/static/`. User uploads go to `media/`.

Collect static files before deploying:

```bash
python manage.py collectstatic
```

### Design Tokens

The main stylesheet is `mcl_site/static/css/style.css`. Key CSS variables:

```css
--primary:  #1e3a5f;   /* navy blue */
--accent:   #d4af37;   /* gold      */
--white:    #ffffff;
--gray-50:  #f9fafb;
```

## Content Management

Log in at `/admin/` to manage site content.

### Page Tree

After running `setup_site`, the expected Wagtail page tree is:

```
Root
└── Home
    ├── About
    ├── Admissions
    ├── Education
    ├── Schedule
    ├── News
    │   └── (News articles)
    ├── Staff
    │   └── (Staff profiles)
    ├── Partners
    └── Public Documents
        └── (Document entries)
```

### Menus

Menus are managed as Wagtail snippets: **Admin → Snippets → Menus**.

Create a `primary` and a `footer` menu, then add items linking to pages.

### SEO Settings

**Admin → Settings → SEO Settings** — set the default meta description and OpenGraph image used across pages that don't override them.

### Redirects

To bulk-import redirects from a CSV (`old_path,new_path[,is_permanent]`):

```bash
# Dry run first
python manage.py import_redirects redirects.csv --dry-run

# Apply
python manage.py import_redirects redirects.csv
```

> **Note**: Wagtail serves document downloads at `/documents/`. Use a different slug for the public documents index page (e.g., `/public-docs/`) to avoid conflicts.

## Deployment

### General checklist

- Set `DEBUG=False`
- Set a strong, unique `SECRET_KEY`
- Add your domain(s) to `ALLOWED_HOSTS`
- Point `DATABASE_URL` to a PostgreSQL instance
- Run `python manage.py collectstatic`
- Run `python manage.py migrate`

### Docker (production)

Build and run the production image:

```bash
docker build -t mcl-site:prod .
docker run -p 8000:8000 \
  -e DJANGO_SETTINGS_MODULE=mcl_site.settings.production \
  -e SECRET_KEY=<your-secret-key> \
  -e DATABASE_URL=postgres://user:pass@db:5432/mcl_site \
  mcl-site:prod
```

The production image uses Gunicorn and runs `startup.sh` on start, which applies migrations before launching the server.

### Cloud platforms (Azure, Railway, Heroku)

1. Set all required environment variables in the platform's dashboard.
2. Point your build to the `Dockerfile` (production).
3. Configure a managed PostgreSQL database and update `DATABASE_URL`.
4. For media storage on Azure, set the `AZURE_*` variables.

A `railway.toml` is included for Railway deployments.

## Development Reference

### Running Tests

```bash
python manage.py test
```

### Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Reset development database

```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Code Style

Follow PEP 8. Use 4-space indentation throughout.

## Contributing

1. Branch off `main`: `git checkout -b feature/your-feature`
2. Commit your changes: `git commit -am 'Short description'`
3. Push and open a pull request against `main`

## License

MIT — see [LICENSE](LICENSE).

## References

- [Wagtail Documentation](https://docs.wagtail.org/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
