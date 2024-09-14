"""Tests of authentication."""
import django.test
from django.urls import reverse
from django.contrib.auth.models import User
from polls.models import Question, Choice, Vote
from mysite import settings


class UserAuthTest(django.test.TestCase):
    """Class to test the Login Logout system for the KU-Polls."""

    def setUp(self):
        """Create Account and Question to set up the test field."""
        # superclass setUp creates a
        # Client object and initializes test database
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
                         username=self.username,
                         password=self.password,
                         email="testuser@nowhere.com"
                         )
        self.user1.first_name = "Tester"
        self.user1.save()
        # we need a poll question to test voting
        q = Question.objects.create(question_text="First Poll Question")
        q.save()
        # a few choices
        for n in range(1, 4):
            choice = Choice(choice_text=f"Choice {n}", question=q)
            choice.save()
        self.question = q

    def test_logout(self):
        """A user can logout using the logout url.

        As an authenticated user,
        when I visit /accounts/logout/
        then I am logged out
        and then redirected to the login page.
        """
        logout_url = reverse("logout")

        # Authenticate the user.
        # We want to logout this user, so we need to associate the
        # user user with a session.  Setting client.user = ... doesn't work.
        # Use Client.login(username, password) to do that.
        # Client.login returns true on success
        self.assertTrue(
              self.client.login(username=self.username, password=self.password)
                       )
        # visit the logout page
        response = self.client.get(logout_url)
        self.assertEqual(302, response.status_code)

        # should redirect us to where? Polls index? Login?
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view(self):
        """A user can login using the login view."""
        login_url = reverse("login")
        # Can get the login page
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)
        # Can login using a POST request
        # usage: client.post(url, {'key1":"value", "key2":"value"})
        form_data = {"username": "testuser",
                     "password": "FatChance!"}

        response = self.client.post(login_url, form_data)
        # after successful login, should redirect browser somewhere
        self.assertEqual(302, response.status_code)
        # should redirect us to the polls index page ("polls:index")
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_auth_required_to_vote(self):
        """Authentication is required to submit a vote.

        As an unauthenticated user,
        when I submit a vote for a question,
        then I am redirected to the login page
        or I receive a 403 response (FORBIDDEN)
        """
        vote_url = reverse('polls:vote', args=[self.question.id])

        # what choice to vote for?
        choice = self.question.choice_set.first()
        # the polls detail page has a form, each choice is identified by its id
        form_data = {"choice": f"{choice.id}"}
        response = self.client.post(vote_url, form_data)
        # should be redirected to the login page
        self.assertEqual(response.status_code, 302)  # could be 303

        # the query parameter ?next=/polls/1/vote/
        # How to fix it?
        # self.assertRedirects(response, reverse('login') )
        login_with_next = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_with_next)

    def test_auth_user_can_vote_only_one_vote(self):
        """Authenticated user can vote only one time."""
        login_url = reverse("login")
        self.client.get(login_url)
        form_data = {"username": "testuser",
                     "password": "FatChance!"}
        self.client.post(login_url, form_data)

        vote_url = reverse('polls:vote',
                           args=[self.question.id])

        # what choice to vote for?
        choice = self.question.choice_set.first()
        # the polls detail page has a form, each choice is identified by its id
        form_data = {"choice": f"{choice.id}"}
        self.client.post(vote_url, form_data)

        total_vote = sum([int(choice.votes)
                          for choice in self.question.choice_set.all()])

        # first time vote
        self.assertEqual(1, total_vote)

        vote_url = reverse('polls:vote',
                           args=[self.question.id])

        # what choice to vote for?
        choice = self.question.choice_set.last()
        # the polls detail page has a form, each choice is identified by its id
        form_data = {"choice": f"{choice.id}"}
        self.client.post(vote_url, form_data)

        total_vote = sum([int(choice.votes)
                          for choice in self.question.choice_set.all()])

        # second time vote (Vote should change)
        self.assertEqual(1, total_vote)

    def test_auth_user_choice_changed_if_already_vote(self):
        """
        Authenticated user can vote only one time.

        And if vote again choice should change into the new one
        """
        login_url = reverse("login")
        self.client.get(login_url)
        form_data = {"username": "testuser",
                     "password": "FatChance!"}
        self.client.post(login_url, form_data)

        vote_url = reverse('polls:vote',
                           args=[self.question.id])

        # what choice to vote for?
        choice = self.question.choice_set.first()
        # the polls detail page has a form, each choice is identified by its id
        form_data = {"choice": f"{choice.id}"}
        self.client.post(vote_url, form_data)

        current_choice = Vote.objects.get(user=self.user1,
                                          choice__question=self.question)

        # first time vote
        self.assertEqual(choice.choice_text,
                         current_choice.choice.choice_text)

        vote_url = reverse('polls:vote',
                           args=[self.question.id])

        # what choice to vote for?
        choice = self.question.choice_set.last()
        # the polls detail page has a form, each choice is identified by its id
        form_data = {"choice": f"{choice.id}"}
        self.client.post(vote_url, form_data)

        current_choice = Vote.objects.get(user=self.user1,
                                          choice__question=self.question)

        # second time vote (Choice should change)
        self.assertEqual(choice.choice_text,
                         current_choice.choice.choice_text)

    def test_auth_user_can_reset_vote(self):
        """Authenticated user can reset the vote."""
        login_url = reverse("login")
        self.client.get(login_url)
        form_data = {"username": "testuser",
                     "password": "FatChance!"}
        self.client.post(login_url, form_data)

        vote_url = reverse('polls:vote',
                           args=[self.question.id])

        # what choice to vote for?
        choice = self.question.choice_set.first()
        # the polls detail page has a form, each choice is identified by its id
        form_data = {"choice": f"{choice.id}"}
        self.client.post(vote_url, form_data)

        total_vote = sum([int(choice.votes)
                          for choice in self.question.choice_set.all()])

        # first time vote
        self.assertEqual(1, total_vote)

        vote_url = reverse('polls:reset',
                           args=[self.question.id])

        # what choice to vote for?
        choice = self.question.choice_set.last()
        # the polls detail page has a form, each choice is identified by its id
        form_data = {"choice": f"{choice.id}"}
        self.client.post(vote_url, form_data)

        total_vote = sum([int(choice.votes)
                          for choice in self.question.choice_set.all()])

        # second time vote (Vote should change)
        self.assertEqual(0, total_vote)