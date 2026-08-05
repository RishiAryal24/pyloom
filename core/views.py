from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, JsonResponse, HttpResponse, Http404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import connection
from django.utils import timezone
import json
import random
import re
from django.urls import reverse
from django.core.paginator import Paginator
from django.utils.html import strip_tags
from .forms import ClientLoginForm, ContactForm, FeedbackForm, NewsletterForm, ArticleForm, EventForm, TrainingForm, GalleryItemForm, ClientSignupForm
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
import requests


def health_check(request):
    """Minimal deployment health check with database verification."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()

    return JsonResponse({"status": "ok"})


def favicon(request):
    """Serve the bundled favicon without rendering templates or querying models."""
    favicon_path = settings.BASE_DIR / 'core' / 'static' / 'img' / 'logo.svg'
    if favicon_path.exists():
        return FileResponse(favicon_path.open('rb'), content_type='image/svg+xml')
    return HttpResponse(status=204)



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
        form = ClientSignupForm(request.POST, request.FILES)
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
    try:
        site_settings = SiteSettings.load()
    except Exception:
        site_settings = None

    site_settings = site_settings or {
        'site_name': 'PyLoom',
        'slogan': 'Weaving Innovation Beyond Expectations',
        'contact_email': 'info@pyloomtech.com',
        'contact_phone': '',
        'logo_url': '/static/img/logo.svg',
        'favicon_url': '/static/img/logo.svg',
    }
    
    try:
        about_us = AboutUs.objects.first()
    except Exception:
        about_us = None

    about_us = about_us or {
        'title': 'About Us',
        'company_background': 'No company background available.',
        'mission': 'No mission statement available.',
        'vision': 'No vision statement available.',
        'values': 'No values available.'
    }

    try:
        latest_solutions = Solution.objects.filter(is_active=True).order_by('-created_at')[:3]
    except Exception:
        latest_solutions = []

    try:
        latest_projects = Project.objects.order_by('-completed_on')[:3]
    except Exception:
        latest_projects = []

    try:
        latest_articles = Article.objects.filter(status='published').order_by('-published_at')[:3]
    except Exception:
        latest_articles = []

    try:
        feedbacks = Feedback.objects.filter(is_approved=True).order_by('-created_at')[:5]
    except Exception:
        feedbacks = []
    

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
    clients = ClientPartner.objects.filter(is_active=True).order_by('order', 'name')
    
    context = {
        'about_us': about_us,
        'team_members': team_members,
        'clients': clients,
        'settings': SiteSettings.load(),
    }
    
    return render(request, 'frontend/about.html', context)


def careers(request):
    """Careers page"""
    return render(request, 'frontend/careers.html', {
        'settings': SiteSettings.load(),
    })


def partnerships(request):
    """Partnerships page"""
    return render(request, 'frontend/partnerships.html', {
        'settings': SiteSettings.load(),
    })

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
    active_services = Service.objects.filter(is_active=True).order_by('order', 'title')
    featured_services = active_services.filter(is_featured=True)[:6]

    context = {
        'settings': SiteSettings.load(),
        'services': active_services,
        'featured_services': featured_services,
    }
    return render(request, 'frontend/services.html', context)


def trainings(request):
    """Trainings page"""
    context = {
        'settings': SiteSettings.load(),
        'upcoming_trainings': Training.objects.filter(status='upcoming').order_by('date', 'time')[:6],
    }
    return render(request, 'frontend/trainings.html', context)


def training_detail(request, slug):
    """Training detail page"""
    training = get_object_or_404(Training, slug=slug)
    related_trainings = Training.objects.filter(status='upcoming').exclude(id=training.id)[:3]

    context = {
        'training': training,
        'related_trainings': related_trainings,
        'settings': SiteSettings.load(),
    }
    return render(request, 'frontend/training_detail.html', context)


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
            if 'featured_image' in request.FILES:
                event.featured_image = request.FILES['featured_image']
            if 'og_image' in request.FILES:
                event.og_image = request.FILES['og_image']
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
    
def chatbot(request):
    return render(request, 'frontend/chatbot.html')


def _chatbot_clean(value):
    if value is None:
        return ''
    if isinstance(value, (list, tuple)):
        return ', '.join(_chatbot_clean(item) for item in value if item)
    if isinstance(value, dict):
        parts = []
        for key, item in value.items():
            cleaned = _chatbot_clean(item)
            if cleaned:
                parts.append(f"{key}: {cleaned}")
        return ', '.join(parts)
    return re.sub(r'\s+', ' ', strip_tags(str(value))).strip()


def _chatbot_terms(query):
    return {
        term
        for term in re.findall(r'[a-zA-Z0-9]+', (query or '').lower())
        if len(term) > 2 and term not in {'what', 'tell', 'about', 'available', 'does', 'from', 'with', 'give', 'show', 'have', 'having', 'info', 'information'}
    }


def _chatbot_direct_answer(query):
    q = (query or '').lower()

    if re.search(r'\b(what does (this |the |your |our )?company do|what do you do|what is this company|about (this|the) company|company overview|who are you)\b', q):
        about = AboutUs.objects.first()
        if about and _chatbot_clean(about.company_background):
            return f"We are PyLoom. {_chatbot_clean(about.company_background)}"

        settings_obj = SiteSettings.load()
        if settings_obj and settings_obj.slogan:
            return f"We are PyLoom. {settings_obj.slogan}"
        return "We are PyLoom, and we build practical technology, AI, automation, and software solutions for organizations."

    if re.search(r'\b(ceo|chief executive officer)\b', q):
        ceo = TeamMember.objects.filter(role='ceo', is_active=True).first()
        if ceo:
            return f"The CEO is {ceo.name}. {ceo.bio or 'This information is stored in the Team Members section of the website admin.'}"
        return "Our CEO profile is not published yet. We can still help with other PyLoom information."

    if re.search(r'\b(cto|chief technology officer)\b', q):
        cto = TeamMember.objects.filter(role='cto', is_active=True).first()
        if cto:
            return f"The CTO is {cto.name}. {cto.bio or 'This information is stored in the Team Members section of the website admin.'}"
        return "Our CTO profile is not published yet. We can still help with other PyLoom information."

    if re.search(r'\b(team|leadership|founder|founders|leadership team)\b', q):
        members = TeamMember.objects.filter(is_active=True).order_by('order', 'name')[:5]
        if members:
            names = ', '.join(member.name for member in members)
            return f"Our active team members are: {names}."
        return "Our leadership team has not been published yet."

    if re.search(r'\b(data source|where does .*data|where do you get .*data|source of data|trained on)\b', q):
        return (
            "We answer from our website content: Site Settings, About Us, Team Members, Services, Solutions, Projects, Events, Trainings, Articles, and Client Partners. "
            "Our published database content is the main source for answers, not generic external sources."
        )

    if re.search(r'\b(contact|reach|email|phone|address|location)\b', q):
        settings_obj = SiteSettings.load()
        if settings_obj:
            return (
                f"You can reach us at phone {settings_obj.contact_phone or 'not set'}, "
                f"email {settings_obj.contact_email or 'not set'}, address {settings_obj.address or 'not set'}."
            )
        return "Contact information is not yet configured in Site Settings."

    if re.search(r'\b(login|sign in|signin|sign up|signup|password|account|profile|access|dashboard|user access)\b', q):
        return (
            "We can help with our services, solutions, projects, clients, and contact information. "
            "We cannot provide user login or account access details."
        )

    if re.search(r'\b(client|clients|client partner|client partners|customer|customers)\b', q):
        clients = ClientPartner.objects.filter(is_active=True).order_by('order', 'name')[:4]
        if clients:
            client_names = ', '.join(client.name for client in clients)
            return (
                f"These are the client partnerships featured on the website: {client_names}. "
                "You can explore related projects and case studies to learn more about our work."
            )
        about = AboutUs.objects.first()
        if about and about.clients_count:
            return (
                f"The website says PyLoom serves around {about.clients_count} clients. "
                "Explore the Projects section for examples of client work."
            )
        projects = Project.objects.order_by('-completed_on')[:3]
        if projects:
            titles = ', '.join(project.title for project in projects)
            return (
                f"We do not have published client partner profiles yet, but here are recent projects built for our clients: {titles}."
            )
        return (
            "We do not have client-specific entries published yet."
        )

    if re.search(r'\b(service|services|offer|offerings|solutions?)\b', q):
        services = Service.objects.filter(is_active=True).order_by('order', 'title')[:4]
        if services:
            titles = ', '.join(service.title for service in services)
            return f"Our active services include: {titles}."
        return "No active services are listed on the website yet."

    if re.search(r'\b(solution|solutions?)\b', q):
        solutions = Solution.objects.filter(is_active=True).order_by('order', 'title')[:4]
        if solutions:
            titles = ', '.join(solution.title for solution in solutions)
            return f"Our active solutions include: {titles}."
        return "No active solutions are listed on the website yet."

    return None


def _chatbot_doc(kind, title, body, extra=''):
    text = _chatbot_clean(' '.join([title or '', body or '', extra or '']))
    return {
        'kind': kind,
        'title': _chatbot_clean(title),
        'body': _chatbot_clean(body),
        'extra': _chatbot_clean(extra),
        'text': text,
    }


def _chatbot_live_documents():
    docs = []

    try:
        settings_obj = SiteSettings.load()
        if settings_obj:
            docs.append(_chatbot_doc(
                'Site information',
                settings_obj.site_name,
                settings_obj.slogan,
                f"Email: {settings_obj.contact_email}. Phone: {settings_obj.contact_phone}. Address: {settings_obj.address}",
            ))
    except Exception:
        pass

    try:
        about = AboutUs.objects.first()
        if about:
            docs.append(_chatbot_doc(
                'About PyLoom',
                about.title,
                about.company_background,
                f"Mission: {about.mission}. Vision: {about.vision}. Values: {about.values}",
            ))
    except Exception:
        pass

    try:
        for service in Service.objects.filter(is_active=True).order_by('order', 'title')[:30]:
            docs.append(_chatbot_doc('Service', service.title, service.description, service.detailed_content))
    except Exception:
        pass

    try:
        for solution in Solution.objects.filter(is_active=True).select_related('category').order_by('order', 'title')[:30]:
            docs.append(_chatbot_doc(
                'Solution',
                solution.title,
                solution.description,
                f"Category: {solution.get_category_display()}. Details: {solution.detailed_content}. Features: {solution.features}. Benefits: {solution.benefits}. Use cases: {solution.use_cases}. FAQs: {solution.faqs}",
            ))
    except Exception:
        pass

    try:
        for training in Training.objects.all().order_by('-is_featured', 'date', 'time')[:30]:
            docs.append(_chatbot_doc(
                'Training',
                training.title,
                training.summary,
                f"Status: {training.get_status_display()}. Overview: {training.course_overview}. Outcomes: {training.learning_outcomes}. Duration: {training.duration}. Schedule: {training.class_schedule}. Level: {training.level}. Location: {training.location}. Start date: {training.start_date or training.date}. Time: {training.time}. Price: {training.price}. Who can attend: {training.who_can_attend}. Prerequisites: {training.prerequisites}. Certificate: {training.certificate}",
            ))
    except Exception:
        pass

    try:
        for event in Event.objects.all().order_by('-is_promoted', 'date', 'time')[:30]:
            docs.append(_chatbot_doc(
                'Event',
                event.title,
                event.description,
                f"Type: {event.get_event_type_display()}. Status: {event.get_status_display()}. Date: {event.date}. Time: {event.time}. Location: {event.location}. Capacity: {event.capacity}. Price: {event.price}. Speakers: {event.normalized_speakers}. Agenda: {event.normalized_agenda}",
            ))
    except Exception:
        pass

    try:
        for article in Article.objects.filter(status='published').order_by('-published_at')[:30]:
            docs.append(_chatbot_doc(
                'Article',
                article.title,
                article.excerpt,
                f"Type: {article.get_article_type_display()}. Category: {article.category}. Content: {article.content}",
            ))
    except Exception:
        pass

    try:
        for project in Project.objects.all().order_by('-completed_on')[:30]:
            docs.append(_chatbot_doc(
                'Project',
                project.title,
                project.summary,
                f"Completed on: {project.completed_on}. Description: {project.description}",
            ))
    except Exception:
        pass

    try:
        for client in ClientPartner.objects.filter(is_active=True).order_by('order', 'name')[:30]:
            docs.append(_chatbot_doc(
                'Client Partner',
                client.name,
                client.description,
                f"Location: {client.location}. Website: {client.website}",
            ))
    except Exception:
        pass

    try:
        for vacancy in CareerVacancy.objects.filter(is_active=True).order_by('order', 'deadline', 'title')[:20]:
            docs.append(_chatbot_doc(
                'Career vacancy',
                vacancy.title,
                vacancy.description,
                f"Deadline: {vacancy.deadline}. Application URL: {vacancy.application_url}",
            ))
    except Exception:
        pass

    return docs


def _chatbot_score(doc, terms):
    if not terms:
        return 0
    text = doc['text'].lower()
    title = doc['title'].lower()
    kind = doc['kind'].lower()
    score = 0
    for term in terms:
        singular = term[:-1] if term.endswith('s') else term
        if term in title:
            score += 6
        elif singular and singular in title:
            score += 5
        if term in kind:
            score += 4
        elif singular and singular in kind:
            score += 4
        score += min(text.count(term), 4)
        if singular and singular != term:
            score += min(text.count(singular), 3)
    return score


def _chatbot_intent_kind(terms):
    intents = {
        'event': 'Event',
        'events': 'Event',
        'training': 'Training',
        'trainings': 'Training',
        'course': 'Training',
        'courses': 'Training',
        'service': 'Service',
        'services': 'Service',
        'solution': 'Solution',
        'solutions': 'Solution',
        'article': 'Article',
        'articles': 'Article',
        'blog': 'Article',
        'project': 'Project',
        'projects': 'Project',
        'career': 'Career vacancy',
        'careers': 'Career vacancy',
        'job': 'Career vacancy',
        'jobs': 'Career vacancy',
        'contact': 'Site information',
        'address': 'Site information',
        'email': 'Site information',
        'phone': 'Site information',
    }
    for term in terms:
        if term in intents:
            return intents[term]
    return None


def _chatbot_kind_label(kind):
    labels = {
        'Site information': 'PyLoom information',
        'About PyLoom': 'About PyLoom',
        'Service': 'service',
        'Solution': 'solution',
        'Training': 'training program',
        'Event': 'event',
        'Article': 'article',
        'Project': 'project',
        'Career vacancy': 'career opening',
    }
    return labels.get(kind, kind.lower())


def _chatbot_response_heading(intent_kind):
    headings = {
        'Site information': 'You can reach us through the following contact details:',
        'About PyLoom': 'PyLoom is focused on practical technology, AI, and automation solutions that help organizations grow with confidence.',
        'Service': 'At PyLoom, our services are designed to solve real business problems with reliable technology and intelligent automation.',
        'Solution': 'At PyLoom, our solutions combine AI, automation, data, and modern software engineering to create measurable business value.',
        'Training': 'At PyLoom, our training programs are practical, hands-on, and built to help learners apply technology with confidence.',
        'Event': 'Here are the PyLoom events and activities that match your question:',
        'Article': 'Here are PyLoom insights that match your question:',
        'Project': 'Here are PyLoom projects that match your question:',
        'Career vacancy': 'Here are the current PyLoom career opportunities that match your question:',
    }
    return headings.get(
        intent_kind,
        'At PyLoom, we can help with our services, solutions, trainings, events, projects, articles, careers, and contact details.',
    )


def _chatbot_match_line(doc):
    body = doc['body'] or doc['extra']
    if len(body) > 420:
        body = body[:417].rsplit(' ', 1)[0] + '...'

    label = _chatbot_kind_label(doc['kind'])
    title = doc['title']

    if doc['kind'] == 'Site information':
        return doc['extra'] or body
    if doc['kind'] == 'About PyLoom':
        return body
    return f"{title} — {body}" if body else f"{title} — this {label} is available through PyLoom."


def _chatbot_training_match(query, docs):
    """Return one clearly named training, without broadening to other courses."""
    query_words = _chatbot_terms(query) - {'training', 'trainings', 'course', 'courses'}
    normalized_query = ' '.join(re.findall(r'[a-z0-9]+', (query or '').lower()))
    candidates = []

    for doc in docs:
        if doc['kind'] != 'Training' or not doc['title']:
            continue

        normalized_title = ' '.join(re.findall(r'[a-z0-9]+', doc['title'].lower()))
        title_words = set(re.findall(r'[a-z0-9]+', doc['title'].lower()))
        matched_words = query_words & title_words
        exact_title = normalized_title and normalized_title in normalized_query

        # Two title words (for example, "machine learning") are enough to
        # identify a course. A one-word title needs an exact phrase match.
        if exact_title or len(matched_words) >= 2:
            score = (100 if exact_title else 0) + len(matched_words)
            candidates.append((score, doc))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    if len(candidates) > 1 and candidates[0][0] == candidates[1][0]:
        return None
    return candidates[0][1]


def _chatbot_training_response(training, query, agent_name):
    """Give a short, natural answer using only the selected training record."""
    text = (query or '').lower()
    extra = training['extra']
    fields = {
        'price': r'Price:\s*([^\.]+)',
        'duration': r'Duration:\s*([^\.]+)',
        'schedule': r'Schedule:\s*([^\.]+)',
        'level': r'Level:\s*([^\.]+)',
        'location': r'Location:\s*([^\.]+)',
        'start date': r'Start date:\s*([^\.]+)',
        'time': r'Time:\s*([^\.]+)',
        'prerequisites': r'Prerequisites:\s*([^\.]+)',
        'certificate': r'Certificate:\s*([^\.]+)',
        'who can attend': r'Who can attend:\s*([^\.]+)',
    }
    requested_field = next(
        (name for name in fields if name in text or (name == 'schedule' and 'class' in text)),
        None,
    )
    if requested_field:
        match = re.search(fields[requested_field], extra, re.IGNORECASE)
        if match and match.group(1).strip() not in {'', 'None'}:
            return (
                f"{agent_name} here — for {training['title']}, the "
                f"{requested_field} is {match.group(1).strip()}."
            )
        return f"{agent_name} here — I found {training['title']}, but its {requested_field} has not been added yet."

    summary = training['body'] or 'I found this training in the PyLoom course listings.'
    return f"{agent_name} here — {training['title']} is {summary}"


def _chatbot_requested_training_field(query):
    """Map natural ways of asking for a training detail to its stored label."""
    text = (query or '').lower()
    aliases = {
        'price': ('price', 'prices', 'cost', 'costs', 'fee', 'fees', 'how much'),
        'duration': ('duration', 'durations', 'long', 'length'),
        'schedule': ('schedule', 'schedules', 'class time', 'class times'),
        'start date': ('start date', 'start dates', 'when does', 'when do'),
        'prerequisites': ('prerequisite', 'prerequisites', 'requirement', 'requirements'),
    }
    for field, phrases in aliases.items():
        if any(phrase in text for phrase in phrases):
            return field
    return None


def _chatbot_training_field_list_response(trainings, field, agent_name):
    """List a single requested detail across trainings, without their summaries."""
    pattern = {
        'price': r'Price:\s*([^\.]+)',
        'duration': r'Duration:\s*([^\.]+)',
        'schedule': r'Schedule:\s*([^\.]+)',
        'start date': r'Start date:\s*([^\.]+)',
        'prerequisites': r'Prerequisites:\s*([^\.]+)',
    }[field]
    lines = [f"{agent_name} here — here are the {field}s currently listed for our trainings:"]
    for training in trainings:
        match = re.search(pattern, training['extra'], re.IGNORECASE)
        value = match.group(1).strip() if match and match.group(1).strip() not in {'', 'None'} else 'Not listed yet'
        lines.append(f"- {training['title']}: {value}")
    return '\n'.join(lines)


def _chatbot_contextual_query(query, chat_history, docs):
    """Resolve a follow-up against the last relevant topic in this chat session."""
    if not chat_history:
        return query

    requested_training_field = _chatbot_requested_training_field(query)
    if not requested_training_field:
        return query

    # A question such as "Can you also give me the durations?" inherits the
    # most recent training subject. If it was a named course, keep that course;
    # otherwise keep the plural training list context.
    for message in reversed(chat_history):
        if message.get('role') != 'user':
            continue
        previous_query = message.get('content', '')
        if _chatbot_intent_kind(_chatbot_terms(previous_query)) != 'Training':
            continue
        selected_training = _chatbot_training_match(previous_query, docs)
        subject = selected_training['title'] if selected_training else 'trainings'
        return f"{query} for {subject}"

    return query


def get_live_chatbot_response(query, agent_name='Ritika', chat_history=None):
    chat_history = chat_history or []
    terms = _chatbot_terms(query)
    casual = {'hello', 'hi', 'hey', 'thanks', 'thank', 'bye'}
    if terms and terms.issubset(casual):
        return f"Hi, this is {agent_name} from PyLoom. We can help with our services, solutions, trainings, events, articles, projects, careers, and contact details."

    direct_answer = _chatbot_direct_answer(query)
    if direct_answer:
        return direct_answer

    docs = _chatbot_live_documents()
    effective_query = _chatbot_contextual_query(query, chat_history, docs)
    terms = _chatbot_terms(effective_query)
    intent_kind = _chatbot_intent_kind(terms)

    # A named course is a focused request: answer from that one record only.
    # General ranking remains available for questions such as "What trainings
    # are available?"
    selected_training = _chatbot_training_match(effective_query, docs)
    if selected_training:
        return _chatbot_training_response(selected_training, effective_query, agent_name)

    requested_training_field = _chatbot_requested_training_field(effective_query)
    if intent_kind == 'Training' and requested_training_field:
        trainings = [doc for doc in docs if doc['kind'] == 'Training']
        if trainings:
            return _chatbot_training_field_list_response(trainings, requested_training_field, agent_name)

    ranked = sorted(
        (
            (
                doc,
                _chatbot_score(doc, terms) + (20 if intent_kind and doc['kind'] == intent_kind else 0),
            )
            for doc in docs
        ),
        key=lambda item: item[1],
        reverse=True,
    )
    if intent_kind:
        intent_matches = [doc for doc, score in ranked if score > 0 and doc['kind'] == intent_kind][:4]
        intent_docs_exist = any(doc['kind'] == intent_kind for doc in docs)
        if intent_matches:
            matches = intent_matches
        elif intent_docs_exist:
            matches = [doc for doc in docs if doc['kind'] == intent_kind][:4]
        else:
            matches = []
    else:
        matches = [doc for doc, score in ranked if score > 0][:4]

    if not matches:
        if intent_kind:
            return (
                f"This is {agent_name} from PyLoom. We do not have matching {_chatbot_kind_label(intent_kind)} information published yet. "
                "You can ask us about services, solutions, trainings, articles, projects, careers, or contact details."
            )
        return (
            f"This is {agent_name} from PyLoom. We do not have published information for that exact question yet. "
            "You can ask us about services, solutions, events, projects, articles, careers, or contact details."
        )

    lines = [_chatbot_response_heading(intent_kind or matches[0]['kind'])]
    for doc in matches:
        line = _chatbot_match_line(doc)
        if line:
            lines.append(f"- {line}")

    lines.append("Tell me which one you want to explore, and I will guide you further.")
    return "\n".join(lines)


def get_local_chatbot_response(message):
    message = (message or '').lower()
    responses = {
        'hello': "Hi, this is Ritika from PyLoom. How can I help you today?",
        'hi': "Hi, this is Ritika from PyLoom. What would you like to know about PyLoom?",
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
                payload = json.loads(request.body.decode("utf-8"))
                query = payload.get("query")
                agent_name = payload.get("agent_name", "Ritika")
            except (json.JSONDecodeError, UnicodeDecodeError):
                query = None
                agent_name = "Ritika"
        else:
            agent_name = request.POST.get("agent_name", "Ritika")
        if not query:
            return JsonResponse({"error": "No query provided"}, status=400)
        chat_history = request.session.get('chatbot_history', [])
        answer = get_live_chatbot_response(
            query,
            agent_name=agent_name,
            chat_history=chat_history,
        )
        chat_history.extend([
            {'role': 'user', 'content': query},
            {'role': 'assistant', 'content': answer},
        ])
        request.session['chatbot_history'] = chat_history[-16:]
        return JsonResponse({
            "response": answer,
            "source": "live_database",
        })
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def chatbot_reset(request):
    if request.method == "POST":
        request.session.pop('chatbot_history', None)
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
            if 'featured_image' in request.FILES:
                event.featured_image = request.FILES['featured_image']
            if 'og_image' in request.FILES:
                event.og_image = request.FILES['og_image']
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
    clients = ClientPartner.objects.filter(is_active=True).order_by('order', 'name')
    
    context = {
        'about_us': about_us,
        'team_members': team_members,
        'clients': clients,
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
