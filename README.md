
# News Scraper

A professional news aggregation system built with Django and Wagtail CMS. It scrapes articles from multiple sources and displays them in a beautiful, paginated interface.

---

## 🌟 Features

- **Modern Tech Stack:** Django 4.2 + Wagtail 5.2
- **Web Scraping:** BBC Technology and Hacker News
- **Responsive Design:** Mobile-first Bootstrap 5 UI
- **Admin Interface:** Full Wagtail CMS integration
- **Search & Filter:** Built-in search and filtering
- **Pagination:** Clean Bootstrap-styled pagination
- **Logging:** Comprehensive scraping logs
- **Performance:** Optimized queries and caching
- **Error Handling:** Graceful handling of scraping failures

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Installation

1. **Clone and setup environment:**
    ```bash
    git clone <your-repo-url>
    cd news_scraper_project
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```
2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3. **Setup database:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
    ```
4. **Run the scraper:**
    ```bash
    python manage.py scrape_news
    ```
5. **Start the server:**
    ```bash
    python manage.py runserver
    ```
6. **Visit the site:**
    - Frontend: [http://localhost:8000/](http://localhost:8000/)
    - Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## 📖 Usage

### Scraping Commands

```bash
# Basic scraping (5 articles)
python manage.py scrape_news

# Scrape more articles
python manage.py scrape_news --max-articles 10

# Force update existing articles
python manage.py scrape_news --force-update

# Test run without saving
python manage.py scrape_news --dry-run
```

### Admin Features

- News Articles Management: View, edit, and manage scraped articles
- Scraping Logs: Monitor scraping performance and errors
- Page Management: Full Wagtail page management capabilities
- User Management: Django admin integration

---

## 🏗️ Architecture

### Models
- **NewsListPage:** Wagtail page for displaying article lists
- **NewsArticle:** Individual news articles with metadata
- **ScrapingLog:** Tracks scraping operations and statistics

### Scrapers 
- **HackerNewsScraper:** Scrapes Hacker News front page
- **ScraperManager:** Coordinates multiple scrapers

### Features
- Error Handling: Graceful handling of network issues and HTML changes
- Duplicate Prevention: Prevents duplicate articles by URL and title
- Data Validation: Ensures data quality and consistency
- Logging: Comprehensive logging for debugging and monitoring

---

## 🔧 Customization

### Adding New Scrapers

Create a new scraper class inheriting from `NewsScraperBase`:

```python
class YourSiteScraper(NewsScraperBase):
     def __init__(self, max_articles=5):
          super().__init__('https://yoursite.com', max_articles)
     def scrape(self):
          # Implement your scraping logic
          pass
```

Add to `ScraperManager`:

```python
self.scrapers = [
     BBCTechScraper(max_articles=3),
     HackerNewsScraper(max_articles=2),
     YourSiteScraper(max_articles=2),  # Add here
]
```

### Styling Customization

Templates use Bootstrap 5 with custom CSS variables. Modify the CSS variables in your template:

```css
:root {
     --primary-color: #your-color;
     --secondary-color: #your-color;
     --accent-color: #your-color;
}
```

---

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Check code quality
flake8 .
black .
```

---

## 🚀 Deployment

### Environment Variables

Create a `.env` file for production:

```env
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=your-database-url
```

### Production Checklist
- Set `DEBUG=False`
- Configure proper database (PostgreSQL recommended)
- Setup static file serving
- Configure logging
- Setup monitoring
- Configure cron job for scraping

---

## 📁 Project Structure

```text
news_scraper_project/
├── news/
│   ├── models.py              # News models and Wagtail pages
│   ├── scrapers.py            # Web scraping logic
│   ├── management/
│   │   └── commands/
│   │       └── scrape_news.py # Scraping management command
│   ├── templates/
│   │   └── news/              # Frontend templates
│   └── admin.py               # Admin configurations
├── news_scraper_project/
│   ├── settings.py            # Django settings
│   ├── urls.py                # URL configurations
│   └── wsgi.py                # WSGI configuration
├── requirements.txt           # Python dependencies
└── manage.py                  # Django management script
```

---

## 🎯 Key Features Implemented

- Django + Wagtail Setup: Complete integration
- NewsArticle Model: All required fields with metadata
- Web Scraping:  Hacker News scrapers
- Management Command: Full-featured `scrape_news` command
- Display in Wagtail: Responsive news list page
- Pagination: Bootstrap-styled
- Logging: Scraping statistics
- Admin Interface: Full Wagtail admin
- Error Handling: Graceful failures
- Professional Design: Modern, responsive UI

## 🎯 Extra Features Added

- Duplicate Prevention: Prevents duplicate articles
- Responsive Design: Mobile-first
- Comprehensive Logging: ScrapingLog model
- Multiple Scrapers: Extensible architecture
- Data Validation: Robust cleaning
- SEO Optimization: Meta tags & semantic HTML
- Performance: Optimized queries & pagination

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🆘 Support

For questions or support, please open an issue on GitHub.
