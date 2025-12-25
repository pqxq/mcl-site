# mcl_site

A Wagtail-powered site for Миколаївський ліцей №9.
## Migration Checklist

- Content tree:
   - Create under Home: About, Admissions, Education, Schedule, News, Staff, Partners, Public Documents.
   - Add child pages: News articles under News; Staff profiles under Staff; Documents under Public Documents.
- Menus:
   - Admin → Snippets → Menus: create `primary` and `footer` menus; add items linking to pages.
- SEO settings:
   - Admin → Settings → SEO Settings: set default meta description and OpenGraph image.
- Redirects:
   - Prepare a CSV `redirects.csv` with `old_path,new_path[,is_permanent]`.
   - Import with:

      ```powershell
      D:/mcl-site/venv/Scripts/python.exe manage.py import_redirects redirects.csv --dry-run
      D:/mcl-site/venv/Scripts/python.exe manage.py import_redirects redirects.csv
      ```

- Documents route:
   - Wagtail serves files at `/documents/`. Use a different slug for the public documents index (e.g., `/public-docs/`).

## Development

```powershell
D:/mcl-site/venv/Scripts/python.exe manage.py migrate
D:/mcl-site/venv/Scripts/python.exe manage.py runserver
```

Login to Wagtail admin at `/admin/`.
# Миколаївський ліцей №9 Website

A modern Django/Wagtail CMS website for Mykolaiv Classical Lyceum #9 in Ukraine. Features dynamic content management, staff directory, news updates, admissions forms, and class scheduling.

## Features

- **Dynamic CMS** — Wagtail-powered content management
- **Responsive Design** — Mobile-first Bootstrap 5.3.0 layout
- **Staff Directory** — Teacher profiles with education, experience, and subjects
- **News Management** — Blog-style news with date filters and search
- **Class Schedule** — Interactive weekly schedule with group filtering
- **Admissions Form** — Online application form for prospective students
- **Modern UI** — Gold accent color scheme with smooth animations
- **SEO Optimized** — Built-in SEO features through Wagtail

## Tech Stack

- **Backend**: Django 5.1.x, Python 3.8+
- **CMS**: Wagtail 7.2.1
- **Database**: SQLite (development), PostgreSQL (production recommended)
- **Frontend**: Bootstrap 5.3.0, Custom CSS with CSS variables
- **Icons**: Bootstrap Icons
- **Typography**: DM Sans (headings), IBM Plex Sans (body)

## Project Structure

```
mcl_site/                  # Main project settings
├── settings/
│   ├── base.py           # Common settings
│   ├── dev.py            # Development settings
│   └── production.py     # Production settings
├── templates/            # Global templates
│   ├── base.html
│   ├── 404.html
│   └── 500.html
└── static/css/style.css  # Main stylesheet

home/                      # Home app
├── models.py             # HomePage, AboutPage, HeroImage
└── templates/home/

news/                      # News management
├── models.py             # NewsIndexPage, NewsPage
└── templates/news/

staff/                     # Staff directory
├── models.py             # StaffIndexPage, PersonPage
└── templates/staff/

schedule/                  # Class scheduling
├── models.py             # ClassGroup, Lesson
└── templates/schedule/

admissions/               # Applications
├── models.py             # ApplicationFormPage
└── templates/admissions/
```

## Installation

### Prerequisites

- Python 3.8+ (3.11+ recommended)
- pip
- Virtual Environment (recommended)
- PostgreSQL (for production deployment)

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/pqxq/mcl-site.git
   cd mcl-site
   ```

   Or download and extract the ZIP file, then navigate to the project directory.
2. **Create and activate virtual environment**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```
4. **Create environment file** (recommended for production)

   ```bash
   # Copy the example file
   cp .env.example .env
   # Edit .env with your actual settings (especially SECRET_KEY)
   ```
   
   For development, you can skip this step as default values are provided.
5. **Run migrations**

   ```bash
   python manage.py migrate
   ```
6. **Initialize site structure** (creates HomePage, News, Admissions, About pages)

   ```bash
   python manage.py setup_site
   ```
7. **Create superuser (admin)**

   ```bash
   python manage.py createsuperuser
   ```
8. **Run development server**

   ```bash
   python manage.py runserver
   ```

   Visit `http://localhost:8000/admin/` to access the Wagtail CMS admin panel.

## Configuration

### Settings Files

- **Development** (`mcl_site/settings/dev.py`): SQLite database, debug mode enabled
- **Production** (`mcl_site/settings/production.py`): PostgreSQL recommended, security settings

### Environment Variables

Create a `.env` file in the project root:

```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/mcl_site
```

### Static & Media Files

- **Static files**: `mcl_site/static/` (CSS, JS, images)
- **Media files**: `media/` (user uploads, dynamically served)

Collect static files for production:

```bash
python manage.py collectstatic
```

## Usage

### Managing Content

1. Visit `/admin/` and log in with your superuser credentials
2. Use Wagtail's intuitive interface to:
   - Add news articles
   - Manage staff profiles
   - Update schedules
   - Review applications
   - Manage pages

### Adding Pages

Pages are created through the Wagtail admin interface:

- Home page content
- About page
- Custom pages under any parent

### Customizing Design

Main styles are in `mcl_site/static/css/style.css`:

- CSS variables for colors, fonts, spacing
- Responsive breakpoints (Bootstrap 5)
- Component styles (buttons, cards, badges, etc.)

Color variables:

```css
--primary: #1e3a5f      /* Navy blue */
--accent: #d4af37       /* Gold */
--white: #ffffff
--gray-50: #f9fafb
```

## Development

### Running Tests

```bash
python manage.py test
```

### Database Migrations

```bash
# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Code Style

Follow PEP 8 conventions. Use consistent indentation (4 spaces).

## Deployment

### Heroku/Cloud Platforms

1. Set `DEBUG=False` in production settings
2. Add domain to `ALLOWED_HOSTS`
3. Use PostgreSQL database (recommended)
4. Set secure headers and SSL
5. Configure environment variables

### Docker

A `Dockerfile` is provided:

```bash
docker build -t mcl-site .
docker run -p 8000:8000 mcl-site
```

### Static Files

For production, use WhiteNoise or a CDN:

```bash
# In settings/production.py
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... other middleware
]
```

## Troubleshooting

### Database Errors

```bash
# Reset database (development only)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Missing Static Files

```bash
python manage.py collectstatic --noinput
```

### Permission Errors

Ensure your user has write permissions to `media/` and `static/` directories.

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add new feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues and questions:

- Check [Wagtail Documentation](https://docs.wagtail.org/)
- Check [Django Documentation](https://docs.djangoproject.com/)
- Open an issue on GitHub

## Team

- **CMS**: Wagtail
- **Framework**: Django
- **Design**: Bootstrap 5

---

**Last Updated**: December 2025
**Version**: 1.0.0
