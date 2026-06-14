from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    EventViewSet, GalleryItemViewSet, SolutionViewSet,
    ProjectViewSet, ArticleViewSet, BlogPostViewSet,
    NewsletterViewSet, TeamMemberViewSet
)

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'gallery', GalleryItemViewSet, basename='gallery')
router.register(r'solutions', SolutionViewSet, basename='solution')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'blog', BlogPostViewSet, basename='blog')
router.register(r'newsletter', NewsletterViewSet, basename='newsletter')
router.register(r'team', TeamMemberViewSet, basename='team')

urlpatterns = [
    path('', include(router.urls)),
]
