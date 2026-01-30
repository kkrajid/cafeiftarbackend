from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows login with email instead of username.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate using email address.
        The 'username' parameter receives the email from the login form.
        """
        email = kwargs.get('email') or username
        
        if email is None or password is None:
            return None
        
        try:
            # Try to find user by email (case-insensitive)
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce timing attacks
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # If multiple users have same email, get the first one
            user = User.objects.filter(email__iexact=email).first()
        
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
