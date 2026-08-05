from unittest.mock import patch

from django.test import TestCase

from core.models import AboutUs, Category, ClientPartner, Project, Service, SiteSettings, Solution, Training
from core.views import get_live_chatbot_response


class ChatbotResponseTests(TestCase):
    def setUp(self):
        SiteSettings.objects.create(
            site_name="AI-Solution",
            contact_phone="9848583779",
            contact_email="panthipratistha@gmail.com",
            address="Butwal-Janakinagar",
        )
        AboutUs.objects.create(
            company_background="We create AI, automation, and custom software solutions for growing organizations.",
            mission="Make technology practical.",
            vision="Build a more capable digital future.",
        )
        Service.objects.create(title="AI-Powered Learning Platform", description="Adaptive learning service.")
        Service.objects.create(title="Smart Investment Tracker", description="Finance intelligence service.")
        solution_category = Category.objects.create(name="Technology", content_type="solution")
        Solution.objects.create(
            title="Workflow Automation Suite",
            description="Automates repeatable business processes.",
            category=solution_category,
            icon="bi-cpu",
        )
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

    def test_solution_queries_do_not_return_services(self):
        response = get_live_chatbot_response("List our solutions")

        self.assertIn("Workflow Automation Suite", response)
        self.assertNotIn("AI-Powered Learning Platform", response)

    def test_brief_training_question_returns_short_summaries(self):
        response = get_live_chatbot_response("Briefly tell me about our trainings")

        self.assertIn("brief overview", response)
        self.assertIn("Machine Learning Fundamentals", response)
        self.assertLess(len(response), 650)

    def test_company_overview_uses_only_about_us_content(self):
        response = get_live_chatbot_response("What does this company do?")

        self.assertIn("We are PyLoom", response)
        self.assertIn("AI, automation, and custom software", response)
        self.assertNotIn("Machine Learning Fundamentals", response)
        self.assertNotIn("Cybersecurity Essentials", response)

    def test_website_creator_question_does_not_return_unrelated_content(self):
        response = get_live_chatbot_response("Who made this website?")

        self.assertIn("developed by our PyLoom team", response)
        self.assertNotIn("Machine Learning Fundamentals", response)
        self.assertNotIn("Workflow Automation Suite", response)

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

    def test_training_price_list_does_not_include_training_summaries(self):
        response = get_live_chatbot_response("Give me the prices for trainings")

        self.assertIn("Machine Learning Fundamentals: NPR 12,000", response)
        self.assertIn("Cybersecurity Essentials: NPR 9,000", response)
        self.assertNotIn("A practical introduction", response)
        self.assertNotIn("A beginner-friendly course", response)

    def test_training_follow_up_uses_session_context(self):
        history = [
            {'role': 'user', 'content': 'Tell me about our trainings'},
            {'role': 'assistant', 'content': 'Training list shown.'},
            {'role': 'user', 'content': 'Tell me the prices of these trainings'},
            {'role': 'assistant', 'content': 'Price list shown.'},
        ]

        response = get_live_chatbot_response(
            'Can you also give me the durations?',
            chat_history=history,
        )

        self.assertIn('Machine Learning Fundamentals: 6 weeks', response)
        self.assertIn('Cybersecurity Essentials: 4 weeks', response)
        self.assertNotIn('Here are PyLoom insights', response)

    def test_general_follow_up_keeps_the_previous_topic(self):
        history = [
            {'role': 'user', 'content': 'Tell me about our services'},
            {'role': 'assistant', 'content': 'Service list shown.'},
        ]

        response = get_live_chatbot_response(
            'Can you give me more details about them?',
            chat_history=history,
        )

        self.assertIn('AI-Powered Learning Platform', response)
        self.assertIn('Smart Investment Tracker', response)
        self.assertNotIn('Workflow Automation Suite', response)
