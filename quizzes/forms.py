from django import forms

from .models import AttemptAnswer, Choice, Question, Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ('title', 'quiz_type', 'lesson', 'quarter', 'time_limit', 'pass_score', 'max_attempts', 'is_published')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'quiz_type': forms.Select(attrs={'class': 'form-select'}),
            'lesson': forms.Select(attrs={'class': 'form-select'}),
            'quarter': forms.Select(attrs={'class': 'form-select'}),
            'time_limit': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'pass_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
            'max_attempts': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('question_type', 'text', 'image', 'order', 'score')
        widgets = {
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ('text', 'is_correct', 'order')
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AttemptAnswerForm(forms.Form):
    """Test yechish jarayonida bitta savolga javob berish uchun."""
    choice = forms.ModelChoiceField(
        queryset=Choice.objects.none(),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        empty_label=None,
        label='',
    )

    def __init__(self, question: Question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question
        self.fields['choice'].queryset = question.choices.order_by('order')
        self.fields['choice'].label_from_instance = lambda obj: obj.text
