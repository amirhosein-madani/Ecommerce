from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.core.cache import cache
from django.contrib import messages
from website.messages import ContactUsMessages, NewsletterMessages
from website.models import Newsletter
from website.forms import ContactUsForm, NewsletterForm

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


class ContactView(FormView):
    template_name = "website/contact.html"
    form_class = ContactUsForm
    success_url = reverse_lazy("website:index")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        cache_key = f"contact_{email}"

        if cache.get(cache_key):
            messages.warning(self.request, ContactUsMessages.RATE_LIMIT)
            return self.form_invalid(form)

        cache.set(cache_key, True, timeout=120)
        form.save()
        messages.success(self.request, ContactUsMessages.SUCCESS)
        return super().form_valid(form)


class AboutView(TemplateView):
    template_name = "website/about.html"
