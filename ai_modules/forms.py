from django import forms


class AIChatForm(forms.Form):
    message = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Savolingizni yozing...',
            'maxlength': 1000,
        }),
        max_length=1000,
    )


class AIEssayForm(forms.Form):
    text = forms.CharField(
        label='Inshoni kiriting',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Matnni shu yerga yozing yoki joylashtiring...',
        }),
        min_length=50,
        max_length=5000,
    )
    language = forms.ChoiceField(
        choices=[('uz', "O'zbek"), ('ru', 'Rus'), ('en', 'Ingliz')],
        label='Til',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class AITestGenerateForm(forms.Form):
    topic = forms.CharField(
        label='Mavzu',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Masalan: Kvadrat tenglamalar",
        }),
    )
    difficulty = forms.ChoiceField(
        choices=[('easy', 'Oson'), ('medium', "O'rta"), ('hard', 'Qiyin')],
        label='Qiyinlik darajasi',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    count = forms.IntegerField(
        label='Savollar soni',
        min_value=5,
        max_value=30,
        initial=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    language = forms.ChoiceField(
        choices=[('uz', "O'zbek"), ('ru', 'Rus'), ('en', 'Ingliz')],
        label='Til',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
