from django import forms
from django.forms import inlineformset_factory

from lessons.models import Lesson, Quarter
from library.models import LibraryItem
from quizzes.models import Choice, Question, Quiz
from subjects.models import Subject

from .models import SiteSettings


WIDGET_ATTRS = {'class': 'form-control'}
SELECT_ATTRS = {'class': 'form-select'}
CHECK_ATTRS  = {'class': 'form-check-input'}


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'slug', 'color', 'icon', 'description', 'order', 'is_active']
        widgets = {
            'name':        forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': 'Matematika'}),
            'slug':        forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': 'matematika'}),
            'color':       forms.Select(attrs=SELECT_ATTRS),
            'icon':        forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': 'bi-calculator'}),
            'description': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 3}),
            'order':       forms.NumberInput(attrs=WIDGET_ATTRS),
            'is_active':   forms.CheckboxInput(attrs=CHECK_ATTRS),
        }
        labels = {
            'name': 'Fan nomi', 'slug': 'Slug (URL)', 'color': 'Rang',
            'icon': 'Icon (Bootstrap Icons)', 'description': 'Tavsif',
            'order': 'Tartib', 'is_active': 'Faol',
        }


class QuarterForm(forms.ModelForm):
    class Meta:
        model = Quarter
        fields = ['subject', 'grade', 'number', 'title']
        widgets = {
            'subject':    forms.Select(attrs=SELECT_ATTRS),
            'grade':      forms.Select(attrs=SELECT_ATTRS),
            'number':     forms.Select(attrs=SELECT_ATTRS),
            'title':      forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': 'Chorak sarlavhasi (ixtiyoriy)'}),
        }
        labels = {
            'subject': 'Fan', 'grade': 'Sinf', 'number': 'Chorak raqami',
            'title': 'Sarlavha',
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            'title', 'slug', 'subject', 'grade', 'quarter',
            'description', 'youtube_url',
            'pdf_conspect', 'thumbnail', 'duration_minutes',
            'order', 'is_published',
        ]
        widgets = {
            'title':           forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': 'Dars sarlavhasi'}),
            'slug':            forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': 'dars-slugi'}),
            'subject':         forms.Select(attrs=SELECT_ATTRS),
            'grade':           forms.Select(attrs=SELECT_ATTRS),
            'quarter':         forms.Select(attrs=SELECT_ATTRS),
            'description':     forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 4}),
            'youtube_url':     forms.URLInput(attrs={
                **WIDGET_ATTRS,
                'placeholder': 'https://youtube.com/watch?v=XXXXXXXXXXX',
                'pattern': r'https?://(www\.)?(youtube\.com|youtu\.be)/.+',
            }),
            'pdf_conspect':    forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'thumbnail':       forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'duration_minutes': forms.NumberInput(attrs={**WIDGET_ATTRS, 'min': 0}),
            'order':           forms.NumberInput(attrs={**WIDGET_ATTRS, 'min': 0}),
            'is_published':    forms.CheckboxInput(attrs=CHECK_ATTRS),
        }
        labels = {
            'title': 'Sarlavha', 'slug': 'Slug', 'subject': 'Fan',
            'grade': 'Sinf', 'quarter': 'Chorak',
            'description': 'Tavsif',
            'youtube_url': 'YouTube video havolasi',
            'pdf_conspect': 'PDF konspekt', 'thumbnail': 'Muqova rasmi',
            'duration_minutes': 'Davomiyligi (daqiqa)', 'order': 'Tartib',
            'is_published': 'Nashr etilgan',
        }
        help_texts = {
            'youtube_url': 'Misol: https://youtube.com/watch?v=dQw4w9WgXcQ yoki https://youtu.be/dQw4w9WgXcQ',
        }

    def clean_youtube_url(self):
        from lessons.models import extract_youtube_id
        url = self.cleaned_data.get('youtube_url', '').strip()
        if not url:
            return url
        if not extract_youtube_id(url):
            raise forms.ValidationError(
                "Yaroqsiz YouTube havolasi. Namuna: https://youtube.com/watch?v=XXXXXXXXXXX"
            )
        return url


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'quiz_type', 'lesson', 'quarter', 'time_limit', 'pass_score', 'max_attempts', 'is_published']
        widgets = {
            'title':        forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': 'Test sarlavhasi'}),
            'quiz_type':    forms.Select(attrs=SELECT_ATTRS),
            'lesson':       forms.Select(attrs=SELECT_ATTRS),
            'quarter':      forms.Select(attrs=SELECT_ATTRS),
            'time_limit':   forms.NumberInput(attrs={**WIDGET_ATTRS, 'min': 0}),
            'pass_score':   forms.NumberInput(attrs={**WIDGET_ATTRS, 'min': 1, 'max': 100}),
            'max_attempts': forms.NumberInput(attrs={**WIDGET_ATTRS, 'min': 0}),
            'is_published': forms.CheckboxInput(attrs=CHECK_ATTRS),
        }
        labels = {
            'title': 'Test sarlavhasi', 'quiz_type': 'Test turi',
            'lesson': 'Dars (dars testi uchun)', 'quarter': 'Chorak (chorak testi uchun)',
            'time_limit': 'Vaqt chegarasi (daqiqa, 0=cheksiz)',
            'pass_score': "O'tish bali (%)",
            'max_attempts': 'Maksimal urinishlar (0=cheksiz)',
            'is_published': 'Nashr etilgan',
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'image', 'order', 'score']
        widgets = {
            'text':          forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 2, 'placeholder': 'Savol matni'}),
            'question_type': forms.Select(attrs=SELECT_ATTRS),
            'image':         forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'order':         forms.NumberInput(attrs={**WIDGET_ATTRS, 'min': 0}),
            'score':         forms.NumberInput(attrs={**WIDGET_ATTRS, 'min': 1}),
        }
        labels = {
            'text': 'Savol matni', 'question_type': 'Savol turi',
            'image': 'Rasm (ixtiyoriy)', 'order': 'Tartib', 'score': 'Ball',
        }


