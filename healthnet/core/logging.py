from django.db import models

from datetime import datetime

from healthnet.core.enumfield import EnumField

LogLevel = EnumField('Info', 'Warning', 'Error')


class LogEntry(models.Model):
    """
    A log entry which is logged by the log, and created automatically through system interactions
    """
    datetime = models.DateTimeField()
    level = models.IntegerField(choices=LogLevel.get_choices(), default=LogLevel.Info)
    message = models.TextField()

    def get_level_str(self):
        """
        Gets the level of the log entry
        :return: level of the log entry
        """
        if self.level == 0:
            return 'Info'
        if self.level == 1:
            return 'Warning'
        if self.level == 2:
            return 'Error'
        else:
            return 'Unknown'


class Logging(object):
    """
    The log
    """
    @staticmethod
    def log(level, msg):
        """
        Log a message into the database
        :param level: level of the log
        :param msg: message being logged
        """
        time = datetime.now()
        entry = LogEntry(message=msg, level=level, datetime=time)
        print('%s: [%s] %s' % (entry.datetime.strftime("%Y-%m-%d %H:%M"), entry.get_level_display(), entry.message))
        entry.save()

    @staticmethod
    def error(msg):
        """
        Log an error
        :param msg: message to log
        """
        Logging.log(LogLevel.Error, msg)

    @staticmethod
    def warning(msg):
        """
        Log a warning
        :param msg: message to log
        """
        Logging.log(LogLevel.Warning, msg)

    @staticmethod
    def info(msg):
        """
        Log info
        :param msg: message to log
        """
        Logging.log(LogLevel.Info, msg)