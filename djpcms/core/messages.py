import logging

MESSAGE_KEY = 'request-messanges'

__all__ = (
    'add_message',
    'get_messages',
    'get_level',
    'set_level',
    'debug', 'info', 'warning', 'error',
)


class MessageFailure(Exception):
    pass


def add_message(request, level, message, extra_tags=''):
    """Add a message to the request using the 'messages' app."""
    if hasattr(request,'session'):
        session = request.session
        if MESSAGE_KEY in session:
            messages = session[MESSAGE_KEY]
        else:
            messages = {}
        if not level in messages:
            messages[level] = []
        messages[level].append(message)
        session[MESSAGE_KEY] = messages


def get_messages(request):
    """
    Returns the message storage on the request if it exists, otherwise returns
    user.message_set.all() as the old auth context processor did.
    """
    if hasattr(request,'session'):
        if MESSAGE_KEY in request.session:
            msg = request.session[MESSAGE_KEY]
            del request.session[MESSAGE_KEY]
            return msg
    

def get_level(request,level):
    messanges = get_messages(request)
    if not level in messanges:
        messanges[level] = []
    return messanges[level]


def debug(request, message, extra_tags=''):
    """
    Adds a message with the ``DEBUG`` level.
    """
    add_message(request, logging.DEBUG, message, extra_tags=extra_tags)


def info(request, message, extra_tags=''):
    """
    Adds a message with the ``INFO`` level.
    """
    add_message(request, logging.INFO, message, extra_tags=extra_tags)


def warning(request, message, extra_tags=''):
    """
    Adds a message with the ``WARNING`` level.
    """
    add_message(request, logging.WARNING, message, extra_tags=extra_tags)


def error(request, message, extra_tags=''):
    """
    Adds a message with the ``ERROR`` level.
    """
    add_message(request, logging.ERROR, message, extra_tags=extra_tags)

