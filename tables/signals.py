from allauth.account.signals import user_logged_in
from django.contrib.sessions.models import Session
from django.dispatch import receiver

@receiver(user_logged_in)
def sync_user_to_session(request, user, **kwargs):
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["role"] = user.role

@receiver(user_logged_in)
def enforce_single_session(request, user, **kwargs):
    # 如果用户已经有旧 session，先踢掉
    if user.session_key:
        try:
            old_session = Session.objects.get(session_key=user.session_key)
            old_session.delete()
        except Session.DoesNotExist:
            pass

    # 把当前 session 记下来
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["role"] = user.role
    user.session_key = request.session.session_key
    user.save()