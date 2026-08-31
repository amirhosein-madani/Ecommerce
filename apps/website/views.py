from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.core.cache import cache
from django.contrib import messages
from website.messages import TicketMessages, NewsletterMessages
from website.models.generals import Newsletter
from website.models.tickets import TicketMessage

from website.forms import NewsletterForm, TicketForm

from accounts.mixins import LoginRequiredMixin

# Create your views here.


class IndexView(FormView):

    form_class = NewsletterForm
    success_url = reverse_lazy("website:index")
    template_name = "website/index.html"

    def form_valid(self, form):

        if Newsletter.objects.filter(email=form.cleaned_data.get("email")).exists():
            messages.error(self.request, NewsletterMessages.ALREADY_SUBSCRIBED)
            return super().form_valid(form)

        Newsletter.objects.create(email=form.cleaned_data.get("email"))
        messages.success(self.request, NewsletterMessages.SUCCESS)
        return super().form_valid(form)


class TicketCreateView(LoginRequiredMixin, FormView):
    template_name = "website/ticket.html"
    form_class = TicketForm
    success_url = reverse_lazy("website:index")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        cache_key = f"ticket_create_{self.request.user.id}"

        if cache.get(cache_key):
            messages.warning(self.request, TicketMessages.RATE_LIMIT)
            return self.form_invalid(form)

        cache.set(cache_key, True, timeout=120)

        ticket = form.save(commit=False)
        ticket.user = self.request.user
        ticket.save()

        TicketMessage.objects.create(
            ticket=ticket,
            sender=self.request.user,
            message=form.cleaned_data["message"],
            is_staff_reply=False,
        )

        messages.success(self.request, TicketMessages.SUCCESS)

        return super().form_valid(form)


class AboutView(TemplateView):
    template_name = "website/about.html"
