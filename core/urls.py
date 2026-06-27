from django.urls import path
from . import views

app_name = "core"  # Namespace for the core app URLs

urlpatterns = [
    # Client Authentication
    path('login/', views.client_login, name='client_login'),
    path('logout/', views.client_logout, name='client_logout'),
    path('signup/', views.client_signup, name='client_signup'),
    # Main Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('solutions/', views.solutions, name='solutions'),
    path('solutions/<slug:solution_slug>/', views.solution_detail, name='solution_detail'),
    path('services/', views.services, name='services'),
    path('trainings/', views.trainings, name='trainings'),
    path('trainings/<slug:slug>/', views.training_detail, name='training_detail'),
    path('contact/', views.contact, name='contact'),
    path('events/', views.events, name='events'),
    path('events/<slug:slug>/', views.event_detail, name='event_detail'), 
    path('user_feedback/', views.user_feedback, name='user_feedback'),
    path('feedback/', views.feedback, name='feedback'),

    # Password Reset
    path('password_reset/', views.password_reset_request, name='password_reset'),

    # Blog and Articles
    path('articles/', views.articles, name='articles'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),


    # Gallery and Projects
    path('gallery/', views.gallery, name='gallery'),
    path('projects/', views.projects, name="projects"),           
    path('projects/<slug:slug>/', views.project_detail, name="project_detail"),

    # Add new content
    path('add_article/', views.add_article, name='add_article'),
    path('add_event/', views.add_event, name='add_event'),
    path('add_gallery_item/', views.add_gallery_item, name='add_gallery_item'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('api/chat/', views.chatbot_proxy, name='chatbot_proxy'),  # New chatbot URL
    path('api/chat/reset/', views.chatbot_reset, name='chatbot_reset'),


    # AJAX endpoints
    path('api/feedback/', views.submit_feedback, name='submit_feedback'),
    path('api/newsletter/', views.newsletter_signup, name='newsletter_signup'),
        path('api/download-article/<int:article_id>/', views.download_article, name='download_article'),
    path('api/register-event/<int:event_id>/', views.event_registration, name='event_registration'),
    path('api/solutions/', views.solutions, name='get_solutions'),  # New endpoint for fetching solutions
]
