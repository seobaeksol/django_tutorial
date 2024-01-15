import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from polls.models import Question


# Create your tests here.
class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for question whose pub_date is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the given number of `days` offset to now
    (negative for questions published in the past, positive for quetions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no question exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the index page.
        """
        question = create_question(question_text="Past Question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question])

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on the index page.
        """
        create_question(question_text="Future Question", days=+30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")

        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        past_question = create_question(question_text="Past Question", days=-30)
        create_question(question_text="Future Question", days=+30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [past_question]
        )

    def test_two_past_question(self):
        past_question_1 = create_question("Past Question 1", days=-30)
        past_question_2 = create_question("Past Question 2", days=-15)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [past_question_2, past_question_1]
        )


class QuestionDetailViewTest(TestCase):
    def test_future_question(self):
        question = create_question("Future Question", days=5)
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        question = create_question("Past Question", days=-5)
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question.question_text)


class QuestionResultsViewTest(TestCase):
    def test_future_question(self):
        question = create_question("Future Question", days=5)
        response = self.client.get(reverse("polls:results", args=(question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        question_text = "Past Question"
        question = create_question(question_text, days=-5)
        response = self.client.get(reverse("polls:results", args=(question.id,)))
        self.assertContains(response, question_text)
