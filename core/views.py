from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
import json
import random
from django.urls import reverse
from django.utils.html import escape
from django.core.paginator import Paginator
from .forms import ClientLoginForm, ContactForm, FeedbackForm, NewsletterForm, ArticleForm ,EventForm, GalleryItemForm, ClientSignupForm
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
import requests


def _absolute_url(request, url_name, *args, **kwargs):
    return request.build_absolute_uri(reverse(url_name, args=args, kwargs=kwargs))


def _sitemap_url(location, lastmod=None, priority='0.7', changefreq='monthly'):
    lastmod_xml = ''
    if lastmod:
        if hasattr(lastmod, 'date'):
            lastmod = lastmod.date()
        lastmod_xml = f'<lastmod>{lastmod.isoformat()}</lastmod>'
    return (
        '<url>'
        f'<loc>{escape(location)}</loc>'
        f'{lastmod_xml}'
        f'<changefreq>{changefreq}</changefreq>'
        f'<priority>{priority}</priority>'
        '</url>'
    )



def client_login(request):
    if request.method == "POST":
        form = ClientLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                # Redirect to feedback page after login
                return redirect('core:feedback')
            messages.error(request, "Invalid credentials")
    else:
        form = ClientLoginForm()
    return render(request, "frontend/client_login.html", {"form": form})


def client_signup(request):
    if request.method == "POST":
        form = ClientSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:feedback')
    else:
        form = ClientSignupForm()
    return render(request, "frontend/client_signup.html", {"form": form})

def client_logout(request):
    logout(request)
    return redirect('core:client_login')

def home(request):
    """Homepage view"""
    site_settings = SiteSettings.load() or {
        'site_name': 'Default Site Name',
        'contact_email': 'info@default.com',
        'contact_phone': '+1234567890'
    }
    
    about_us = AboutUs.objects.first() or {
        'title': 'About Us',
        'company_background': 'No company background available.',
        'mission': 'No mission statement available.',
        'vision': 'No vision statement available.',
        'values': 'No values available.'
    }
    # Get Latest 3 Solutions
    latest_solutions = Solution.objects.filter(is_active=True).order_by('-created_at')[:3]

    # Get latest 3 projects
    latest_projects = Project.objects.order_by('-completed_on')[:3]


    # Get latest 3 articles
    latest_articles = Article.objects.filter(status='published').order_by('-published_at')[:3]

    # Get all featured Feedbacks
    feedbacks = Feedback.objects.all()[:5]
    

    context = {
        'settings': site_settings,
        'about_us': about_us,
        'latest_projects': latest_projects,
        'latest_articles': latest_articles,
        'latest_solutions': latest_solutions,
        'featured_feedbacks': feedbacks,
    }

    return render(request, 'frontend/index.html', context)

def about(request):
    """About us page"""
    about_us = AboutUs.objects.first()
    team_members = TeamMember.objects.filter(is_active=True)
    
    context = {
        'about_us': about_us,
        'team_members': team_members,
        'settings': SiteSettings.load(),
    }
    
    return render(request, 'frontend/about.html', context)

def solutions(request):
    """Solutions page with filtering by category and complexity"""
    
    # Get category and complexity from query parameters
    category = request.GET.get('category', '')
    # complexity = request.GET.get('complexity', '')
    
    # Start with all active solutions
    queryset = Solution.objects.filter(is_active=True)
    
    # Filter by category if provided
    if category:
        queryset = queryset.filter(category__slug=category)
    
    # Order by 'order' field and 'title' field
    solutions_list = queryset.order_by('order', 'title')
    
    # Fetch categories and complexities for filters
    categories = Category.objects.filter(content_type='solution', is_active=True).values_list('slug', 'name')
    # complexities = Solution.COMPLEXITY_CHOICES  # Assuming this exists in your model
    
    context = {
        'solutions': solutions_list,
        'categories': categories,
        'selected_category': category,
        'settings': SiteSettings.load(),
    }
    
    return render(request, 'frontend/solutions.html', context)


def services(request):
    """Services page"""
    context = {
        'settings': SiteSettings.load(),
        'featured_solutions': Solution.objects.filter(is_active=True, is_featured=True).order_by('order', 'title')[:6],
    }
    return render(request, 'frontend/services.html', context)


