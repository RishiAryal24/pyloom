from rest_framework import viewsets
from core.models import Event, GalleryItem, Solution
from .serializers import EventSerializer, GalleryItemSerializer, SolutionSerializer, ProjectSerializer, ArticleSerializer, BlogPostSerializer, NewsletterSerializer, TeamMemberSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-date')
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class GalleryItemViewSet(viewsets.ModelViewSet):
    queryset = GalleryItem.objects.prefetch_related('images').all().order_by('-created_at')
    serializer_class = GalleryItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class SolutionViewSet(viewsets.ModelViewSet):
    queryset = Solution.objects.all().order_by('order')
    serializer_class = SolutionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ProjectViewSet(viewsets.ModelViewSet):
    from core.models import Project
    from .serializers import ProjectSerializer
    queryset = Project.objects.all().order_by('-id')
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ArticleViewSet(viewsets.ModelViewSet):
    from core.models import Article
    from .serializers import ArticleSerializer
    queryset = Article.objects.all().order_by('-published_at')  
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BlogPostViewSet(viewsets.ModelViewSet):
    from core.models import BlogPost
    from .serializers import BlogPostSerializer
    queryset = BlogPost.objects.all().order_by('-published_at')
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class NewsletterViewSet(viewsets.ModelViewSet):
    from core.models import Newsletter
    from .serializers import NewsletterSerializer
    queryset = Newsletter.objects.all().order_by('-subscribed_at')
    serializer_class = NewsletterSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class TeamMemberViewSet(viewsets.ModelViewSet):
    from core.models import TeamMember
    from .serializers import TeamMemberSerializer
    queryset = TeamMember.objects.all().order_by('name')
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
