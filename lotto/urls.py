from django.urls import path

from . import views


app_name = "lotto"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("tickets/buy/", views.BuyTicketView.as_view(), name="buy_ticket"),
    path("tickets/auto/", views.buy_auto_ticket, name="buy_auto_ticket"),
    path("tickets/", views.TicketListView.as_view(), name="ticket_list"),
    path("results/", views.ResultListView.as_view(), name="result_list"),
    path("manager/", views.ManagerDashboardView.as_view(), name="manager_dashboard"),
    path("manager/rounds/<int:pk>/draw/", views.draw_round, name="draw_round"),
]
