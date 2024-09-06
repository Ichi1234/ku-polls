"""This module contains all test case for all model classes."""

import datetime

from django.test import TestCase
from django.utils import timezone

from polls.models import Question


# Create your tests here.


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
