# core/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import AbstractUser
from tinymce.models import HTMLField
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

# core/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from tinymce.models import HTMLField
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse

# ----------------------------
# Custom Admin User
# ----------------------------
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    phone = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def has_admin_access(self):
        return self.role in ['admin', 'editor'] or self.is_superuser
# ----------------------------
# Site Settings
# ----------------------------
class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="PyLoom")
    slogan = models.CharField(max_length=200, default="Weaving Innovation Beyond Expectations")
    logo = models.ImageField(upload_to='settings/', blank=True, null=True)
    favicon = models.ImageField(upload_to='settings/', blank=True, null=True)
    contact_email = models.EmailField(max_length=254, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    maintenance_mode = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='site_settings_updated_by')

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('There can be only one SiteSettings instance')
        return super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        return cls.objects.first()

# ----------------------------
# Feedback Model
# ----------------------------
class Feedback(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    solution = models.ForeignKey(
        'Solution',
        on_delete=models.CASCADE,
        related_name='feedbacks',
        null=True, blank=True
    )
    company = models.CharField(max_length=100, blank=True)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback from {self.user.get_full_name() or self.user.username} - {self.rating}★"

# ----------------------------
# Solution Model
# ----------------------------
class Category(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('solution', 'Solution'),
        ('blog', 'Blog'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, blank=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['content_type', 'order', 'name']
        unique_together = ('content_type', 'slug')
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Solution(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    detailed_content = HTMLField(help_text="Rich text content for solution details", blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='solutions',
        limit_choices_to={'content_type': 'solution', 'is_active': True},
    )
    icon = models.CharField(max_length=50)
    features = models.JSONField(default=list)
    benefits = models.JSONField(default=list)
    use_cases = models.JSONField(default=list)
    faqs = models.JSONField(default=list)
    image = models.ImageField(upload_to='solutions/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    slug = models.SlugField(max_length=200, blank=True)
    demo_url = models.URLField(blank=True, null=True)
    canonical_url = models.URLField(max_length=200, blank=True, default='')
    meta_description = models.TextField(blank=True, default='')
    meta_title = models.CharField(max_length=70, blank=True, default='')
    og_image = models.ImageField(upload_to='solutions/', blank=True, default='')

    class Meta:
        ordering = ['order', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

    def get_category_display(self):
        return self.category.name if self.category_id else ''

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:60]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
# Project model
class Project(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    summary = models.TextField()
    description = models.TextField()
    cover_image = models.ImageField(upload_to='projects/')
    tags = models.ManyToManyField('Tag', through='Project_tags', blank=True)  # Many-to-many relationship with through model
    completed_on = models.DateField()
    views_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

# Project_tags model (through model for many-to-many relation)
class Project_tags(models.Model):  # keep the original name
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        db_table = 'core_project_tags_intermediary'
        unique_together = ('project', 'tag')

    def __str__(self):
        return f"{self.project.title} - {self.tag.name}"

# About Us model
class AboutUs(models.Model):
    title = models.CharField(max_length=200, default="About PyLoom")
    company_background = HTMLField()  # Rich text content for company background
    mission = HTMLField()  # Rich text content for mission
    vision = HTMLField()  # Rich text content for vision
    values = HTMLField(blank=True)  # Optional
    founded_year = models.PositiveIntegerField(default=2019)
    employees_count = models.PositiveIntegerField(default=50)
    clients_count = models.PositiveIntegerField(default=500)
    countries_count = models.PositiveIntegerField(default=25)
    success_rate = models.PositiveIntegerField(default=98, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = "About Us"
        verbose_name_plural = "About Us"
    
    def __str__(self):
        return self.title
    

# Article model
from django.utils.text import slugify

class Article(models.Model):
    ARTICLE_TYPE_CHOICES = [
        ('industry_report', 'Industry Report'),
        ('research_paper', 'Research Paper'),
        ('white_paper', 'White Paper'),
        ('technical_paper', 'Technical Paper'),
        ('market_analysis', 'Market Analysis'),
        ('framework_guide', 'Framework Guide'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=200)
    content = HTMLField()  # Rich text content
    excerpt = models.TextField(blank=True)  # Short summary
    category = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    article_type = models.CharField(max_length=50, choices=ARTICLE_TYPE_CHOICES, default='industry_report')
    author = models.CharField(max_length=100, blank=True)  # Can be changed to ForeignKey if needed
    featured_image = models.ImageField(upload_to='articles/', blank=True, null=True)
    published_at = models.DateTimeField(default=timezone.now, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=200, blank=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('core:article_detail', kwargs={'slug': self.slug})

    def increment_download_count(self):
        self.download_count += 1
        self.save(update_fields=['download_count'])

    def save(self, *args, **kwargs):
        # Generate slug if not set
        if not self.slug:
            self.slug = slugify(self.title)
        # Set published_at if status is published but date is missing
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        # Call the parent save method
        super(Article, self).save(*args, **kwargs)

# Event Model
class Event(models.Model):
    TYPE_CHOICES = [
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('webinar', 'Webinar'),
        ('showcase', 'Showcase'),
        ('symposium', 'Symposium'),
    ]
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = HTMLField()
    event_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField()
    price = models.CharField(max_length=50, default='Free')
    featured_image = models.ImageField(upload_to='events/', blank=True, null=True)
    speakers = models.JSONField(default=list)
    agenda = models.JSONField(default=list)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    is_featured = models.BooleanField(default=False)
    is_promoted = models.BooleanField(default=False)
    registration_url = models.URLField(blank=True)
    slug = models.SlugField(max_length=200, blank=True, unique=True)  # Ensure unique slug
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    views_count = models.PositiveIntegerField(default=0) 
    
    class Meta:
        ordering = ['date', 'time']

    def save(self, *args, **kwargs):
        # Auto-generate slug if it's empty
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # Ensure slug uniqueness
            while Event.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} - {self.date}"

class Training(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    course_overview = HTMLField(blank=True)
    learning_outcomes = HTMLField(blank=True)
    delivery_mode = models.CharField(max_length=100, blank=True)
    class_schedule = models.CharField(max_length=100, blank=True)
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    who_can_attend = models.TextField(blank=True)
    prerequisites = models.TextField(blank=True)
    certificate = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=200, blank=True)
    date = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    price = models.CharField(max_length=50, default='Free', blank=True)
    featured_image = models.ImageField(upload_to='trainings/', blank=True, null=True)
    registration_url = models.URLField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    is_featured = models.BooleanField(default=False)
    slug = models.SlugField(max_length=200, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['date', 'time']
        verbose_name = 'Training'
        verbose_name_plural = 'Trainings'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Training.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    special_requirements = models.TextField(blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=True)
    attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ['event', 'email']  # Ensure a user can only register once for an event
        ordering = ['-registration_date']

    def __str__(self):
        return f"{self.name} - {self.event.title}"

# Gallery Model
class GalleryItem(models.Model):
    CATEGORY_CHOICES = [
        ('conference', 'Conference'),
        ('product_launch', 'Product Launch'),
        ('workshop', 'Workshop'),
        ('symposium', 'Symposium'),
        ('team_event', 'Team Event'),
        ('demo', 'Demo'),
        ('tour', 'Tour'),
        ('award', 'Award'),
        ('partnership', 'Partnership'),
    ]

    event = models.ForeignKey(
        Event,  # Link to your Event model
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gallery_items'
    )
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

class GalleryItemImage(models.Model):
    gallery_item = models.ForeignKey(GalleryItem, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gallery/')

    def __str__(self):
        return f"Image for {self.gallery_item}"

# User model
class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # In practice, use Django's built-in User model for authentication
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email
# Contact Inquiry Model
class ContactInquiry(models.Model):
    COUNTRY_CHOICES = [
        ('US', 'United States'),
        ('CA', 'Canada'),
        ('UK', 'United Kingdom'),
        ('DE', 'Germany'),
        ('FR', 'France'),
        ('AU', 'Australia'),
        ('JP', 'Japan'),
        ('KR', 'South Korea'),
        ('SG', 'Singapore'),
        ('IN', 'India'),
        ('BR', 'Brazil'),
        ('MX', 'Mexico'),
        ('OTHER', 'Other'),
    ]
    
    JOB_TITLE_CHOICES = [
        ('ceo', 'CEO/President'),
        ('cto', 'CTO/VP Technology'),
        ('director', 'IT Director'),
        ('scientist', 'Data Scientist'),
        ('engineer', 'Software Engineer'),
        ('manager', 'Product Manager'),
        ('analyst', 'Business Analyst'),
        ('consultant', 'Consultant'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, blank=True)
    job_title = models.CharField(max_length=20, choices=JOB_TITLE_CHOICES, blank=True)
    message = models.TextField()
    attachment = models.FileField(upload_to='inquiries/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    is_responded = models.BooleanField(default=False)
    response_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Inquiry from {self.name} - {self.company}"
    
class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(max_length=300)
    content = HTMLField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='blog_posts',
        limit_choices_to={'content_type': 'blog', 'is_active': True},
    )
    tags = models.JSONField(default=list)
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    read_time = models.PositiveIntegerField(default=5, help_text="Estimated read time in minutes")
    views_count = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

    def get_category_display(self):
        return self.category.name if self.category_id else ''

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
#New letter model
class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email
class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('view', 'Viewed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    content_type = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField()
    object_repr = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} {self.action} {self.content_type} at {self.timestamp}"
class TeamMember(models.Model):
    ROLE_CHOICES = [
        ('founder', 'Founder'),
        ('ceo', 'CEO'),
        ('cto', 'CTO'),
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('marketer', 'Marketer'),
        ('sales', 'Sales'),
        ('hr', 'HR'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.get_role_display()}"
    
# Link clients to the main User model
    def __str__(self):
        return self.user.get_full_name() or self.user.username


