from django.contrib.sitemaps import Sitemap
from core.models import Article, Solution, Event, Project, Training


class ArticleSitemap(Sitemap):
    """Sitemap for blog articles"""
    changefreq = 'weekly'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return Article.objects.filter(is_published=True).order_by('-created_at')

    def lastmod(self, item):
        return item.updated_at


class SolutionSitemap(Sitemap):
    """Sitemap for solutions"""
    changefreq = 'monthly'
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Solution.objects.filter(is_published=True).order_by('-created_at')

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return f'/solutions/{item.slug}/'


class EventSitemap(Sitemap):
    """Sitemap for events"""
    changefreq = 'weekly'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return Event.objects.all().order_by('-date')

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return f'/events/{item.slug}/'


class ProjectSitemap(Sitemap):
    """Sitemap for projects"""
    changefreq = 'monthly'
    priority = 0.6
    protocol = 'https'

    def items(self):
        return Project.objects.all().order_by('-created_at')

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return f'/projects/{item.slug}/'


class TrainingSitemap(Sitemap):
    """Sitemap for training programs"""
    changefreq = 'monthly'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return Training.objects.filter(is_active=True).order_by('-created_at')

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return f'/trainings/{item.slug}/'


class StaticPageSitemap(Sitemap):
    """Sitemap for static pages"""
    changefreq = 'monthly'
    priority = 0.9
    protocol = 'https'

    def items(self):
        return [
            {'name': 'home', 'priority': 1.0},
            {'name': 'about', 'priority': 0.9},
            {'name': 'solutions', 'priority': 0.9},
            {'name': 'services', 'priority': 0.8},
            {'name': 'trainings', 'priority': 0.8},
            {'name': 'careers', 'priority': 0.7},
            {'name': 'partnerships', 'priority': 0.7},
            {'name': 'contact', 'priority': 0.8},
            {'name': 'articles', 'priority': 0.8},
            {'name': 'events', 'priority': 0.7},
            {'name': 'gallery', 'priority': 0.6},
            {'name': 'projects', 'priority': 0.7},
        ]

    def location(self, item):
        if item['name'] == 'home':
            return '/'
        return f'/{item["name"]}/'

    def priority(self, item):
        return item.get('priority', 0.5)
