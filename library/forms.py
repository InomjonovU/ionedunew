from django import forms

from .models import LibraryItem


class LibraryItemForm(forms.ModelForm):
    class Meta:
        model = LibraryItem
        fields = (
            'title', 'subject', 'grade', 'author',
            'item_type', 'file', 'cover_image',
            'description', 'is_published',
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'grade': forms.Select(attrs={'class': 'form-select'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'item_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class LibrarySearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Qidiruv',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kitob nomi yoki muallif...',
        }),
    )
    subject = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput(),
    )
    grade = forms.ChoiceField(
        required=False,
        choices=[('', 'Barcha sinflar')] + [(i, f'{i}-sinf') for i in range(1, 12)],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Sinf',
    )
    item_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Barcha turlar')] + LibraryItem.ITEM_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tur',
    )
