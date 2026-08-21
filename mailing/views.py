from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Client, Message, Mailing, MailingAttempt
from .forms import MailingForm
from .services import send_mailing
from django.views.decorators.vary import vary_on_cookie


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

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user

        if user.groups.filter(name='Менеджер').exists():
            messages.error(request, 'Менеджер не может редактировать данные.')
            return redirect('mailing:client_list')

        if obj.owner != user:
            messages.error(request, 'Вы не можете редактировать этот объект.')
            return redirect('mailing:client_list')

        return super().dispatch(request, *args, **kwargs)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'mailing/client_confirm_delete.html'
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return Client.objects.all()
        return Client.objects.filter(owner=user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user

        if user.groups.filter(name='Менеджер').exists():
            messages.error(request, 'Менеджер не может удалять данные.')
            return redirect('mailing:client_list')

        if obj.owner != user:
            messages.error(request, 'Вы не можете удалить этот объект.')
            return redirect('mailing:client_list')

        return super().dispatch(request, *args, **kwargs)


# === Сообщения ===
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return Message.objects.all()
        return Message.objects.filter(owner=user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'mailing/message_detail.html'
    context_object_name = 'message'


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


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
        queryset = Mailing.objects.filter(owner=user) if not user.groups.filter(
            name='Менеджер').exists() else Mailing.objects.all()

        # Обновляем статус для всех рассылок
        for mailing in queryset:
            mailing.update_status()

        return queryset


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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user

        if user.groups.filter(name='Менеджер').exists():
            messages.error(request, 'Менеджер не может редактировать данные.')
            return redirect('mailing:mailing_list')

        if obj.owner != user:
            messages.error(request, 'Вы не можете редактировать этот объект.')
            return redirect('mailing:mailing_list')

        return super().dispatch(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user

        if user.groups.filter(name='Менеджер').exists():
            messages.error(request, 'Менеджер не может редактировать данные.')
            return redirect('mailing:mailing_list')

        if obj.owner != user:
            messages.error(request, 'Вы не можете редактировать этот объект.')
            return redirect('mailing:mailing_list')

        return super().dispatch(request, *args, **kwargs)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user

        if user.groups.filter(name='Менеджер').exists():
            messages.error(request, 'Менеджер не может удалять данные.')
            return redirect('mailing:mailing_list')

        if obj.owner != user:
            messages.error(request, 'Вы не можете удалить этот объект.')
            return redirect('mailing:mailing_list')

        return super().dispatch(request, *args, **kwargs)


# === Отправка ===
def send_mailing_view(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    # Проверка: только владелец или менеджер может отправлять
    user = request.user
    if mailing.owner != user and not user.groups.filter(name='Менеджер').exists():
        messages.error(request, 'У вас нет прав на отправку этой рассылки.')
        return redirect('mailing:mailing_list')

    send_mailing(mailing)
    messages.success(request, 'Рассылка отправлена!')
    return redirect('mailing:mailing_detail', pk=pk)


# === Главная ===
class HomeView(TemplateView):
    template_name = 'mailing/home.html'

    @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(30))
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        response['Cache-Control'] = 'public, max-age=30, stale-while-revalidate=10'
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        if user.is_authenticated:
            # Для авторизованного — только свои данные
            user_mailings = Mailing.objects.filter(owner=user)
            for mailing in user_mailings:
                mailing.update_status()

            context['total_mailings'] = user_mailings.count()
            context['active_mailings'] = user_mailings.filter(status='started').count()
            context['total_clients'] = Client.objects.filter(owner=user).count()
            context['user_mailings'] = user_mailings.count()
            context['user_clients'] = Client.objects.filter(owner=user).count()
            context['user_attempts'] = MailingAttempt.objects.filter(mailing__owner=user).count()
            context['user_success'] = MailingAttempt.objects.filter(
                mailing__owner=user,
                status='success'
            ).count()
        else:
            # Для неавторизованного — общая статистика сервиса
            all_mailings = Mailing.objects.all()
            for mailing in all_mailings:
                mailing.update_status()

            context['total_mailings'] = all_mailings.count()
            context['active_mailings'] = all_mailings.filter(status='started').count()
            context['total_clients'] = Client.objects.count()
            context['user_mailings'] = 0
            context['user_clients'] = 0
            context['user_attempts'] = 0
            context['user_success'] = 0

        return context

