from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from polls.models import Question


# Create your views here.
def index(request):
    lastest_question_list = Question.objects.order_by("-pub_date")[:5]
    return render(
        request, "polls/index.html", {"latest_question_list": lastest_question_list}
    )


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})


def results(request, question_id):
    return HttpResponse(f"You're looking at the results of question {question_id}.")


def vote(request, question_id):
    return HttpResponse(f"You're voting on question {question_id}.")
