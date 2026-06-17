import datetime

from django import forms
from django.core.exceptions import ValidationError

from .models import Reservation, Review

class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(
        help_text="Enter a date between now and 4 weeks (default 3)."
    )

    def clean_renewal_date(self):
        data = self.cleaned_data["renewal_date"]

        if data < datetime.date.today():
            raise ValidationError("Invalid date - renewal in past")

        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError("Invalid date - renewal more than 4 weeks ahead")

        return data
    
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["reserved_date"]

    def clean_reserved_date(self):
        data = self.cleaned_data["reserved_date"]

        if data < datetime.date.today():
            raise ValidationError("Invalid date - reservation in past")

        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError("Invalid date - reservation more than 4 weeks ahead")

        return data


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]