from datetime import datetime

from django.db import models

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
    def log(level, msg, print_stdout=True):
        """
        Log a message into the database
        :param print_stdout: print to stdout
        :param level: level of the log
        :param msg: message being logged
        """
        time = datetime.now()
        entry = LogEntry(message=msg, level=level, datetime=time)
        if print_stdout:
            print('%s: [%s] %s' % (entry.datetime.strftime("%Y-%m-%d %H:%M"), entry.get_level_display(), entry.message))
        entry.save()

    @staticmethod
    def error(msg, print_stdout=True):
        """
        Log an error
        :param print_stdout:
        :param msg: message to log
        """
        Logging.log(LogLevel.Error, msg, print_stdout=print_stdout)

    @staticmethod
    def warning(msg, print_stdout=True):
        """
        Log a warning
        :param print_stdout:
        :param msg: message to log
        """
        Logging.log(LogLevel.Warning, msg, print_stdout=print_stdout)

    @staticmethod
    def info(msg, print_stdout=True):
        """
        Log info
        :param print_stdout:
        :param msg: message to log
        """
        Logging.log(LogLevel.Info, msg, print_stdout=print_stdout)
