"""This module used to manage everything about database"""

import datetime

from django.db import models
from django.utils import timezone
from django.contrib import admin


# Create your models here.
class Question(models.Model):
    """
    This class used for handle database of questions
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        """:return question_text to show it to user"""
        return self.question_text

    def was_published_recently(self):
        """If the question published recently return True else false"""
        current_time = timezone.now()
        return current_time - datetime.timedelta(days=1) <= self.pub_date <= current_time

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def was_published_recently(self):
        """If the question published recently return True else false"""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    """
     This class used for handle database of choices
     """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """:return choice's text to show it to user"""
        return self.choice_text

