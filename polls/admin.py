"""This module is for Admin only"""
from django.contrib import admin

from .models import Question, Choice


# Register your models here.

class ChoiceInline(admin.TabularInline):
    """
    change choices style to TabularInline and add 3 more blank choice
    to make it easier for admin to update the question.
    """
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    """
    After admin click to choice name go to this page.
    This page is for update specific question element (Add new choice, Delete/Change Name Question)
    """

    # make question_text and date in Question page separate (look like add margin to div)
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"]}),
    ]

    # insert choice list to the Question page make it easier to manage
    inlines = [ChoiceInline]

    # make pubdate and publish appear in admin home page
    list_display = ["question_text", "pub_date", "was_published_recently"]

    # add sorting table
    list_filter = ["pub_date"]

    # add search box
    search_fields = ["question_text"]


admin.site.register(Question, QuestionAdmin)
