from django.contrib.sessions.models import Session
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from tables.models import User 

class SingleSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and isinstance(request.user, User):
            current_session_key = request.session.session_key
            saved_session_key = request.user.session_key

            if saved_session_key and saved_session_key != current_session_key:
                Session.objects.filter(session_key=saved_session_key).delete()

            if saved_session_key != current_session_key:
                request.user.session_key = current_session_key
                request.user.save()


class EnforceSingleLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_id = request.session.get("user_id")
        session_key = request.session.session_key

        if user_id and session_key:
            try:
                user = User.objects.get(id=user_id)
                if user.session_key != session_key:
                    print("🚫 Session mismatch detected, logging out user")
                    request.session.flush()
                    return redirect("login")
            except User.DoesNotExist:
                request.session.flush()
                return redirect("login")

        return self.get_response(request)