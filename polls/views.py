"""Views class for element that show to the user"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.db.models import F
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages

from .models import Question, Choice


# Create your views here.
class IndexView(generic.ListView):
    """class for KU-Polls Home Page"""

    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last 5 questions
        (Not include those set that set to published in the future)
        Not show the polls that don't have any choices
        """

        # filter no choices question and not yet published question
        question_list = [question for question in Question.objects.all()
                         if question.have_choice() and question.is_published()]

        return Question.objects.filter(pub_date__lte=timezone.now(),
                                       pk__in=[question.pk
                                               for question in
                                               question_list]).order_by(
            "-pub_date")[:5]


class DetailView(generic.DetailView):
    """
    when the user click at polls question
    user will come to this page to vote
    """

    model = Question
    template_name = "polls/detail.html"

    def get(self, request, *args, **kwargs):
        """
        GET method for detail.html page
        """

        # give me question
        question = self.get_object()

        if not question.can_vote():
            # Set an error message
            messages.error(request, f"Voting is not allowed for '{question.question_text}' poll.")

            # Redirect to the index page
            return redirect('polls:index')

        # If voting is allowed, proceed with the normal behavior
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Return the last 5 questions
        (Not include those set that set to published in the future)
        Not show the polls that don't have any choices
        """

        # filter no choices question and not yet published question
        question_list = [question for question in Question.objects.all()
                         if question.have_choice() and question.is_published()]

        return Question.objects.filter(pub_date__lte=timezone.now(),
                                       pk__in=[question.pk
                                               for question in question_list])


class ResultsView(generic.DetailView):
    """After vote this page will appear"""
    model = Question
    template_name = "polls/results.html"

    def get_queryset(self):
        """
        Return the last 5 questions
        (Not include those set that set to published in the future)
        Not show the polls that don't have any choices
        """

        # filter no choices question and not yet published question
        question_list = [question for question in Question.objects.all()
                         if question.have_choice() and question.is_published()]

        return Question.objects.filter(pub_date__lte=timezone.now(),
                                       pk__in=[question.pk
                                               for question in question_list])

    def get_context_data(self, **kwargs):
        """
        Add custom context to the template.
        (Use this method to sent the data that I want to results.html)
        """
        # Get the existing context from the superclass method
        context = super().get_context_data(**kwargs)

        question = self.get_object()

        list_of_question = []  # I hate Django want to use ejs and js instead

        total_votes = sum([int(choice.votes) for choice in question.choice_set.all()])

        for cur_question in question.choice_set.all():

            if total_votes > 0:
                list_of_question.append({
                    "choice_text": cur_question.choice_text,
                    "votes": cur_question.votes,
                    "percentage": (int(cur_question.votes) / total_votes) * 100
                })
            else:
                list_of_question.append({
                    "choice_text": cur_question.choice_text,
                    "votes": cur_question.votes,
                    "percentage": 0
                })

        # Add custom data to the context
        context['list_of_question'] = list_of_question # please work

        # LET'S GO TO RESULT.HTML
        return context


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
        return HttpResponseRedirect(reverse("polls:results",
                                            args=(question.id,)))
