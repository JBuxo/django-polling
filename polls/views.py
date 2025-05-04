from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
import requests

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Try multiple approaches to get the EC2 public IP
        context['public_ip'] = "Unavailable"
        
        # Approach 1: Try EC2 IMDSv2 (token-based approach)
        try:
            # Step 1: Get token
            token_headers = {'X-aws-ec2-metadata-token-ttl-seconds': '21600'}
            token_response = requests.put('http://169.254.169.254/latest/api/token', headers=token_headers, timeout=1)
            
            if token_response.status_code == 200:
                token = token_response.text
                # Step 2: Use token to get IP
                headers = {'X-aws-ec2-metadata-token': token}
                ip_response = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4', headers=headers, timeout=1)
                
                if ip_response.status_code == 200:
                    context['public_ip'] = ip_response.text
                    return context
        except requests.exceptions.RequestException as e:
            print(f"EC2 IMDSv2 method failed: {e}")
        
        # Approach 2: Try IMDSv1 as fallback
        try:
            response = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4', timeout=1)
            if response.status_code == 200:
                context['public_ip'] = response.text
                return context
        except requests.exceptions.RequestException as e:
            print(f"EC2 IMDSv1 method failed: {e}")
        
        # Approach 3: Use external service as last resort
        try:
            response = requests.get('https://checkip.amazonaws.com', timeout=2)
            if response.status_code == 200:
                context['public_ip'] = response.text.strip()
                return context
        except requests.exceptions.RequestException as e:
            print(f"External IP service method failed: {e}")
        
        return context


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))