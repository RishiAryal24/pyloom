# admin_dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.apps import apps
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import csv
import json
from datetime import datetime, timedelta
from django.utils import timezone

from core.admin import AboutUsAdmin

from .decorators import admin_required, superuser_required
from core.models import *
from core.forms import (
    AboutUsForm,
    GalleryItemImageForm,
    ProjectForm,
    SiteSettingsForm,
    SolutionForm,
    BlogPostForm,
    EventForm,
    GalleryItemForm,
    CustomUserCreationForm,
    ArticleForm,
    TeamMemberForm,
    
)

# Content type mappings used throughout the admin dashboard
CONTENT_MODEL_MAPPING = {
    'inquiries': ContactInquiry,
    'feedback': Feedback,
    'blog': BlogPost,
    'articles': Article,
    'events': Event,
    'gallery': GalleryItem,
    'solutions': Solution,
    'services': Solution,
    'trainings': Event,
    'users': CustomUser,
    'team': TeamMember,
    'projects': Project,
    'about': AboutUs,
    'site_settings': SiteSettings,
}

CONTENT_FORM_MAPPING = {
    'solutions': SolutionForm,
    'services': SolutionForm,
    'blog': BlogPostForm,
    'users': CustomUserCreationForm,
    'events': EventForm,
    'trainings': EventForm,
    'gallery': GalleryItemForm,
    'articles': ArticleForm,
    'team': TeamMemberForm,
    'projects': ProjectForm,
    'about': AboutUsForm,
    'site_settings': SiteSettingsForm,
}

DISPLAY_NAMES = {
    'inquiries': 'Contact Inquiries',
    'feedback': 'Feedback',
    'blog': 'Blog Posts',
    'articles': 'Articles',
    'events': 'Events',
    'gallery': 'Gallery',
    'solutions': 'Solutions',
    'services': 'Services',
    'trainings': 'Trainings',
    'users': 'Users',
    'team': 'Team Members',
    'projects': 'Projects',
    'about': 'About Us',
    'site_settings': 'Site Settings',
    'newsletter': 'Newsletter Subscribers',
}

SINGULAR_DISPLAY_NAMES = {
    'inquiries': 'Contact Inquiry',
    'feedback': 'Feedback',
    'blog': 'Blog Post',
    'articles': 'Article',
    'events': 'Event',
    'gallery': 'Gallery Item',
    'solutions': 'Solution',
    'services': 'Service',
    'trainings': 'Training',
    'users': 'User',
    'team': 'Team Member',
    'projects': 'Project',
    'about': 'About Us',
    'site_settings': 'Site Setting',
    'newsletter': 'Newsletter Subscriber',
}


