from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic.base import TemplateView

from chat.models import Chat


class HomeView(LoginRequiredMixin, TemplateView):

    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Lista todos os usuários para bate-papo. Exceto eu.
        context['users'] = User.objects.exclude(id=self.request.user.id)\
                                       .values('username')
        return context


class ChatView(LoginRequiredMixin, TemplateView):

    template_name = 'chat.html'

    def dispatch(self, request, **kwargs):
        #Pega o user com quem estamos conversando, se não houver, mostra o erro 404.
        receiver_username = kwargs['chatname'].replace(
            request.user.username, '').replace('-', '')
        kwargs['empresa'] = get_object_or_404(User, username=receiver_username)
        return super().dispatch(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa'] = kwargs['empresa']
        return context


class ChatAPIView(View):

    def get(self, request, chatname):
        #Pega dois usuários com base no nome do bate-papo.
        users = User.objects.filter(username__in=chatname.split('-'))
        #Filtra mensagens entre esses dois usuários.
        result = Chat.objects.filter(
            Q(cliente=users[0], empresa=users[1]) | Q(cliente=users[1], empresa=users[0])
        ).annotate(
            username=F('cliente__username'), message=F('msg'),
        ).order_by('created_at').values('username', 'message', 'created_at')

        return JsonResponse(list(result), safe=False)

