from django import forms
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML
from .models import *  # Assuming all models are imported 
from tinymce.models import HTMLField  # or your HTMLField import
from tinymce.widgets import TinyMCE  # or your TinyMCE widget import
from django.contrib.auth import get_user_model 
from django.forms import ModelForm, inlineformset_factory, modelformset_factory

User = get_user_model()

class ClientSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Set username same as email
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class ClientLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

# Contact Form
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'phone', 'company', 'country', 'job_title', 'message', 'attachment']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@company.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Company Name'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'job_title': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Tell us about your project and how we can help...'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.txt'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-6 mb-0'),
                Column('company', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('country', css_class='form-group col-md-6 mb-0'),
                Column('job_title', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'message',
            'attachment',
            HTML('<small class="form-text text-muted">Supported formats: PDF, DOC, DOCX, TXT (Max 10MB)</small>'),
            Submit('submit', 'Send Message', css_class='btn btn-primary btn-lg w-100 mt-3')
        )

# Custom User Creation Form
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role']  # Add fields as needed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

# Feedback Form
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['solution', 'company', 'rating', 'comment']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company (optional)'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'solution',
            'company',
            'rating',
            'comment',
            Submit('submit', 'Submit Feedback', css_class='btn btn-primary w-100 mt-3')
        )
# Newsletter Form
class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['email', 'name']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name (Optional)'}),
        }

# Solution Form
class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = [
            'title',
            'description',
            'detailed_content',
            'category',
            'icon',
            'features',
            'benefits',
            'use_cases',
            'faqs',
            'demo_url',  # Added this field
            'image',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Solution Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Short description'}),
            'detailed_content': TinyMCE(attrs={'cols': 80, 'rows': 10}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bootstrap icon name'}),
            'features': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter features as JSON list'}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter benefits as JSON list'}),
            'use_cases': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter use cases as JSON list'}),
            'faqs': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter FAQs as JSON list of dicts'}),
            'demo_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Demo URL'}),  # Widget for demo_url
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(content_type='solution', is_active=True)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'title',
            'description',
            'detailed_content',
            'category',
            'icon',
            'features',
            'benefits',
            'use_cases',
            'faqs',
            'demo_url',  # Ensure demo_url is in the layout
            'image',
            Submit('submit', 'Save Solution', css_class='btn btn-primary')
        )

# BlogPost Form
class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'category', 'status', 'excerpt', 'featured_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Blog Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Blog Content'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Short excerpt for the blog'}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(content_type='blog', is_active=True)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'content',
            'category',
            'status',
            'excerpt',
            'featured_image',
            Submit('submit', 'Save Blog Post', css_class='btn btn-primary')
        )

# Article Form
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'excerpt', 'category', 'status', 'featured_image', 'author', 'is_featured', 'download_count']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Article Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Article Content'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Article Excerpt'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'download_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'content',
            'excerpt',
            'category',
            'status',
            'featured_image',
            'download_count',
            'is_featured',
            Submit('submit', 'Save Article', css_class='btn btn-primary')
        )

# Custom User Creation Form (Updated)
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

# Event Form
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'date', 'time', 'location',
            'capacity', 'price', 'featured_image', 'speakers', 'agenda',
            'status', 'is_featured', 'registration_url', 'is_promoted'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'price': forms.TextInput(attrs={'class': 'form-control'}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'speakers': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Optional: List of speakers'}),
            'agenda': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Optional: List of agenda items'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(),
            'is_promoted': forms.CheckboxInput(),
            'registration_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def clean_speakers(self):
        return self.cleaned_data.get('speakers', '')

    def clean_agenda(self):
        return self.cleaned_data.get('agenda', '')

class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = [
            'title', 'summary', 'course_overview', 'duration', 'who_can_attend',
            'prerequisites', 'location', 'date', 'time', 'price', 'featured_image',
            'registration_url', 'status', 'is_featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'course_overview': TinyMCE(attrs={'cols': 80, 'rows': 10}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g. 2 days, 6 weeks'}),
            'who_can_attend': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Who should attend?'}),
            'prerequisites': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Prerequisites or prior knowledge'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'price': forms.TextInput(attrs={'class': 'form-control'}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'registration_url': forms.URLInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(),
        }

# Gallery Form
class GalleryItemForm(forms.ModelForm):
    class Meta:
        model = GalleryItem
        fields = ['event', 'is_featured']
        # now valid
        widgets = {
            'event': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(),
            
        }

class GalleryItemImageForm(forms.ModelForm):
    class Meta:
        model = GalleryItemImage
        fields = ['image']

GalleryImageFormSet = inlineformset_factory(
    GalleryItem,
    GalleryItemImage,
    form=GalleryItemImageForm,
    extra=1,
    can_delete=True
)

# Article Form
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'title', 
            'category', 
            'article_type', 
            'author',
            'content', 
            'excerpt', 
            'featured_image', 
            'status', 
            'is_featured',
            'published_at',  # optional, if you want to allow setting publish date
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Article Title'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category'}),
            'article_type': forms.Select(attrs={'class': 'form-select'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author Name'}),
            'content': TinyMCE(attrs={'cols': 80, 'rows': 10}),  # Rich text editor
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Short summary'}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'published_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            'title',
            'category',
            'article_type',
            'author',
            'content',
            'excerpt',
            'featured_image',
            'status',
            'is_featured',
            'published_at',
            Submit('submit', 'Save Article', css_class='btn btn-primary')
        )

# Project Form
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'summary', 'description', 'cover_image', 'tags', 'completed_on', 'slug']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'completed_on': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }
class AboutUsForm(forms.ModelForm):
    class Meta:
        model = AboutUs
        fields = [
            'title',
            'company_background',
            'mission',
            'vision',
            'values',
            'founded_year',
            'employees_count',
            'clients_count',
            'countries_count',
            'success_rate',
        ]
class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = [
            'name',
            'role',
            'bio',
            'photo',
            'linkedin_url',
            'twitter_url',
            'facebook_url',
            'instagram_url',
        ]
class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ['site_name', 'slogan', 'logo', 'favicon', 'contact_email', 'contact_phone', 'address', 
                  'facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url', 'youtube_url', 'maintenance_mode']
        widgets = {
            'site_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Site Name'}),
            'slogan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Site Slogan'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'favicon': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Contact Email'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Phone'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Facebook URL'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Twitter URL'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'LinkedIn URL'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Instagram URL'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'YouTube URL'}),
        }
