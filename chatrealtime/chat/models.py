from django.contrib.auth.models import User
from django.db import models

class Chat(models.Model):

    cliente = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='sender_messages')
    empresa = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='receiver_messages')
    msg = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    enviado = models.BooleanField(null=False,default=False)

    def __str__(self):
        return '{} to {}'.format(self.cliente.username, self.empresa.username)