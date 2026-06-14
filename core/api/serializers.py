from rest_framework import serializers
from core.models import Event, GalleryItem, GalleryItemImage, Solution, Project, Article, BlogPost, Newsletter, TeamMember

class GalleryItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryItemImage
        fields = ['id', 'image']

class GalleryItemSerializer(serializers.ModelSerializer):
    images = GalleryItemImageSerializer(many=True, read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = GalleryItem
        fields = ['id', 'event', 'event_title', 'is_featured', 'images']

class EventSerializer(serializers.ModelSerializer):
    gallery_items = GalleryItemSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'event_type', 'date', 'location', 'gallery_items']

class SolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = ['id', 'name', 'description', 'image', 'link']
        
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'summary', 'image', 'link']

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'published_date']
class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'author', 'published_date']
class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ['id', 'title', 'content', 'published_date']
class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['id', 'name', 'role', 'bio', 'photo']