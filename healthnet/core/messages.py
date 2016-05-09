from django.utils.html import linebreaks
from vendor.markdown2 import markdown

from django.db import models

from healthnet.core.enumfield import EnumField

MessageType = EnumField('Normal', 'Emergency', 'Reminder', 'Call to Action')


class Message(models.Model):
    """
    The model for a message
    """
    type = models.IntegerField(choices=MessageType.get_choices(), default=MessageType.Normal)
    sender = models.ForeignKey('User', related_name='sent_messages')
    recipient = models.ForeignKey('User', related_name='received_messages')
    text = models.TextField()
    previous_message = models.ForeignKey('Message', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    is_notification = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def get_html(self):
        """
        Get the HTML for a message while stripping
        excessive line breaks and converting markdown
        :return: The HTML for this message
        """
        return linebreaks(markdown(self.text.rstrip()).rstrip())

    def toggle_unread(self):
        """
        Toggle the messages read state
        :return: None
        """
        self.is_read = not self.is_read
        self.save()

    def get_read_status_str(self, invert=False):
        """
        Get a string stating whether or not the message is read
        :param invert: Get the opposite state
        :return: The string (read or unread)
        """
        if (self.is_read and not invert) or (invert and not self.is_read):
            return 'read'
        else:
            return 'unread'

    def get_read_status_str_inv(self):
        """
        Same as get_read_status_str but always inverted
        :return: The inverted string (read or unread)
        """
        return self.get_read_status_str(True)

    def get_previous_messages(self):
        """
        Get the messages that this message was a reply to
        :return: A list of messages in the order the where sent
        """
        messages = [self]
        message = self
        while message.previous_message is not None:
            messages += [message.previous_message]
            message = message.previous_message
        messages.reverse()
        return messages

    def reply(self, sender, recipient, msg):
        """
        Reply to the message
        :param sender: The user that sent the reply
        :param recipient: The user receiving the message
        :param msg: The message contents
        :return: The message that was sent
        """
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
        """
        Send a new message
        :param sender: The user sending the message
        :param recipient: The user receiving the message
        :param msg: The message contents
        :param msg_type: The type of the message
        :return: The message that was sent
        """
        message = Message.objects.create(sender=sender, recipient=recipient, text=msg, type=msg_type)
        message.save()
        return message