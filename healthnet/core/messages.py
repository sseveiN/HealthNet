from django.db import models

from healthnet.core.enumfield import EnumField

MessageType = EnumField('Normal', 'Emergency', 'Reminder', 'Call to Action')


class Message(models.Model):
    type = models.IntegerField(choices=MessageType.get_choices(), default=MessageType.Normal)
    sender = models.ForeignKey('User', related_name='sent_messages')
    recipient = models.ForeignKey('User', related_name='received_messages')
    text = models.TextField()
    previous_message = models.ForeignKey('Message', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def toggle_unread(self):
        self.is_read = not self.is_read
        self.save()

    def get_read_status_str(self, invert=False):
        if self.is_read and not invert:
            return 'read'
        else:
            return 'unread'

    def get_read_status_str_inv(self):
        return self.get_read_status_str(True)

    def get_previous_messages(self):
        messages = [self]
        message = self
        while message.previous_message is not None:
            messages += [message.previous_message]
            message = message.previous_message
        messages.reverse()
        return messages

    def reply(self, sender, recipient, msg):
        message = Message.objects.create(sender=sender, recipient=recipient, text=msg)
        message.previous_message = self
        self.is_read = True
        self.save()
        message.save()
        return message

    def get_type_str(self):
        """
        Gets the type of the message
        :return: type of the message as a str
        """
        if self.type == 0:
            return 'Normal'
        if self.type == 1:
            return 'Emergency'
        if self.type == 2:
            return 'Reminder'
        if self.type == 3:
            return 'Call-to-Action'
        else:
            return 'Unknown'

    @staticmethod
    def send(sender, recipient, msg, msg_type=MessageType.Normal):
        message = Message.objects.create(sender=sender, recipient=recipient, text=msg, type=msg_type)
        message.save()
        return message
