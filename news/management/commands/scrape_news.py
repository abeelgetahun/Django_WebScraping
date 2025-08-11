import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.dateparse import parse_date
from dateutil import parser as date_parser
from news.models import NewsArticle, NewsListPage
from wagtail.models import Site
import logging
import time
import hashlib
from urllib.parse import urljoin, urlparse
import re
import os

# Set up logging
logger = logging.getLogger('news.scraper')

class NewsScraper:
    """Professional news scraper with multiple source support."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_hacker_news(self, max_articles=5):
        """Scrape Hacker News - reliable and stable structure."""
        try:
            url = "https://news.ycombinator.com/"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Find all story rows
            story_rows = soup.find_all('tr', class_='athing')
            
            for story_row in story_rows[:max_articles]:
                try:
                    # Get title and link
                    title_cell = story_row.find('span', class_='titleline')
                    if not title_cell:
                        continue
                        
                    title_link = title_cell.find('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    link = title_link.get('href', '')
                    
                    # Handle different URL types
                    if link.startswith('item?'):
                        link = f"https://news.ycombinator.com/{link}"
                    elif not link.startswith('http'):
                        continue  # Skip invalid links
                    
                    # Create summary from title
                    summary = f"Latest story from Hacker News: {title}"
                    if len(summary) > 200:
                        summary = summary[:200] + "..."
                    
                    articles.append({
                        'title': title,
                        'summary': summary,
                        'source_url': link,
                        'source_name': 'Hacker News',
                        'publication_date': timezone.now().date(),
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to extract Hacker News article: {e}")
                    continue
                    
            return articles
            
        except Exception as e:
            logger.error(f"Failed to scrape Hacker News: {e}")
            return []
    
    def scrape_reddit_programming(self, max_articles=5):
        """Scrape Reddit Programming subreddit."""
        try:
            url = "https://old.reddit.com/r/programming.json"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for post in data['data']['children'][:max_articles]:
                try:
                    post_data = post['data']
                    
                    title = post_data.get('title', '').strip()
                    if not title:
                        continue
                    
                    # Get URL - prefer external URL over Reddit post
                    source_url = post_data.get('url', '')
                    if source_url.startswith('/r/') or 'reddit.com' in source_url:
                        source_url = f"https://reddit.com{post_data['permalink']}"
                    
                    # Create summary
                    selftext = post_data.get('selftext', '')
                    if selftext:
                        summary = selftext[:200] + "..." if len(selftext) > 200 else selftext
                    else:
                        summary = f"Programming discussion: {title}"
                        if len(summary) > 200:
                            summary = summary[:200] + "..."
                    
                    articles.append({
                        'title': title,
                        'summary': summary,
                        'source_url': source_url,
                        'source_name': 'Reddit Programming',
                        'publication_date': timezone.now().date(),
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to extract Reddit article: {e}")
                    continue
                    
            return articles
            
        except Exception as e:
            logger.error(f"Failed to scrape Reddit: {e}")
            return []

class Command(BaseCommand):
    help = 'Scrape news articles from various sources and add them to Wagtail'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--max-articles',
            type=int,
            default=5,
            help='Maximum number of articles to scrape per source (default: 5)'
        )
        parser.add_argument(
            '--source',
            choices=['hackernews', 'reddit', 'all'],
            default='all',
            help='Which news source to scrape (default: all)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be scraped without saving to database'
        )
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Update existing articles even if they haven\'t changed'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Create test articles instead of scraping'
        )
    
    def handle(self, *args, **options):
        """Main command handler."""
        self.stdout.write(
            self.style.SUCCESS("🚀 Starting news scraping...")
        )
        
        # Get options with defaults
        max_articles = options.get('max_articles', 5)
        source = options.get('source', 'all')
        dry_run = options.get('dry_run', False)
        force_update = options.get('force_update', False)
        test_mode = options.get('test', False)
        
        self.stdout.write(f"📋 Options: max_articles={max_articles}, source={source}, dry_run={dry_run}")
        
        if test_mode:
            self.stdout.write("🧪 Running in test mode...")
            return self._create_test_articles(dry_run)
        
        # Ensure we have a news list page
        if not dry_run:
            self._ensure_news_list_page()
        
        scraper = NewsScraper()
        all_articles = []
        
        # Scrape from selected sources
        if source in ['hackernews', 'all']:
            self.stdout.write("📰 Scraping Hacker News...")
            hn_articles = scraper.scrape_hacker_news(max_articles)
            all_articles.extend(hn_articles)
            self.stdout.write(f"   Found {len(hn_articles)} Hacker News articles")
        
        if source in ['reddit', 'all']:
            self.stdout.write("📰 Scraping Reddit Programming...")
            reddit_articles = scraper.scrape_reddit_programming(max_articles)
            all_articles.extend(reddit_articles)
            self.stdout.write(f"   Found {len(reddit_articles)} Reddit articles")
        
        if not all_articles:
            self.stdout.write(
                self.style.WARNING("⚠️  No articles found to process.")
            )
            return
        
        # Process articles
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for article_data in all_articles:
            if dry_run:
                self.stdout.write(f"🔍 WOULD CREATE: {article_data['title'][:60]}...")
                continue
            
            try:
                result = self._process_article(article_data, force_update)
                if result == 'created':
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Created: {article_data['title'][:60]}...")
                    )
                elif result == 'updated':
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"🔄 Updated: {article_data['title'][:60]}...")
                    )
                else:
                    skipped_count += 1
                    self.stdout.write(f"⏭️  Skipped: {article_data['title'][:60]}...")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Failed: {article_data['title'][:60]}... - {e}")
                )
                logger.error(f"Failed to process article {article_data['title']}: {e}")
        
        # Summary
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎉 Scraping complete!\n"
                    f"   Created: {created_count}\n"
                    f"   Updated: {updated_count}\n"
                    f"   Skipped: {skipped_count}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\n🔍 Dry run complete! Found {len(all_articles)} articles")
            )
    
    def _create_test_articles(self, dry_run=False):
        """Create test articles for debugging."""
        test_articles = [
            {
                'title': 'Test Article: Python Django Framework Updates',
                'summary': 'This is a test article about Django framework updates and new features for web development.',
                'source_url': 'https://example.com/django-updates',
                'source_name': 'Test Tech News',
            },
            {
                'title': 'Test Article: AI and Machine Learning Trends',
                'summary': 'A comprehensive overview of current artificial intelligence and machine learning trends in the tech industry.',
                'source_url': 'https://example.com/ai-trends',
                'source_name': 'Test AI News',
            },
            {
                'title': 'Test Article: Web Development Best Practices',
                'summary': 'Essential best practices for modern web development including security, performance, and maintainability.',
                'source_url': 'https://example.com/web-dev-practices',
                'source_name': 'Test Dev News',
            }
        ]
        
        if dry_run:
            for article in test_articles:
                self.stdout.write(f"🔍 WOULD CREATE TEST: {article['title']}")
            return
        
        self._ensure_news_list_page()
        
        created_count = 0
        for article_data in test_articles:
            try:
                result = self._process_article(article_data, False)
                if result == 'created':
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Created test article: {article_data['title']}")
                    )
                else:
                    self.stdout.write(f"⏭️  Skipped existing test article: {article_data['title']}")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Failed to create test article: {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"\n🧪 Test complete! Created {created_count} test articles")
        )
    
    def _ensure_news_list_page(self):
        """Ensure there's a news list page as the site root."""
        try:
            site = Site.objects.get(is_default_site=True)
            root_page = site.root_page
            
            # Check if news list page exists
            news_list_page = NewsListPage.objects.child_of(root_page).first()
            
            if not news_list_page:
                news_list_page = NewsListPage(
                    title="Latest News",
                    intro="Stay updated with the latest technology news from top sources.",
                    slug="news",
                    show_in_menus=True,
                )
                root_page.add_child(instance=news_list_page)
                news_list_page.save_revision().publish()
                
                self.stdout.write(
                    self.style.SUCCESS("📄 Created news list page")
                )
                logger.info("Created news list page")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to create news list page: {e}")
            )
            raise CommandError(f"Failed to create news list page: {e}")
    
    def _process_article(self, article_data, force_update=False):
        """Process a single article and save to database."""
        # Generate content hash
        content_for_hash = f"{article_data['title']}{article_data['summary']}{article_data['source_url']}"
        content_hash = hashlib.sha256(content_for_hash.encode()).hexdigest()
        
        # Check if article already exists
        try:
            existing_article = NewsArticle.objects.get(content_hash=content_hash)
            if not force_update:
                return 'skipped'
            
            # Update existing article
            existing_article.title = article_data['title']
            existing_article.summary = article_data['summary']
            existing_article.publication_date = article_data['publication_date']
            existing_article.source_name = article_data['source_name']
            existing_article.save_revision().publish()
            
            return 'updated'
            
        except NewsArticle.DoesNotExist:
            # Create new article
            news_list_page = NewsListPage.objects.first()
            if not news_list_page:
                raise CommandError("No news list page found. Please run the command again.")
            
            # Create slug from title
            slug = self._create_slug(article_data['title'])
            
            article = NewsArticle(
                title=article_data['title'],
                summary=article_data['summary'],
                source_url=article_data['source_url'],
                source_name=article_data['source_name'],
                publication_date=article_data['publication_date'],
                content_hash=content_hash,
                slug=slug,
                show_in_menus=True,
            )
            
            news_list_page.add_child(instance=article)
            article.save_revision().publish()
            
            return 'created'
    
    def _create_slug(self, title):
        """Create a URL-safe slug from the article title."""
        # Remove special characters and convert to lowercase
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
        # Replace spaces with hyphens
        slug = re.sub(r'\s+', '-', slug)
        # Remove leading/trailing hyphens and limit length
        slug = slug.strip('-')[:50]
        
        # Ensure uniqueness
        base_slug = slug
        counter = 1
        
        while NewsArticle.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug