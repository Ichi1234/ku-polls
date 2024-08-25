"""Views class for element that show to the user"""

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.db.models import F
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Question, Choice


# Create your views here.
class IndexView(generic.ListView):
    """class for KU-Polls Home Page"""

    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last 5 questions (Not include those set that set to published in the future)
        """

        # filter no choices question
        question_list = []
        for each_question in Question.objects.all():
            if not [choice for choice in each_question.choice_set.all()]:
                continue
            else:
                question_list.append(each_question)

        return Question.objects.filter(pub_date__lte=timezone.now(),
                                       pk__in=[question.pk for question in question_list]).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    """when the user click at polls question user will come to this page to vote"""

    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    """After vote this page will appear"""
    model = Question
    template_name = "polls/results.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


def vote(request, question_id):
    """Function used to update vote to choice"""
    question = get_object_or_404(Question, pk=question_id)
    try:
        select_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # display error
        return render(
            request, "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        select_choice.votes = F("votes") + 1
        select_choice.save()

        # return redirect after finish dealing with POST data
        # (Prevent data from posted twice if user click at back button)
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

