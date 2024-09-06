"""This module contains all test case for IndexView classes."""

import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from polls.models import Question

def create_question(question_text, days, choices: list):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    new_question = Question.objects.create(
        question_text=question_text,
        pub_date=time)

    # add choice to question

    for all_choice in choices:
        new_question.choice_set.create(
            choice_text=all_choice
        )
    return new_question


class QuestionIndexViewTests(TestCase):
    """Test case for Index class in views.py"""

    def test_no_choice(self):
        """
        Question that doesn't have a choice shouldn't appear to user
        """
        create_question(question_text="HAHAHA No CHOICE", days=-2, choices=[])
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30,
                                   choices=["Test1", "Test2"])

        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"],
                                 [question], )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30,
                        choices=["Test1", "Test2"])

        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30,
                                   choices=["Test1", "Test2"])

        create_question(question_text="Future question.", days=30,
                        choices=["Test1", "Test2"])

        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"],
                                 [question])

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30,
                                    choices=["Test1", "Test2"])

        question2 = create_question(question_text="Past question 2.", days=-5,
                                    choices=["Test1", "Test2"])

        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [question2, question1])

    def test_two_past_questions_and_one_future(self):
        """
        The questions index page should only display question1
        and question 2 because question 3 pub_date is in the future.
        """
        question1 = create_question(question_text="Past question 1.", days=-30,
                                    choices=["Test1", "Test2"])

        question2 = create_question(question_text="Past question 2.", days=-5,
                                    choices=["Test1", "Test2"])

        create_question(question_text="Future question 3.", days=10,
                        choices=["FOUL TARNISED"])

        response = self.client.get(reverse("polls:index"))

        self.assertQuerySetEqual(
            response.context["latest_question_list"], [question2, question1])