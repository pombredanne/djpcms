# Uniforms Layout is the Default layout
from uuid import uuid4

from djpcms import FormException, ValidationError

__all__ = ['FormException',
           'generate_prefix',
           'get_ajax_action',
           'get_ajax_action_value',
           'SEARCH_STRING',
           'SAVE_KEY',
           'CANCEL_KEY',
           'SAVE_AND_CONTINUE_KEY',
           'SAVE_AS_NEW_KEY',
           'PREFIX_KEY',
           'REFERER_KEY',
           'AJAX',
           'NOBUTTON',
           'BUTTON']


# some useful hidden keys
SEARCH_STRING = 'sSearch'
SAVE_KEY = '_save'
CANCEL_KEY = '_cancel'
SAVE_AND_CONTINUE_KEY = '_save_and_continue'
SAVE_AS_NEW_KEY = '_save_as_new'
PREFIX_KEY = '__prefixed__'
REFERER_KEY = '__referer__'
AJAX_ACTION_KEY = 'xhr'
AJAX = 'ajax'
BUTTON = 'button'
NOBUTTON = 'nobutton'


def generate_prefix():
    return str(uuid4())[:8]


class NoData(object):
    def __repr__(self):
        return '<NoData>'
    __str__ = __repr__


def get_ajax_action(data):
    action = None
    action = data.get(AJAX_ACTION_KEY, None)
    if action:
        prefix = data.get(PREFIX_KEY,None)
        if prefix and prefix in action:
            action = action[len(prefix):]
    return action


def get_ajax_action_value(action, data):
    prefix = data.get(PREFIX_KEY,None)
    if prefix:
        action = prefix + action
    return data.get(action)
    


nodata = NoData()
