from django.db import models
from django.utils import timezone
from django.urls import reverse
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
import hashlib

class NewsListPage(Page):
    """
    A page that lists all news articles with pagination and filtering.
    """
    intro = RichTextField(blank=True, help_text="Introduction text for the news section")
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        # Get all published news articles, ordered by publication date (newest first)
        all_articles = NewsArticle.objects.live().order_by('-publication_date')
        
        # Pagination
        page_num = request.GET.get('page', 1)
        paginator = Paginator(all_articles, 10)  # 10 articles per page
        
        try:
            articles = paginator.page(page_num)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)
        
        context['articles'] = articles
        context['total_articles'] = all_articles.count()
        
        return context
    
    class Meta:
        verbose_name = "News List Page"

class NewsArticle(Page):
    """
    A news article page with scraped content from external sources.
    """
    publication_date = models.DateField(
        default=timezone.now,
        help_text="The date this article was originally published"
    )
    summary = models.TextField(
        max_length=500,
        help_text="A brief summary of the article (150-200 characters recommended)"
    )
    source_url = models.URLField(
        help_text="The original URL of the article"
    )
    source_name = models.CharField(
        max_length=100,
        default="Unknown",
        help_text="Name of the news source (e.g., BBC, Reuters)"
    )
    content_hash = models.CharField(
        max_length=64,
        unique=True,
        help_text="Hash of the article content to prevent duplicates"
    )
    scraped_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this article was scraped"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this article was last updated"
    )
    
    # Search configuration
    search_fields = Page.search_fields + [
        index.SearchField('summary'),
        index.FilterField('publication_date'),
        index.FilterField('source_name'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel('publication_date'),
        FieldPanel('summary'),
        FieldPanel('source_url'),
        FieldPanel('source_name'),
    ]
    
    def save(self, *args, **kwargs):
        """Generate content hash before saving to prevent duplicates."""
        if not self.content_hash:
            content_for_hash = f"{self.title}{self.summary}{self.source_url}"
            self.content_hash = hashlib.sha256(content_for_hash.encode()).hexdigest()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Return the canonical URL for this article."""
        return self.url
    
    @property
    def short_summary(self):
        """Return a truncated version of the summary."""
        if len(self.summary) > 150:
            return self.summary[:150] + "..."
        return self.summary
    
    class Meta:
        verbose_name = "News Article"
        ordering = ['-publication_date', '-scraped_at']
        
    def __str__(self):
        return f"{self.title} ({self.source_name})"