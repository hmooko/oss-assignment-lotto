from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import ManualTicketForm, SignUpForm, create_auto_ticket
from .models import LottoResult, LottoRound, LottoTicket


class HomeView(generic.TemplateView):
    template_name = "lotto/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_round"] = LottoRound.objects.filter(is_drawn=False).order_by("round_number").first()
        context["latest_draw"] = LottoRound.objects.filter(is_drawn=True).first()
        return context


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("lotto:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class BuyTicketView(LoginRequiredMixin, generic.FormView):
    form_class = ManualTicketForm
    template_name = "lotto/buy_ticket.html"
    success_url = reverse_lazy("lotto:ticket_list")

    def dispatch(self, request, *args, **kwargs):
        self.current_round = LottoRound.objects.filter(is_drawn=False).order_by("round_number").first()
        if self.current_round is None:
            messages.error(request, "구매 가능한 회차가 없습니다.")
            return redirect("lotto:home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_round"] = self.current_round
        return context

    def form_valid(self, form):
        LottoTicket.objects.create(
            user=self.request.user,
            round=self.current_round,
            numbers=form.cleaned_data["numbers"],
            purchase_type=LottoTicket.MANUAL,
        )
        messages.success(self.request, "수동 복권 구매가 완료되었습니다.")
        return super().form_valid(form)


@login_required
@require_POST
def buy_auto_ticket(request):
    current_round = LottoRound.objects.filter(is_drawn=False).order_by("round_number").first()
    if current_round is None:
        messages.error(request, "구매 가능한 회차가 없습니다.")
        return redirect("lotto:home")
    ticket = create_auto_ticket(request.user, current_round)
    messages.success(request, f"자동 복권 구매 완료: {ticket.numbers}")
    return redirect("lotto:ticket_list")


class TicketListView(LoginRequiredMixin, generic.ListView):
    model = LottoTicket
    template_name = "lotto/ticket_list.html"
    context_object_name = "tickets"

    def get_queryset(self):
        return LottoTicket.objects.filter(user=self.request.user).select_related("round")


class ResultListView(LoginRequiredMixin, generic.ListView):
    model = LottoResult
    template_name = "lotto/result_list.html"
    context_object_name = "results"

    def get_queryset(self):
        return LottoResult.objects.filter(ticket__user=self.request.user).select_related("ticket", "ticket__round")


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class ManagerDashboardView(LoginRequiredMixin, StaffRequiredMixin, generic.TemplateView):
    template_name = "lotto/manager_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rounds"] = LottoRound.objects.all()
        context["tickets"] = LottoTicket.objects.select_related("user", "round")[:50]
        context["results"] = LottoResult.objects.select_related("ticket", "ticket__user", "ticket__round")[:50]
        return context


def is_staff(user):
    return user.is_staff


@login_required
@user_passes_test(is_staff)
@require_POST
def draw_round(request, pk):
    lotto_round = get_object_or_404(LottoRound, pk=pk)
    try:
        lotto_round.draw()
        messages.success(request, f"{lotto_round.round_number}회차 추첨이 완료되었습니다.")
    except Exception as exc:
        messages.error(request, str(exc))
    return redirect("lotto:manager_dashboard")
