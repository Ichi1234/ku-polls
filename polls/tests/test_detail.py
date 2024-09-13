"""This module contains all test case for DetailView classes."""

import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from polls.models import Question


def create_question(question_text, days, choices: list):
    """
    Create a question with the given `question_text`.

    and published the given number of `days` offset to now
    (negative for questions published
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


class QuestionDetailViewTests(TestCase):
    """Test cases for Detail class in views.py."""

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future.

        returns a 404 not found.
        """
        future_question = create_question(question_text="Future Question",
                                          days=5,
                                          choices=["Test1", "Test2"])

        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past.

        Displays the question's text.
        """
        past_question = create_question(question_text="Past Question.",
                                        days=-5,
                                        choices=["Test1", "Test2"])

        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_no_choice(self):
        """Question that doesn't have a choice shouldn't appear to user."""
        no_choice_question = create_question(question_text="HAHAHA No CHOICE",
                                             days=-2, choices=[])

        url = reverse("polls:detail", args=(no_choice_question.id,))
        response = self.client.get(url)

        # Ensure the no_choice_question is not displayed
        self.assertEqual(response.status_code, 404)