def admin_login(request):
    if request.user.is_authenticated and (request.user.has_admin_access() or request.user.is_superuser):
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and (user.has_admin_access() or user.is_superuser):
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            ActivityLog.objects.create(
                user=user,
                action='view',
                content_type='Admin Dashboard',
                object_id=1,
                object_repr='Admin Login',
                ip_address=get_client_ip(request)
            )
            
            next_url = request.GET.get('next', 'admin_dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    
    return render(request, 'admin/login.html')

def admin_logout(request):
    """Admin logout view"""
    if request.user.is_authenticated:
        ActivityLog.objects.create(
            user=request.user,
            action='view',
            content_type='Admin Dashboard',
            object_id=1,
            object_repr='Admin Logout',
            ip_address=request.META.get('REMOTE_ADDR')
        )
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('admin_login')

@admin_required
def admin_dashboard(request):
    """Main admin dashboard view"""
    # Get dashboard statistics
    stats = {
        'total_inquiries': ContactInquiry.objects.count(),
        'unread_inquiries': ContactInquiry.objects.filter(is_read=False).count(),
        'total_feedback': Feedback.objects.count(),
        'pending_feedback': Feedback.objects.filter(is_approved=False).count(),
        'total_blog_posts': BlogPost.objects.count(),
        'draft_posts': BlogPost.objects.filter(status='draft').count(),
        'total_events': Event.objects.count(),
        'upcoming_events': Event.objects.filter(status='upcoming').count(),
        'newsletter_subscribers': Newsletter.objects.filter(is_active=True).count(),
        'total_users': CustomUser.objects.count(),
    }
    
    # Recent activities
    recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:10]
    
    # Recent inquiries
    recent_inquiries = ContactInquiry.objects.order_by('-created_at')[:5]
    
    # Upcoming events
    upcoming_events = Event.objects.filter(
        status='upcoming',
        date__gte=timezone.now().date()
    ).order_by('date')[:5]
    
    # Monthly statistics for charts
    current_month = timezone.now().replace(day=1)
    months_data = []
    user_growth = []
    event_growth = []
    
    for i in range(6):
        month_start = current_month - timedelta(days=30 * i)
        month_end = month_start + timedelta(days=30)
        
        month_stats = {
            'month': month_start.strftime('%b %Y'),
            'inquiries': ContactInquiry.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count(),
            'feedback': Feedback.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count(),
            'user_growth': CustomUser.objects.filter(
                date_joined__gte=month_start,
                date_joined__lt=month_end
            ).count(),
            'event_growth': Event.objects.filter(
                date__gte=month_start,
                date__lt=month_end
            ).count(),
        }
        
        months_data.append(month_stats)
    
    months_data.reverse()
    
    # User growth graph data
    for month_data in months_data:
        user_growth.append(month_data['user_growth'])
        event_growth.append(month_data['event_growth'])
    
    context = {
        'stats': stats,
        'recent_activities': recent_activities,
        'recent_inquiries': recent_inquiries,
        'upcoming_events': upcoming_events,
        'months_data': months_data,
        'user_growth': user_growth,
        'event_growth': event_growth,
    }
    
    return render(request, 'admin/dashboard.html', context)

@admin_required
def content_list(request, content_type):
    """Generic content listing view"""
    content_type = content_type.lower() 
    model_mapping = {**CONTENT_MODEL_MAPPING, 'newsletter': Newsletter}

    if content_type not in model_mapping:
        raise Http404("Content type not found")

    model = model_mapping[content_type]

    # Get search query
    search_query = request.GET.get('search', '')

    # Build queryset
    queryset = model.objects.all()

    if content_type == 'feedback':
        # Show all feedback, regardless of approval status
        queryset = queryset.all()

    if search_query:
        if content_type in ['projects', 'solutions', 'services']:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            )
        elif content_type in ['events', 'trainings']:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            )
        elif content_type in ['articles', 'blog']:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(content__icontains=search_query) | Q(excerpt__icontains=search_query)
            )
        elif content_type == 'users':
            queryset = queryset.filter(
                Q(username__icontains=search_query) | Q(email__icontains=search_query) | Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)
            )
        else:
            queryset = queryset.filter(name__icontains=search_query)

    # Order by creation date (newest first)
    if hasattr(model, 'created_at'):
        queryset = queryset.order_by('-created_at')

    # Pagination
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'content_type': content_type,
        'display_name': DISPLAY_NAMES.get(content_type, content_type.title()),
        'display_name_singular': SINGULAR_DISPLAY_NAMES.get(content_type, content_type[:-1].title()),
        'page_obj': page_obj,
        'search_query': search_query,
        'total_count': queryset.count(),
    }

    return render(request, 'admin/content_list.html', context)



  


