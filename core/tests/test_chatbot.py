from unittest.mock import patch

from django.test import TestCase

from core.models import SiteSettings, Service, ClientPartner, Project, AboutUs, Training
from core.views import get_live_chatbot_response


class ChatbotResponseTests(TestCase):
    def setUp(self):
        SiteSettings.objects.create(
            site_name="AI-Solution",
            contact_phone="9848583779",
            contact_email="panthipratistha@gmail.com",
            address="Butwal-Janakinagar",
        )
        Service.objects.create(title="AI-Powered Learning Platform", description="Adaptive learning service.")
        Service.objects.create(title="Smart Investment Tracker", description="Finance intelligence service.")
        Training.objects.create(
            title="Machine Learning Fundamentals",
            summary="A practical introduction to core machine learning concepts.",
            duration="6 weeks",
            price="NPR 12,000",
            prerequisites="Basic Python knowledge",
        )
        Training.objects.create(
            title="Cybersecurity Essentials",
            summary="A beginner-friendly course on protecting digital systems.",
            duration="4 weeks",
            price="NPR 9,000",
        )

    def test_returns_contact_details_for_contact_queries(self):
        response = get_live_chatbot_response("How can I contact AI-Solution?")

        self.assertIn("9848583779", response)
        self.assertIn("panthipratistha@gmail.com", response)

    def test_returns_solution_examples_for_service_queries(self):
        response = get_live_chatbot_response("What services do you offer?")

        self.assertIn("AI-Powered Learning Platform", response)
        self.assertIn("Smart Investment Tracker", response)

    def test_returns_client_fallback_for_client_queries(self):
        ClientPartner.objects.create(name="Acme Corp", description="Long-term client partner.")
        ClientPartner.objects.create(name="Beta LLC", description="Client partner focused on fintech.")

        response = get_live_chatbot_response("clients of this company")

        self.assertIn("client partnerships", response)
        self.assertIn("Acme Corp", response)
        self.assertIn("Beta LLC", response)

    def test_refuses_user_access_questions(self):
        response = get_live_chatbot_response("How do I login to my account?")

        self.assertIn("user login", response)
        self.assertIn("account access", response)

    def test_named_training_answer_does_not_include_other_trainings(self):
        response = get_live_chatbot_response("Tell me about Machine Learning Fundamentals")

        self.assertIn("Machine Learning Fundamentals", response)
        self.assertIn("practical introduction", response)
        self.assertNotIn("Cybersecurity Essentials", response)

    def test_named_training_field_question_is_specific(self):
        response = get_live_chatbot_response("What is the price of Machine Learning Fundamentals?")

        self.assertIn("NPR 12,000", response)
        self.assertNotIn("Cybersecurity Essentials", response)
