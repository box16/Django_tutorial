from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """現在以前の最新5件を表示させる"""
        return filter_valid_question().order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
         """
         現在時刻以前のものだけ許可する
         """
         return filter_valid_question()


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        """
        現在時刻以前のものだけ許可する
        """
        return filter_valid_question()


def filter_valid_question():
    """とりあえず、timezone.now()以前のものを有効としている"""
    have_choices_question = Question.objects.filter(choice__id__isnull=False).filter(pub_date__lte=timezone.now())
    valid_question_id = {x.id for x in have_choices_question}
    return Question.objects.filter(id__in=valid_question_id)

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # postした後に、ブラウザバックなどで変な挙動を起こさないようにするためのRedirect
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))