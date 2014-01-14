from django.conf import settings
from django.contrib import auth
from datetime import timedelta, datetime


class AutoLogout:
    def process_request(self, request):
        if not request.user.is_authenticated():
            return
        try:
            if datetime.now() - datetime.strptime(request.session['last_activity'], '%Y-%m-%d %H:%M:%S') \
                    > timedelta(minutes=settings.AUTO_LOGOUT_DELAY):
                auth.logout(request)
                del request.session['last_activity']
            return
        except KeyError:
            pass
        request.session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')