ChoiceFormSet = inlineformset_factory(
    Question, Choice,
    fields=['text', 'is_correct'],
    extra=4, max_num=6, can_delete=True,
    widgets={
        'text':       forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': 'Variant matni'}),
        'is_correct': forms.CheckboxInput(attrs=CHECK_ATTRS),
    },
    labels={'text': 'Variant', 'is_correct': "To'g'ri javob"},
)


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            'use_real_stats',
            'students_count', 'video_lessons_count', 'subjects_count',
            'certificates_count', 'active_students_count', 'average_rating',
            'test_questions_count', 'grades_count',
        ]
        widgets = {
            'use_real_stats':        forms.CheckboxInput(attrs=CHECK_ATTRS),
            'students_count':        forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': '10,000+'}),
            'video_lessons_count':   forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': '800+'}),
            'subjects_count':        forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': '15+'}),
            'certificates_count':    forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': '4,200+'}),
            'active_students_count': forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': '10K+'}),
            'average_rating':        forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': '4.9'}),
            'test_questions_count':  forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': '1,200+'}),
            'grades_count':          forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': '11'}),
        }
        labels = {
            'use_real_stats': 'Haqiqiy statistikani ishlatish (bazadan)',
            'students_count': "O'quvchilar soni",
            'video_lessons_count': 'Video darslar soni',
            'subjects_count': 'Fanlar soni',
            'certificates_count': 'Sertifikatlar soni',
            'active_students_count': "Faol o'quvchilar",
            'average_rating': "O'rtacha baho",
            'test_questions_count': 'Test savollari soni',
            'grades_count': 'Sinf darslari soni',
        }


class LibraryItemForm(forms.ModelForm):
    class Meta:
        model = LibraryItem
        fields = [
            'title', 'subject', 'grade', 'author', 'item_type',
            'file', 'cover_image', 'description', 'is_published',
        ]
        widgets = {
            'title':       forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': 'Material sarlavhasi'}),
            'subject':     forms.Select(attrs=SELECT_ATTRS),
            'grade':       forms.Select(attrs=SELECT_ATTRS),
            'author':      forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': 'Muallif'}),
            'item_type':   forms.Select(attrs=SELECT_ATTRS),
            'file':        forms.FileInput(attrs={'class': 'form-control'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'description': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 3}),
            'is_published': forms.CheckboxInput(attrs=CHECK_ATTRS),
        }
        labels = {
            'title': 'Sarlavha', 'subject': 'Fan', 'grade': 'Sinf',
            'author': 'Muallif', 'item_type': 'Material turi',
            'file': 'Fayl', 'cover_image': 'Muqova rasmi',
            'description': 'Tavsif', 'is_published': 'Nashr etilgan',
        }
