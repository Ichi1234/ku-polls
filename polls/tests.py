"""This module contains all test case for all modules."""

import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


# Create your tests here.

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


class QuestionModelTests(TestCase):
    """Test cases for Question class in models.py"""

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = (timezone.now()
                - datetime.timedelta(hours=23, minutes=59, seconds=59))
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_default_pub_date_equal_to_now(self):
        """
        This test checks that the default pub_date time is the current time,
        considering only year, month, day, hour, and minute
        because GitHub test too slow
        """
        no_pub_date_question = Question()
        pub_date = no_pub_date_question.pub_date
        now = timezone.now()

        # Check that year, month, day, hour,
        # and minute are equal
        # However, milli sec don't need
        self.assertEqual(pub_date.year, now.year)
        self.assertEqual(pub_date.month, now.month)
        self.assertEqual(pub_date.day, now.day)
        self.assertEqual(pub_date.hour, now.hour)
        self.assertEqual(pub_date.minute, now.minute)

    def test_default_end_date_is_null(self):
        """
        This test checks that the default value for end_date is None.
        """
        no_end_date_question = Question()
        self.assertIsNone(no_end_date_question.end_date)

    def test_is_published_past_question(self):
        """
        :return: True if Question is already published
        (current time is > than pub_date)
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        past_question = Question(pub_date=time)  # end date is null
        self.assertEqual(True, past_question.is_published())

    def test_is_published_future_question(self):
        """
        :return: False if Question has not published
        (current time is < than pub_date)
        """
        time = timezone.now() + datetime.timedelta(days=1, seconds=1)
        past_question = Question(pub_date=time)
        self.assertEqual(False, past_question.is_published())

    def test_can_vote_past_question_future_end_date(self):
        """
        :return: True if Question is already published
        (current time is > than pub_date)
        and can vote (polls still not reach end_date)
        """
        start_time = timezone.now() - datetime.timedelta(days=2, seconds=1)
        end_time = timezone.now() + datetime.timedelta(days=2, seconds=1)
        past_question = Question(pub_date=start_time, end_date=end_time)
        self.assertEqual(True, past_question.can_vote())

    def test_can_vote_past_question_past_end_date(self):
        """
        :return: False if Question has not published
        (current time is > than pub_date)
        or can't vote anymore (polls reach end_date)
        """
        start_time = timezone.now() - datetime.timedelta(days=5, seconds=1)
        end_time = timezone.now() - datetime.timedelta(days=2, seconds=1)
        past_question = Question(pub_date=start_time, end_date=end_time)
        self.assertEqual(False, past_question.can_vote())

    def test_can_vote_future_question_future_end_date(self):
        """
        :return: False because it in future you can't vote future polls!
        """
        start_time = timezone.now() + datetime.timedelta(days=5, seconds=1)
        end_time = timezone.now() + datetime.timedelta(days=8, seconds=1)
        future_question = Question(pub_date=start_time, end_date=end_time)
        self.assertEqual(False, future_question.can_vote())

    def test_can_vote_future_question_past_end_date(self):
        """
        :return: False
        Why you even created this polls!?
        Why the end_date is before future date???
        This is ridiculous!!!
        """
        start_time = timezone.now() + datetime.timedelta(days=2, seconds=1)
        end_time = timezone.now() - datetime.timedelta(days=2, seconds=1)
        future_question = Question(pub_date=start_time, end_date=end_time)
        self.assertEqual(False, future_question.can_vote())


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


class QuestionDetailViewTests(TestCase):
    """Test cases for Detail class in views.py"""

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future Question",
                                          days=5,
                                          choices=["Test1", "Test2"])

        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.",
                                        days=-5,
                                        choices=["Test1", "Test2"])

        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_no_choice(self):
        """
        Question that doesn't have a choice shouldn't appear to user
        """

        no_choice_question = create_question(question_text="HAHAHA No CHOICE",
                                             days=-2, choices=[])
        url = reverse("polls:detail", args=(no_choice_question.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class QuestionResultViewTests(TestCase):
    """Test cases for Result class in views.py"""

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future Question",
                                          days=5,
                                          choices=["Test1", "Test2"])

        url = reverse("polls:results", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.",
                                        days=-5,
                                        choices=["Test1", "Test2"])

        url = reverse("polls:results", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_no_choice(self):
        """
        Question that doesn't have a choice shouldn't appear to user
        """

        no_choice_question = create_question(question_text="HAHAHA No CHOICE",
                                             days=-2, choices=[])
        url = reverse("polls:results", args=(no_choice_question.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
