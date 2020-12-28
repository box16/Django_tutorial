import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

def create_question(question_text, days):
    """指定した日付でQuestionを作成する"""
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """未来の日付の時は、False"""
        future_question = create_question("",30)
        self.assertIs(future_question.was_published_recently(), False)
    
    def test_was_published_recently_with_old_question(self):
        """古すぎる日付の時は、False"""
        old_question = create_question("",-30)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """現在時刻付近の時は、True"""
        recent_question = create_question("",0)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """Questionが何もない時は空表示"""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question_has_choice(self):
        """過去choice有りは空表示"""
        q = create_question(question_text="Past question.", days=-30)
        q.choice_set.create(choice_text='', votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )
    
    def test_past_question_no_choice(self):
        """過去choice無しは空表示"""
        q = create_question(question_text="Past question.", days=-30)
        
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_has_choice(self):
        """未来choiceありは空表示"""
        q = create_question(question_text="Future question.", days=30)
        
        q.choice_set.create(choice_text='', votes=0)
        
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_no_choice(self):
        """未来choice無しは空表示"""
        q = create_question(question_text="Future question.", days=30)

        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_has_choice_and_past_question_has_choice(self):
        """未来Choiceあり、過去Choiceありは過去のみ表示"""
        past_q = create_question(question_text="Past question.", days=-30)
        future_q = create_question(question_text="Future question.", days=30)
        
        past_q.choice_set.create(choice_text='', votes=0)
        future_q.choice_set.create(choice_text='', votes=0)
        
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )
    
    def test_future_question_no_choice_and_past_question_has_choice(self):
        """未来Choice無し、過去Choiceありは過去のみ表示"""
        past_q = create_question(question_text="Past question.", days=-30)
        future_q = create_question(question_text="Future question.", days=30)
        
        past_q.choice_set.create(choice_text='', votes=0)
        
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question_has_choice_and_past_question_no_choice(self):
        """未来Choiceあり、過去Choiceなしは空表示"""
        past_q = create_question(question_text="Past question.", days=-30)
        future_q = create_question(question_text="Future question.", days=30)
        
        future_q.choice_set.create(choice_text='', votes=0)
        
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_no_choice_and_past_question_no_choice(self):
        """未来Choiceなし、過去Choiceなしは空表示"""
        past_q = create_question(question_text="Past question.", days=-30)
        future_q = create_question(question_text="Future question.", days=30)
        
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_two_past_questions_both_has_choice(self):
        """過去2つともchoice有りはどちらも表示"""
        q_1 = create_question(question_text="Past question 1.", days=-30)
        q_2 = create_question(question_text="Past question 2.", days=-5)
        
        q_1.choice_set.create(choice_text='', votes=0)
        q_2.choice_set.create(choice_text='', votes=0)

        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

    def test_two_past_questions_only_one_has_choice(self):
        """過去1つだけchoice有りはそれだけ表示"""
        q_1 = create_question(question_text="Past question 1.", days=-30)
        q_2 = create_question(question_text="Past question 2.", days=-5)
        
        q_1.choice_set.create(choice_text='', votes=0)

        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 1.>']
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question_has_choice(self):
        """未来choice有りは404"""
        future_question = create_question(question_text='Future question.', days=5)
        
        future_question.choice_set.create(choice_text='', votes=0)

        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_future_question_no_choice(self):
        """未来choice無しは404"""
        future_question = create_question(question_text='Future question.', days=5)
        
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_has_choice(self):
        """過去choice有りは表示"""
        past_question = create_question(question_text='Past Question.', days=-5)
        
        past_question.choice_set.create(choice_text='', votes=0)

        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
    
    def test_past_question_no_choice(self):
        """過去choice無しは404"""
        past_question = create_question(question_text='Past Question.', days=-5)
        
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class QuestionResultsViewTests(TestCase):
    def test_future_question_has_choice(self):
        """未来choice有りは404"""
        future_question = create_question(question_text='Future question.', days=5)
        
        future_question.choice_set.create(choice_text='', votes=0)

        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_future_question_no_choice(self):
        """未来choice無しは404"""
        future_question = create_question(question_text='Future question.', days=5)
        
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_has_choice(self):
        """過去choice有りは表示"""
        past_question = create_question(question_text='Past Question.', days=-5)
        
        past_question.choice_set.create(choice_text='', votes=0)

        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
    
    def test_past_question_no_choice(self):
        """過去choice無しは404"""
        past_question = create_question(question_text='Past Question.', days=-5)
        
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)