def trainings(request):
    """Trainings page"""
    context = {
        'settings': SiteSettings.load(),
        'upcoming_events': Event.objects.filter(status='upcoming').order_by('date', 'time')[:6],
    }
    return render(request, 'frontend/trainings.html', context)


def solution_detail(request, solution_slug):
    """Solution detail page"""
    # Fetch the solution using its slug
    solution = get_object_or_404(Solution, slug=solution_slug, is_active=True)
    
    # Fetch related solutions based on the category
    related_solutions = Solution.objects.filter(category=solution.category, is_active=True).exclude(id=solution.id)[:3]
    
    context = {
        'solution': solution,
        'related_solutions': related_solutions,
        'settings': SiteSettings.load(),
    }
    
    return render(request, 'frontend/solution_detail.html', context)


def contact(request):
    """Contact page with form"""
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            # Use 'core:contact' if your URLs are namespaced
            return redirect('core:contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'settings': SiteSettings.load(),
    }
    
    return render(request, 'frontend/contact.html', context)

# def blog(request):
#     """Blog listing page"""
#     category = request.GET.get('category', '')
#     search = request.GET.get('search', '')
    
#     queryset = BlogPost.objects.filter(status='published')
    
#     if category:
#         queryset = queryset.filter(category=category)
    
#     if search:
#         queryset = queryset.filter(
#             Q(title__icontains=search) |
#             Q(excerpt__icontains=search) |
#             Q(content__icontains=search)
#         )
    
#     paginator = Paginator(queryset, 9)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
    
#     categories = BlogPost.CATEGORY_CHOICES
    
#     context = {
#         'page_obj': page_obj,
#         'categories': categories,
#         'selected_category': category,
#         'search_query': search,
#         'settings': SiteSettings.load(),
#     }
    
#     return render(request, 'frontend/blog.html', context)

# def blog_detail(request, slug):
#     """Blog post detail page"""
#     post = get_object_or_404(BlogPost, slug=slug, status='published')
    
#     post.views_count += 1
#     post.save(update_fields=['views_count'])
    
#     related_posts = BlogPost.objects.filter(category=post.category, status='published').exclude(id=post.id)[:3]
    
#     context = {
#         'post': post,
#         'related_posts': related_posts,
#         'settings': SiteSettings.load(),
#     }
    
#     return render(request, 'frontend/blog_detail.html', context)

