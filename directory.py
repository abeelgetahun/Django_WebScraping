import os
from pathlib import Path

def create_django_wagtail_structure(base_dir="Django_Wagtail_WebScraping"):
    # Create root directory
    root = Path(base_dir)
    root.mkdir(exist_ok=True)
    
    # Create root files
    (root / "manage.py").touch()
    (root / "requirements.txt").touch()
    (root / "README.md").touch()
    
    # Create news_scraper directory and files
    news_scraper = root / "news_scraper"
    news_scraper.mkdir(exist_ok=True)
    (news_scraper / "__init__.py").touch()
    (news_scraper / "settings.py").touch()
    (news_scraper / "urls.py").touch()
    (news_scraper / "wsgi.py").touch()
    
    # Create news app directory and files
    news = root / "news"
    news.mkdir(exist_ok=True)
    (news / "__init__.py").touch()
    (news / "admin.py").touch()
    (news / "apps.py").touch()
    (news / "models.py").touch()
    (news / "views.py").touch()
    
    # Create migrations directory
    (news / "migrations").mkdir(exist_ok=True)
    (news / "migrations" / "__init__.py").touch()
    
    # Create management/commands structure
    management = news / "management"
    management.mkdir(exist_ok=True)
    (management / "__init__.py").touch()
    
    commands = management / "commands"
    commands.mkdir(exist_ok=True)
    (commands / "__init__.py").touch()
    (commands / "scrape_news.py").touch()
    
    # Create templatetags structure
    templatetags = news / "templatetags"
    templatetags.mkdir(exist_ok=True)
    (templatetags / "__init__.py").touch()
    (templatetags / "news_tags.py").touch()

if __name__ == "__main__":
    create_django_wagtail_structure()
    print("Directory structure created successfully!")