from django import forms
from django.utils import timezone
from .models import Mailing


class MailingForm(forms.ModelForm):
    start_date = forms.DateField(
        label='Дата начала',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    start_time = forms.TimeField(
        label='Время начала',
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
    )
    end_date = forms.DateField(
        label='Дата окончания',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    end_time = forms.TimeField(
        label='Время окончания',
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
    )

    class Meta:
        model = Mailing
        fields = ['message', 'recipients']
        widgets = {
            'recipients': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            # Заполняем поля при редактировании
            self.fields['start_date'].initial = self.instance.start_time.date()
            self.fields['start_time'].initial = self.instance.start_time.time()
            self.fields['end_date'].initial = self.instance.end_time.date()
            self.fields['end_time'].initial = self.instance.end_time.time()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        start_time = cleaned_data.get('start_time')
        end_date = cleaned_data.get('end_date')
        end_time = cleaned_data.get('end_time')

        errors = []

        if start_date and start_time:
            start_datetime = timezone.make_aware(
                timezone.datetime.combine(start_date, start_time)
            )
            cleaned_data['start_time'] = start_datetime
        else:
            errors.append('Заполните дату и время начала')

        if end_date and end_time:
            end_datetime = timezone.make_aware(
                timezone.datetime.combine(end_date, end_time)
            )
            cleaned_data['end_time'] = end_datetime
        else:
            errors.append('Заполните дату и время окончания')

        if 'start_time' in cleaned_data:
            now = timezone.now()
            if cleaned_data['start_time'] < now:
                errors.append('Дата и время начала не могут быть в прошлом.')

        if 'start_time' in cleaned_data and 'end_time' in cleaned_data:
            if cleaned_data['start_time'] > cleaned_data['end_time']:
                errors.append('Дата начала должна быть раньше даты окончания.')

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.start_time = self.cleaned_data['start_time']
        instance.end_time = self.cleaned_data['end_time']
        if commit:
            instance.save()
            self.save_m2m()
        return instance