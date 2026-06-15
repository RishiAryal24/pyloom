from django import forms
from core.models import Solution, BlogPost, CustomUser, Category
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from crispy_forms.bootstrap import PrependedText, AppendedText
# admin_dashboard/forms.py
from core.models import SiteSettings
# admin_dashboard/forms.py

from django import forms
from core.models import SiteSettings  # Make sure to import the SiteSettings model

class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ['site_name', 'logo', 'favicon', 'contact_email', 'contact_phone', 'address', 
                  'facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url', 'youtube_url']
        widgets = {
            'site_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Site Name'}),
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



class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ['title', 'description', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Solution Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Solution Description'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(content_type='solution', is_active=True)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'description',
            'category',
            'image',
            Submit('submit', 'Save Solution', css_class='btn btn-primary')
        )


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


class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            Submit('submit', 'Create User', css_class='btn btn-primary')
        )