def articles(request):
    """Articles page"""
    article_type = request.GET.get('type', '')
    queryset = Article.objects.all()
    
    if article_type:
        queryset = queryset.filter(article_type=article_type)
    
    paginator = Paginator(queryset, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    types = Article.ARTICLE_TYPE_CHOICES  
    
    context = {
        'page_obj': page_obj,
        'types': types,
        'selected_type': article_type,
        'settings': SiteSettings.load(),
    }
    
    return render(request, 'frontend/articles.html', context)

def add_article(request):
    """Add article page"""
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('article_list')
    else:
        form = ArticleForm()
    
    return render(request, 'add_article.html', {'form': form})

def article_list(request):
    """List all articles"""
    articles = Article.objects.filter(status='published')
    return render(request, 'frontend/article_list.html', {'articles': articles})

def article_detail(request, slug):
    """Display a single article by slug"""
    article = get_object_or_404(Article, slug=slug)
    return render(request, 'frontend/article_detail.html', {'article': article})

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Event
from .forms import EventForm
from .models import SiteSettings

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import EventForm
from .models import Event, SiteSettings



def events(request):
    """Events page with optional add-event form"""
    
    # Handle form submission
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user  # optional: track creator
            # Ensure new events default to upcoming if status is empty
            if not event.status:
                event.status = 'upcoming'
            event.save()
            messages.success(request, "Event added successfully!")
            return redirect('core:events')
    else:
        form = EventForm()

    # Filtering logic
    event_type = request.GET.get('type', '')
    status = request.GET.get('status', '')  # '' = show all

    queryset = Event.objects.all()
    if event_type:
        queryset = queryset.filter(event_type=event_type)
    if status:
        queryset = queryset.filter(status__iexact=status)

    # Order by 'promoted' first, then by date
    events_list = queryset.order_by('-is_promoted', 'date', 'time')

    # Pagination (9 per page)
    paginator = Paginator(events_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    types = Event.TYPE_CHOICES
    statuses = Event.STATUS_CHOICES

    context = {
        'events': events_list,
        'page_obj': page_obj,           # for template pagination
        'types': types,
        'statuses': statuses,
        'selected_type': event_type,
        'selected_status': status,
        'settings': SiteSettings.load(),
        'form': form,                   # for frontend add-event form
    }
    
    return render(request, 'frontend/events.html', context)




def gallery(request):
    """Gallery page with optional filtering and add-gallery form"""

    # Handle gallery item creation (optional front-end form)
    if request.method == 'POST':
        form = GalleryItemForm(request.POST, request.FILES)
        if form.is_valid():
            gallery_item = form.save(commit=False)
            gallery_item.uploaded_by = request.user
            # Optional: mark as active if you have an is_active field
            if hasattr(gallery_item, 'is_active') and gallery_item.is_active is None:
                gallery_item.is_active = True
            gallery_item.save()
            messages.success(request, "Gallery item added successfully!")
            return redirect('core:gallery')
    else:
        form = GalleryItemForm()

    event_type = request.GET.get('category', '')  # kept for existing template/query string

    queryset = GalleryItem.objects.select_related('event').prefetch_related('images')
    if event_type:
        queryset = queryset.filter(event__event_type=event_type)

    gallery_items = queryset.order_by('-is_featured', 'order', '-created_at')

    categories = Event.TYPE_CHOICES

    # Pagination (optional, 9 per page)
    paginator = Paginator(gallery_items, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'gallery_items': page_obj.object_list,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': event_type,
        'settings': SiteSettings.load(),
    }

    return render(request, 'frontend/gallery.html', context)

def event_detail(request, slug):
    """Event detail page"""
    event = get_object_or_404(Event, slug=slug)
    
    event.views_count += 1
    event.save(update_fields=['views_count'])
    
    related_events = Event.objects.filter(event_type=event.event_type).exclude(id=event.id)[:3]
    
    context = {
        'event': event,
        'related_events': related_events,
        'settings': SiteSettings.load(),
    }
    
    return render(request, 'frontend/event_detail.html', context)
# AJAX Views
@require_http_methods(["POST"])
def submit_feedback(request):
    """Submit feedback via AJAX"""
    try:
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Thank you for your feedback! We appreciate your input.'})
        return JsonResponse({'success': False, 'errors': form.errors})
    except Exception:
        return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})

@require_http_methods(["POST"])
def newsletter_signup(request):
    """Newsletter signup via AJAX"""
    try:
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Successfully subscribed to our newsletter!'})
        return JsonResponse({'success': False, 'message': 'Please enter a valid email address.'})
    except Exception:
        return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})


def robots_txt(request):
    """Search crawler instructions."""
    sitemap_url = request.build_absolute_uri(reverse('sitemap_xml'))
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /django-admin/',
        'Disallow: /login/',
        'Disallow: /signup/',
        'Disallow: /feedback/',
        'Disallow: /api/',
        f'Sitemap: {sitemap_url}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


def sitemap_xml(request):
    """XML sitemap for public marketing and content pages."""
    urls = [
        _sitemap_url(_absolute_url(request, 'core:home'), priority='1.0', changefreq='weekly'),
        _sitemap_url(_absolute_url(request, 'core:about'), priority='0.8', changefreq='monthly'),
        _sitemap_url(_absolute_url(request, 'core:solutions'), priority='0.9', changefreq='weekly'),
        _sitemap_url(_absolute_url(request, 'core:services'), priority='0.8', changefreq='monthly'),
        _sitemap_url(_absolute_url(request, 'core:trainings'), priority='0.7', changefreq='weekly'),
        _sitemap_url(_absolute_url(request, 'core:events'), priority='0.8', changefreq='weekly'),
        _sitemap_url(_absolute_url(request, 'core:articles'), priority='0.8', changefreq='weekly'),
        _sitemap_url(_absolute_url(request, 'core:gallery'), priority='0.6', changefreq='monthly'),
        _sitemap_url(_absolute_url(request, 'core:projects'), priority='0.8', changefreq='monthly'),
        _sitemap_url(_absolute_url(request, 'core:user_feedback'), priority='0.5', changefreq='monthly'),
        _sitemap_url(_absolute_url(request, 'core:contact'), priority='0.8', changefreq='monthly'),
    ]

    for solution in Solution.objects.filter(is_active=True).only('slug', 'updated_at'):
        urls.append(_sitemap_url(
            _absolute_url(request, 'core:solution_detail', solution.slug),
            solution.updated_at,
            priority='0.85',
            changefreq='monthly',
        ))

    for article in Article.objects.filter(status='published').only('slug', 'updated_at', 'published_at'):
        urls.append(_sitemap_url(
            _absolute_url(request, 'core:article_detail', article.slug),
            article.updated_at or article.published_at,
            priority='0.75',
            changefreq='monthly',
        ))

    for event in Event.objects.exclude(status='cancelled').only('slug', 'updated_at', 'date'):
        urls.append(_sitemap_url(
            _absolute_url(request, 'core:event_detail', event.slug),
            event.updated_at or event.date,
            priority='0.7',
            changefreq='monthly',
        ))

    for project in Project.objects.all().only('slug', 'completed_on'):
        urls.append(_sitemap_url(
            _absolute_url(request, 'core:project_detail', project.slug),
            project.completed_on,
            priority='0.75',
            changefreq='monthly',
        ))

    xml = '<?xml version="1.0" encoding="UTF-8"?>'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += ''.join(urls)
    xml += '</urlset>'
    return HttpResponse(xml, content_type='application/xml')
    
