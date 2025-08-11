from django import template
from news.models import NewsArticle

register = template.Library()

@register.inclusion_tag('news/recent_articles_widget.html')
def recent_articles(count=5):
    """Template tag to display recent articles anywhere."""
    articles = NewsArticle.objects.live().order_by('-publication_date')[:count]
    return {'articles': articles}

@register.filter
def truncate_words(value, arg):
    """Truncate text to specified number of words."""
    try:
        length = int(arg)
    except ValueError:
        return value
    
    words = value.split()
    if len(words) <= length:
        return value
    
    return ' '.join(words[:length]) + '...'

@register.simple_tag
def source_count():
    """Return count of articles by source."""
    return NewsArticle.objects.values('source_name').distinct().count()