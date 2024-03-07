import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

class QuestionModelTests(TestCase):
    def test_given_recent_question_when_was_published_recently_should_return_true(self):
        time = timezone.now() - datetime.timedelta(hours=1)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), True)
        
    def test_given_old_question_when_was_published_recently_should_return_false(self):
        time = timezone.now() - datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)
        
    def test_given_future_question_when_was_published_recently_should_return_false(self):
        time = timezone.now() + datetime.timedelta(hours=1)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

def given_a_future_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def given_a_past_question(question_text, days):
    time = timezone.now() - datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
    def test_given_no_question_Should_warn(self):
        response = self.client.get(reverse("polls:index"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])
        
    def test_given_past_question_should_display_it(self):
        question = given_a_past_question(question_text="Past question.", days=30)
        
        response = self.client.get(reverse("polls:index"))
        
        self.assertQuerySetEqual(response.context["latest_question_list"], [question])
        
    def test_given_future_question_should_show_none(self):
        given_a_future_question(question_text="Future question.", days=30)
        
        response = self.client.get(reverse("polls:index"))
        
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])
        
    def test_given_future_question_and_past_question_should_display_past_only(self):
        question = given_a_past_question(question_text="Past question.", days=30)
        given_a_future_question(question_text="Future question", days=30)
        
        response = self.client.get(reverse("polls:index"))
        
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [question]
        )
        
    def test_given_two_past_questions_should_display_both(self):
        question1 = given_a_past_question(question_text="Past question 1", days=30)
        question2 = given_a_past_question(question_text="Past question 2", days=4)
        
        response = self.client.get(reverse("polls:index"))
        
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [question1, question2],
        )

class QuestionDetailViewTest(TestCase):
    def test_given_future_question_should_return_404(self):
        future_question = given_a_future_question(question_text="Future question", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
        
    def test_given_past_question_should_display_the_question_text(self):
        past_question = given_a_past_question(question_text="Past question", days=5)
        url = reverse("polls:detail", args=(past_question.id,))
        
        response = self.client.get(url)
        
        self.assertContains(response, past_question.question_text)
