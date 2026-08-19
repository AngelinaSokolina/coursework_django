from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from .models import Client, Message, Mailing, MailingAttempt
from .forms import MailingForm
from .services import send_mailing
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


# === Клиенты ===
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return Client.objects.all()
        return Client.objects.filter(owner=user)


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'mailing/client_detail.html'
    context_object_name = 'client'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return Client.objects.all()
        return Client.objects.filter(owner=user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ['email', 'full_name', 'comment']
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    fields = ['email', 'full_name', 'comment']
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return Client.objects.all()
        return Client.objects.filter(owner=user)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'mailing/client_confirm_delete.html'
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return Client.objects.all()
        return Client.objects.filter(owner=user)


# === Сообщения ===
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'mailing/message_detail.html'
    context_object_name = 'message'


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')


# === Рассылки ===
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)


# === Отправка ===
def send_mailing_view(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    send_mailing(mailing)
    return redirect('mailing:mailing_detail', pk=pk)


# === Главная ===
class HomeView(TemplateView):
    template_name = 'mailing/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Статистика для всех пользователей (главная)
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='started').count()
        context['total_clients'] = Client.objects.count()

        # Если пользователь авторизован — только его данные
        if self.request.user.is_authenticated:
            user = self.request.user
            context['user_mailings'] = Mailing.objects.filter(owner=user).count()
            context['user_clients'] = Client.objects.filter(owner=user).count()
            context['user_attempts'] = MailingAttempt.objects.filter(
                mailing__owner=user
            ).count()
            context['user_success'] = MailingAttempt.objects.filter(
                mailing__owner=user,
                status='success'
            ).count()
        else:
            context['user_mailings'] = 0
            context['user_clients'] = 0
            context['user_attempts'] = 0
            context['user_success'] = 0

        return context