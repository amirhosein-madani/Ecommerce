from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from accounts.models import UserType


class DashboardHomeView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if request.user.user_type == UserType.CUSTOMER:
            return redirect("dashboard:customer:home")

        if request.user.user_type == UserType.ADMIN:
            return redirect("dashboard:admin:home")

        return redirect("login")