@admin_required
def content_form(request, content_type, object_id=None):
    """
    Generic content form view for adding/editing content.
    Supports: solutions, services, trainings, blog, users, events, gallery, articles, team, projects.
    """
    # --- Mapping content types to models and forms ---
    model_mapping = CONTENT_MODEL_MAPPING
    form_mapping = CONTENT_FORM_MAPPING

    if content_type not in model_mapping:
        raise Http404(f"Content type '{content_type}' not found.")

    ModelClass = model_mapping[content_type]
    FormClass = form_mapping.get(content_type)
    instance = get_object_or_404(ModelClass, id=object_id) if object_id else None

    # --- Special handling for Gallery ---
    if content_type == 'gallery':
        GalleryImageFormSet = inlineformset_factory(
            GalleryItem,
            GalleryItemImage,
            form=GalleryItemImageForm,
            extra=1,
            can_delete=True
        )

        if request.method == 'POST':
            form = GalleryItemForm(request.POST, instance=instance)
            formset = GalleryImageFormSet(
                request.POST, request.FILES, instance=instance,
                queryset=GalleryItemImage.objects.filter(gallery_item=instance)
            )

            if form.is_valid() and formset.is_valid():
                gallery_item = form.save(commit=False)
                if not gallery_item.uploaded_by:
                    gallery_item.uploaded_by = request.user
                gallery_item.save()
                formset.instance = gallery_item
                formset.save()
                messages.success(request, "Gallery saved successfully!")
                return redirect('content_list', content_type='gallery')
        else:
            form = GalleryItemForm(instance=instance)
            formset = GalleryImageFormSet(
                instance=instance,
                queryset=GalleryItemImage.objects.filter(gallery_item=instance)
            )

        context = {
            'content_type': content_type,
            'form': form,
            'formset': formset,
            'is_edit': bool(instance),
        }

    # --- Generic handling for all other content types ---
    else:
        if request.method == 'POST':
            form = FormClass(request.POST, request.FILES, instance=instance)
            if form.is_valid():
                obj = form.save(commit=False)
                # Auto-assign user fields
                if content_type == 'events' and not getattr(obj, 'created_by', None):
                    obj.created_by = request.user
                if content_type == 'articles' and not getattr(obj, 'author', None):
                    obj.author = request.user
                obj.save()
                action = 'updated' if instance else 'created'
                messages.success(request, f"{content_type.capitalize()} {action} successfully.")
                return redirect('content_list', content_type=content_type)
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            form = FormClass(instance=instance)

        context = {
            'content_type': content_type,
            'display_name': DISPLAY_NAMES.get(content_type, content_type.title()),
            'display_name_singular': SINGULAR_DISPLAY_NAMES.get(content_type, content_type[:-1].title()),
            'form': form,
            'is_edit': bool(instance),
        }

    return render(request, 'admin/content_form.html', context)



@admin_required
def delete_content(request, content_type, object_id):
    """Delete content object"""
    model_mapping = {
        **CONTENT_MODEL_MAPPING,
        'newsletter': Newsletter,
        'project': Project,
    }
    
    if content_type not in model_mapping:
        raise Http404("Content type not found")
    
    model = model_mapping[content_type]
    instance = get_object_or_404(model, id=object_id)
    
    if request.method == 'POST':
        # Log activity before deletion
        ActivityLog.objects.create(
            user=request.user,
            action='delete',
            content_type=content_type.capitalize(),
            object_id=instance.id,
            object_repr=str(instance),
            ip_address=get_client_ip(request)
        )
        
        instance.delete()
        messages.success(request, f'{content_type.capitalize()} deleted successfully.')
        return redirect('content_list', content_type=content_type)
    
    return render(request, 'admin/confirm_delete.html', {
        'content_type': content_type,
        'instance': instance
    })

@admin_required
def export_csv(request, content_type):
    """Export content to CSV"""
    model_mapping = {**CONTENT_MODEL_MAPPING, 'newsletter': Newsletter}
    
    if content_type not in model_mapping:
        raise Http404("Content type not found")
    
    model = model_mapping[content_type]
    queryset = model.objects.all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{content_type}_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    # Write headers based on model fields
    fields = [field.name for field in model._meta.fields if not field.name.endswith('_ptr')]
    writer.writerow(fields)
    
    # Write data
    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field)
            if callable(value):
                value = value()
            row.append(str(value) if value is not None else '')
        writer.writerow(row)
    
    # Log activity
    ActivityLog.objects.create(
        user=request.user,
        action='view',
        content_type='Export',
        object_id=0,
        object_repr=f'CSV Export: {content_type}',
        ip_address=get_client_ip(request)
    )
    
    return response

