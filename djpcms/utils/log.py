import logging
import sys

# Make sure a NullHandler and dictConfig are available
# They were added in Python 2.7/3.2
try:     # pragma nocover
    from logging.config import dictConfig
    from logging import NullHandler
except ImportError:     # pragma nocover
    from .fallbacks._dictconfig import dictConfig
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
        

# We can't log memory info without psutil
try:         # pragma nocover
    from psutil import Process
    from os import getpid
    _p = Process(getpid())
except:      # pragma nocover
    _p = None

def get_mem_rss():
    if _p:
        return _p.get_memory_info().rss/1024
    else:
        return 0.0
    
class ProcessInfoLogger(logging.Logger):
    """Custom logger that allows process information to be logged.
    Supported items:
        *:mem_rss: resident set size, in KB
    """ 
    def makeRecord(self, *args, **kwargs):
        rv = logging.Logger.makeRecord(self, *args, **kwargs)
        if _p:
            rv.mem_rss = get_mem_rss()
        return rv

logging.setLoggerClass(ProcessInfoLogger)
logger = logging.getLogger('djpcms')

if not logger.handlers:
    logger.addHandler(NullHandler())
        
        
class AdminEmailHandler(logging.Handler):
    """An exception log handler that emails log entries to site admins

    If the request is passed as the first argument to the log record,
    request data will be provided in the
    """
    def emit(self, record):
        import traceback
        from django.conf import settings
        from django.core import mail

        try:
            if sys.version_info < (2,5):
                # A nasty workaround required because Python 2.4's logging
                # module doesn't support passing in extra context.
                # For this handler, the only extra data we need is the
                # request, and that's in the top stack frame.
                request = record.exc_info[2].tb_frame.f_locals['request']
            else:
                request = record.request

            subject = '%s (%s IP): %s' % (
                record.levelname,
                (request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS and 'internal' or 'EXTERNAL'),
                request.path
            )
            request_repr = repr(request)
        except:
            subject = 'Error: Unknown URL'
            request_repr = "Request repr() unavailable"

        if record.exc_info:
            stack_trace = '\n'.join(traceback.format_exception(*record.exc_info))
        else:
            stack_trace = 'No stack trace available'

        message = "%s\n\n%s" % (stack_trace, request_repr)
        mail.mail_admins(subject, message, fail_silently=True)
