import json

from asgiref.sync import async_to_sync

from django.contrib.auth.models import User
from channels.generic.websocket import WebsocketConsumer
from django.core import mail

from chat.models import Chat


def send():
    emails = (
        ('Hey Man', "I'm The Dude! So that's what you call me.", 'jessicahelem.s@hotmail.com',
         ['jessihelem.santos@gmail.com']),

    )
    results = mail.send_mass_mail(emails)


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        """
        Join channel group by chatname.
        """
        self.group_name = 'chat_{0}'.format(self.scope['url_route']['kwargs']['chatname'])

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name,
        )

        self.accept()

    def disconnect(self, close_code):
        """
        Leave channel by group name.
        """
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data):
        """
       Recebe a mensagem do websocket e envia para o grupo.
        """
        text_data_json = json.loads(text_data)
        username = text_data_json['username']
        message = text_data_json['message']

        # armazena a mensagem.
        empresa = User.objects.get(
            username=self.group_name.replace('chat_', '')
                .replace(self.scope['user'].username, '')
                .replace('-', ''))
        Chat(cliente=self.scope['user'], empresa=empresa, msg=message, enviado=True).save()

        client = User.objects.filter(username=self.scope['user'])
        empres = User.objects.filter(username=empresa)

        t1 = Chat.objects.filter(cliente=client[0]).filter(empresa=empres[0])

        print(t1)

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'chat_message',
                'username': username,
                'message': message,
            }
        )

    # @task(bind=True)
    # def task(self):
    #
    #     crontab(hour=12, minute=46, day_of_week=1)
    #     send()

    def chat_message(self, event):
        """
        Recebe a mensagem do grupo de canal e envia para websocket.
        """
        self.send(text_data=json.dumps({
            'username': event['username'],
            'message': event['message'],
        }))
