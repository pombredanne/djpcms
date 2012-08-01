from inspect import isclass

from .exceptions import InvalidForm

NEXT_KEY = 'next-url'

__all__ = ['SubmitMiddleware', 'Referrer', 'NEXT_KEY']


class SubmitMiddleware(object):

    def extra_form_data(self, request):
        raise StopIteration()

    def check(self, request, data):
        pass


class SubmitDataMiddleware(object):

    def __init__(self):
        self._middleware = []

    def extra_form_data(self, request):
        '''Generator of name/value pairs for inputs to add to a form.'''
        for middleware in self._middleware:
            for name, value in middleware.extra_form_data(request):
                yield name, value

    def check(self, request, data):
        for middleware in self._middleware:
            middleware.check(request, data)

    def add(self, middleware):
        if isclass(middleware):
            middleware = middleware()
        self._middleware.append(middleware)


class Referrer(SubmitMiddleware):

    def extra_form_data(self, request):
        yield '__REFERRER__', request.get_full_path(request.path)

    def check(self, request, data):
        referrer = data.pop('__REFERRER__', None)
        if referrer:
            if NEXT_KEY not in data:
                data[NEXT_KEY] = referrer
        else:
            raise InvalidForm('referrer not available.')

