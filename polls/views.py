"""Views class for element that show to the user"""
from random import choice

from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Case, When, BooleanField

from .models import Question, Choice, Vote


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

        # why Django can't use method in objects to filter :(
        return (
            Question.objects.annotate( # create calculation field
                have_choice=Count('choice'), # count how many choices
                is_published=Case( # case is case (create something like if-else)
                    When(pub_date__lte=timezone.now(), then=True), # when is condition in if else
                    default=False,
                    output_field=BooleanField(), # output bool
                )
            )
            .filter(is_published=True, have_choice__gt=0)
            .order_by("-pub_date")[:5]
        )


class DetailView(generic.DetailView):
    """
    when the user click at polls question
    user will come to this page to vote
    ( Display the choice for a poll )
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
            messages.error(request,
                           f"Voting is not allowed for"
                           f" '{question.question_text}' poll.")

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

        return (
            Question.objects.annotate(  # create calculation field
                have_choice=Count('choice'),  # count how many choices
                is_published=Case(  # case is case (create something like if-else)
                    When(pub_date__lte=timezone.now(), then=True),  # when is condition in if else
                    default=False,
                    output_field=BooleanField(),  # output bool
                )
            )
            .filter(is_published=True, have_choice__gt=0)
            .order_by("-pub_date")
        )

    def get_context_data(self, **kwargs):
        """
        Add custom context to the template.
        (Use this method to sent the data that I want to results.html)
        """
        # Get the existing context from the superclass method
        context = super().get_context_data(**kwargs)

        question = self.get_object()

        # GIVE ME YOUR IDENTITY USER!!!
        current_user = self.request.user

        list_of_question = []

        # for set default radio button
        try:
            already_select = Vote.objects.get(user=current_user, choice__question=question)

        except (TypeError, Vote.DoesNotExist):

            # user didn't vote for this question
            already_select = False

        for cur_choice in question.choice_set.all():
            # Get the user's vote

                # user has a vote for this question!
                if already_select and already_select.choice.choice_text == cur_choice.choice_text:
                    list_of_question.append({
                        "choice_text": cur_choice.choice_text,
                        "id": cur_choice.id,
                        "selected_choice": already_select.choice,
                    })

                else:
                    list_of_question.append({
                        "choice_text": cur_choice.choice_text,
                        "id": cur_choice.id,
                        "selected_choice": already_select
                    })

        # Add custom data to the context
        context['user_selected_choice'] = list_of_question

        return context


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

        return (
            Question.objects.annotate(  # create calculation field
                have_choice=Count('choice'),  # count how many choices
                is_published=Case(  # case is case (create something like if-else)
                    When(pub_date__lte=timezone.now(), then=True),  # when is condition in if else
                    default=False,
                    output_field=BooleanField(),  # output bool
                )
            )
            .filter(is_published=True, have_choice__gt=0)
            .order_by("-pub_date")
        )

    def get_context_data(self, **kwargs):
        """
        Add custom context to the template.
        (Use this method to sent the data that I want to results.html)
        """
        # Get the existing context from the superclass method
        context = super().get_context_data(**kwargs)

        question = self.get_object()

        list_of_question = []  # I hate Django want to use ejs and js instead

        total_votes = sum([int(choice.votes)
                           for choice in question.choice_set.all()])

        for cur_question in question.choice_set.all():

            if total_votes > 0:
                list_of_question.append({
                    "choice_text": cur_question.choice_text,
                    "votes": cur_question.votes,
                    "percentage": round(int(cur_question.votes)
                                        / total_votes * 100, 2)
                })
            else:
                list_of_question.append({
                    "choice_text": cur_question.choice_text,
                    "votes": cur_question.votes,
                    "percentage": 0
                })

        # Add custom data to the context
        context['list_of_question'] = list_of_question  # please work

        # LET'S GO TO RESULT.HTML
        return context

@login_required
def vote(request, question_id):
    """Function used to update vote to choice"""

    question = get_object_or_404(Question, pk=question_id)

    try:
        select_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # display error
        messages.error(request, "You didn't select a choice.")

        # Redirect to the index page
        return redirect('polls:detail', question.pk)

    # Reference to the current user
    this_user = request.user

    # Get the user's vote
    try:
        new_vote = Vote.objects.get(user=this_user, choice__question=question)
        # user has a vote for this question! Update his choice.
        new_vote.choice = select_choice
        new_vote.save()
        messages.success(request,f"Your vote was changed to '{select_choice.choice_text}'")

    except Vote.DoesNotExist:
        # does not have a vote yet
        Vote.objects.create(user=this_user, choice=select_choice)
        # automatically saved
        messages.success(request, f"You voted for '{select_choice.choice_text}'")

    # return redirect after finish dealing with POST data
    # (Prevent data from posted twice if user click at back button)
    return HttpResponseRedirect(reverse("polls:results",
                                        args=(question.id,)))

@login_required
def logout_view(request):
    """Logout function"""
    # Django documentation has this. Why I didn't look at it before fighting with this.
    logout(request)
    return redirect('login')
