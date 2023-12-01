from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def gen_token(user: User):
    token = RefreshToken.for_user(user)
    # Add custom claims
    token["email"] = user.email
    token["user_id"] = str(user.id)
    token["user_type"] = user.user_type
    token['full_name'] = user.full_name
    try:
        token['profile_image'] = user.profile_image.url
    except:
        token['profile_image'] = ''


    return token


def update_login(refresh):
    data = dict()
    data["refresh"] = str(refresh)
    data["access"] = str(refresh.access_token)

    return data
