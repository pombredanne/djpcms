from .models import User
from .managers import UNUSABLE_PASSWORD


class ModelBackend(object):
    """
    Authenticates against djpcms.contrib.sessions.models.User.
    """
    supports_object_permissions = False
    supports_anonymous_user = True
    supports_inactive_user = True

    # TODO: Model, login attribute name and password attribute name should be
    # configurable.
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


