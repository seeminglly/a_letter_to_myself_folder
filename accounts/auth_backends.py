from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(f"Trying to authenticate username={username}")
        username = username or kwargs.get('username')
        if username is None or password is None:
            print("Missing username or password")
            return None
        try:
            user = User.objects.get(username=username)
            print(f"Found user: {user}")
            if user.check_password(password):
                print("Password check passed")
                if self.user_can_authenticate(user):
                    print("User can authenticate")
                    return user
                else:
                    print("User cannot authenticate")
            else:
                print("Password check failed")
        except User.DoesNotExist:
            print("User does not exist")
        return None