@admin_required
@require_http_methods(["POST"])
def toggle_approval(request):
    """Toggle approval status for feedback"""
    try:
        data = json.loads(request.body)
        feedback_id = data.get('id')
        
        feedback = get_object_or_404(Feedback, id=feedback_id)
        feedback.is_approved = not feedback.is_approved
        
        feedback.save()
        
        return JsonResponse({
            'success': True,
            'is_approved': feedback.is_approved
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@admin_required
@require_http_methods(["POST"])
def mark_as_read(request):
    """Mark inquiry as read"""
    try:
        data = json.loads(request.body)
        inquiry_id = data.get('id')
        
        inquiry = get_object_or_404(ContactInquiry, id=inquiry_id)
        inquiry.is_read = True
        inquiry.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@admin_required
def change_password(request):
    """Change admin password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'admin/change_password.html', {'form': form})

def password_reset_request(request):
    """Password reset request view"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                if user.has_admin_access():
                    # Generate token
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    
                    # Create reset URL
                    reset_url = request.build_absolute_uri(
                        reverse('admin_password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                    )
                    
                    # Send email
                    subject = 'PyLoom Admin Password Reset'
                    message = render_to_string('admin/password_reset_email.html', {
                        'user': user,
                        'reset_url': reset_url,
                        'site_name': 'PyLoom Admin'
                    })
                    
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                    messages.success(request, 'Password reset email has been sent.')
                    return redirect('admin_login')
                else:
                    messages.error(request, 'This email is not associated with an admin account.')
            except CustomUser.DoesNotExist:
                messages.error(request, 'No admin account found with this email address.')
    else:
        form = PasswordResetForm()
    
    return render(request, 'admin/password_reset.html', {'form': form})

def password_reset_confirm(request, uidb64, token):
    """Password reset confirmation view"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully. You can now log in.')
                return redirect('admin_login')
        else:
            form = SetPasswordForm(user)
        
        return render(request, 'admin/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('admin_login')

@admin_required
def bulk_action(request):
    """Handle bulk actions on content"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            content_type = data.get('content_type')
            object_ids = data.get('object_ids', [])
            
            model_mapping = {**CONTENT_MODEL_MAPPING, 'newsletter': Newsletter}
            
            if content_type not in model_mapping:
                return JsonResponse({'success': False, 'error': 'Invalid content type'})
            
            model = model_mapping[content_type]
            queryset = model.objects.filter(id__in=object_ids)
            
            if action == 'delete':
                count = queryset.count()
                queryset.delete()
                messages.success(request, f'{count} items deleted successfully.')
            elif action == 'approve' and content_type == 'feedback':
                queryset.update(is_approved=True)
                messages.success(request, f'{queryset.count()} feedback items approved.')
            elif action == 'mark_read' and content_type == 'inquiries':
                queryset.update(is_read=True)
                messages.success(request, f'{queryset.count()} inquiries marked as read.')
            
            # Log bulk action
            ActivityLog.objects.create(
                user=request.user,
                action='delete' if action == 'delete' else 'update',
                content_type=content_type.capitalize(),
                object_id=0,
                object_repr=f'Bulk action on {len(object_ids)} items',
                ip_address=get_client_ip(request)
            )
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@admin_required
def activity_logs(request):
    """View activity logs"""
    logs = ActivityLog.objects.select_related('user').order_by('-timestamp')
    
    # Filter by user if specified
    user_filter = request.GET.get('user')
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    
    # Filter by action if specified
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    # Filter by date range if specified
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique actions for filter
    actions = ActivityLog.objects.values_list('action', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'actions': actions,
        'user_filter': user_filter,
        'action_filter': action_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'admin/activity_logs.html', context)

# admin_dashboard/views.py

from django.shortcuts import render, redirect
from .forms import SiteSettingsForm
from core.models import SiteSettings
from django.contrib import messages

def site_settings(request):
    """Admin settings page to edit site settings"""

    # Check if the site settings already exist, otherwise create a default
    site_settings, created = SiteSettings.objects.get_or_create(id=1)  # Assuming you have a single settings object

    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, request.FILES, instance=site_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site settings updated successfully!')
            return redirect('admin_settings')  # Redirect back to the settings page
    else:
        form = SiteSettingsForm(instance=site_settings)

    context = {
        'form': form,
        'site_settings': site_settings,
    }
    return render(request, 'admin/settings.html', context)

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