def chatbot(request):
    return render(request, 'frontend/chatbot.html')

def get_local_chatbot_response(message):
    message = (message or '').lower()
    responses = {
        'hello': "Hello! How can I help you today?",
        'hi': "Hi there! What would you like to know about PyLoom?",
        'services': "We offer AI-powered solutions for healthcare, finance, education, automation, and modern web systems. Which area interests you?",
        'healthcare': "Our healthcare AI solutions can support diagnostics, patient management, and predictive analytics.",
        'finance': "Our finance AI solutions can help with fraud detection, risk assessment, automation, and analytics.",
        'education': "Our education AI solutions can support personalized learning, assessment, and administrative automation.",
        'contact': "You can contact PyLoom through the contact page or email the team for a project discussion.",
        'pricing': "Pricing depends on your project scope. Please contact us for a customized quote.",
        'demo': "We can arrange a demo. Please use the contact form to schedule one.",
        'thanks': "You're welcome! Is there anything else I can help with?",
        'bye': "Thank you for visiting PyLoom. Have a great day!",
    }

    for keyword, reply in responses.items():
        if keyword in message:
            return reply

    return "I can help with PyLoom services, AI solutions, events, projects, and contact information. What would you like to know?"

@csrf_exempt
def chatbot_proxy(request):
    if request.method == "POST":
        query = request.POST.get("query")
        if not query and request.body:
            try:
                query = json.loads(request.body.decode("utf-8")).get("query")
            except (json.JSONDecodeError, UnicodeDecodeError):
                query = None
        if not query:
            return JsonResponse({"error": "No query provided"}, status=400)
        try:
            response = requests.post("http://127.0.0.1:8001/chat", json={"query": query}, timeout=5)
            response.raise_for_status()  # Raise an exception for bad status codes
            return JsonResponse(response.json())
        except requests.RequestException as e:
            return JsonResponse({
                "response": get_local_chatbot_response(query),
                "fallback": True,
            })
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def chatbot_reset(request):
    if request.method == "POST":
        try:
            requests.post("http://127.0.0.1:8001/reset", timeout=3)
        except requests.RequestException:
            pass
        return JsonResponse({"status": "chat reset"})
    return JsonResponse({"error": "Invalid request"}, status=400)

def download_article(request, article_id):
    """Download article PDF"""
    article = get_object_or_404(Article, id=article_id)

    if not hasattr(article, 'pdf_file'):
        raise Http404("Article downloads are not configured.")

    if not article.pdf_file:
        raise Http404("PDF file not found")

    article.download_count += 1
    article.save(update_fields=['download_count'])

    response = HttpResponse(article.pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{article.title}.pdf"'
    return response

@require_http_methods(["POST"])
def event_registration(request, event_id):
    """Event registration via AJAX"""
    try:
        event = get_object_or_404(Event, id=event_id)
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        company = request.POST.get('company', '')
        
        registration, created = EventRegistration.objects.get_or_create(
            event=event,
            email=email,
            defaults={'name': name, 'phone': phone, 'company': company}
        )
        
        if created:
            return JsonResponse({'success': True, 'message': 'Successfully registered for the event!'})
        return JsonResponse({'success': False, 'message': 'You are already registered for this event.'})
    except Exception:
        return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})
