import logging


__all__ = (
    'add_message',
    'get_messages',
    'get_level',
    'set_level',
    'debug', 'info', 'warning', 'error',
)


class MessageFailure(Exception):
    pass


def add_message(request, level, message, extra_tags='', fail_silently = False):
    """Add a message to the request using the 'messages' app."""
    if hasattr(request, '_messages'):
        return request._messages.add(level, message, extra_tags)


def get_messages(request):
    """
    Returns the message storage on the request if it exists, otherwise returns
    user.message_set.all() as the old auth context processor did.
    """
    if hasattr(request, '_messages'):
        return request._messages
    else:
        return []
    

def get_level(request):
    """
    Returns the minimum level of messages to be recorded.

    The default level is the ``MESSAGE_LEVEL`` setting. If this is not found,
    the ``INFO`` level is used.
    """
    if hasattr(request, '_messages'):
        storage = request._messages
        return storage.level


def get_level_tags():
    """
    Returns the message level tags.
    """
    level_tags = constants.DEFAULT_TAGS.copy()
    level_tags.update(getattr(settings, 'MESSAGE_TAGS', {}))
    return level_tags


def set_level(request, level):
    """
    Sets the minimum level of messages to be recorded, returning ``True`` if
    the level was recorded successfully.

    If set to ``None``, the default level will be used (see the ``get_level``
    method).
    """
    if not hasattr(request, '_messages'):
        return False
    request._messages.level = level
    return True


def debug(request, message, extra_tags='', fail_silently=False):
    """
    Adds a message with the ``DEBUG`` level.
    """
    add_message(request, logging.DEBUG, message, extra_tags=extra_tags,
                fail_silently=fail_silently)


def info(request, message, extra_tags='', fail_silently=False):
    """
    Adds a message with the ``INFO`` level.
    """
    add_message(request, logging.INFO, message, extra_tags=extra_tags,
                fail_silently=fail_silently)


def warning(request, message, extra_tags='', fail_silently=False):
    """
    Adds a message with the ``WARNING`` level.
    """
    add_message(request, logging.WARNING, message, extra_tags=extra_tags,
                fail_silently=fail_silently)


def error(request, message, extra_tags='', fail_silently=False):
    """
    Adds a message with the ``ERROR`` level.
    """
    add_message(request, logging.ERROR, message, extra_tags=extra_tags,
                fail_silently=fail_silently)

