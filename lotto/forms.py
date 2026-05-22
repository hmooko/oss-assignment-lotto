from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import LottoTicket
from .services import generate_lotto_numbers, validate_lotto_numbers


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class ManualTicketForm(forms.Form):
    number1 = forms.IntegerField(min_value=1, max_value=45, label="번호 1")
    number2 = forms.IntegerField(min_value=1, max_value=45, label="번호 2")
    number3 = forms.IntegerField(min_value=1, max_value=45, label="번호 3")
    number4 = forms.IntegerField(min_value=1, max_value=45, label="번호 4")
    number5 = forms.IntegerField(min_value=1, max_value=45, label="번호 5")
    number6 = forms.IntegerField(min_value=1, max_value=45, label="번호 6")

    def clean(self):
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data
        numbers = [cleaned_data[f"number{index}"] for index in range(1, 7)]
        try:
            cleaned_data["numbers"] = validate_lotto_numbers(numbers)
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc
        return cleaned_data


def create_auto_ticket(user, lotto_round):
    return LottoTicket.objects.create(
        user=user,
        round=lotto_round,
        numbers=generate_lotto_numbers(),
        purchase_type=LottoTicket.AUTO,
    )