def add_event(request):
    """View for adding a new event."""
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user  # Set the current user as the creator
            event.save()
            messages.success(request, 'Event added successfully.')
            return redirect('event_list')  # Redirect to the event list after successful addition
    else:
        form = EventForm()

    return render(request, 'core/add_event.html', {'form': form})
def add_gallery_item(request):
    """View for adding a new gallery item."""
    if request.method == 'POST':
        form = GalleryItemForm(request.POST, request.FILES)
        if form.is_valid():
            gallery_item = form.save(commit=False)
            gallery_item.uploaded_by = request.user  # Assuming user uploads items
            gallery_item.save()
            messages.success(request, 'Gallery item added successfully.')
            return redirect('gallery_list')  # Redirect to the gallery list after successful addition
    else:
        form = GalleryItemForm()

    return render(request, 'core/add_gallery_item.html', {'form': form})
def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'project_detail.html', {'project': project})
def projects(request):
    projects = Project.objects.all()  # Or filter projects as needed
    return render(request, 'projects.html', {'projects': projects})


def user_feedback(request):
    """Display feedback list and submission form for logged-in clients"""
    # Fetch all feedbacks for display
    feedback_list = Feedback.objects.filter(is_approved=True).order_by('-created_at')

    # Paginate feedbacks (5 per page)
    paginator = Paginator(feedback_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'settings': SiteSettings.load(),  # optional site settings
    }

    return render(request, 'frontend/user_feedback.html', context)
@login_required(login_url='core:client_login')
def feedback(request):
    """Feedback submission page"""
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback_obj = form.save(commit=False)
            feedback_obj.user = request.user
            feedback_obj.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('core:feedback')
    else:
        form = FeedbackForm()
    
    return render(request, "frontend/feedback.html", {"form": form})
    


def projects(request):
    """Projects page"""
    tag = request.GET.get('tag', '')
    queryset = Project.objects.order_by('-completed_on', 'title')
    
    if tag:
        queryset = queryset.filter(tags__name__iexact=tag)
    
    paginator = Paginator(queryset, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    all_tags = Tag.objects.all()
    
    context = {
        'page_obj': page_obj,
        'all_tags': all_tags,
        'selected_tag': tag,
        'settings': SiteSettings.load(),
    }
    
    return render(request, 'frontend/projects.html', context)
def project_detail(request, slug):
    """Project detail page"""
    project = get_object_or_404(Project, slug=slug)
    
    project.views_count += 1
    project.save(update_fields=['views_count'])
    
    related_projects = Project.objects.filter(tags__in=project.tags.all()).exclude(id=project.id).distinct()[:3]
    
    context = {
        'project': project,
        'related_projects': related_projects,
        'settings': SiteSettings.load(),
    }
    
    return render(request, 'frontend/project_detail.html', context)
def password_reset_request(request):
    """Handle password reset requests"""
    if request.method == 'POST':
        email = request.POST.get('email')
        associated_users = User.objects.filter(Q(email=email))
        if associated_users.exists():
            for user in associated_users:
                subject = "Password Reset Requested"
                email_template_name = "registration/password_reset_email.txt"
                c = {
                    "email": user.email,
                    'domain': request.META['HTTP_HOST'],
                    'site_name': 'Your Site',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                }
                email = render_to_string(email_template_name, c)
                try:
                    send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Error sending email: {str(e)}'})
            return JsonResponse({'success': True, 'message': 'A password reset link has been sent to your email.'})
        else:
            return JsonResponse({'success': False, 'message': 'No user is associated with this email address.'})
    return render(request, 'registration/password_reset_form.html')
def about(request):
    """About us page"""
    about_us = AboutUs.objects.first()
    team_members = TeamMember.objects.filter(is_active=True)
    
    context = {
        'about_us': about_us,
        'team_members': team_members,
        'settings': SiteSettings.load(),
    }
    
    return render(request, 'frontend/about.html', context)

@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get('message', '').lower()

            response = get_local_chatbot_response(message)

            return JsonResponse({'success': True, 'response': response})

        except Exception as e:
            return JsonResponse({'success': False, 'response': 'Sorry, I encountered an error. Please try again.'})
