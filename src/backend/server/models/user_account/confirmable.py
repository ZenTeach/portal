from datetime import datetime
from secrets import token_urlsafe


class Confirmable(object):
    def generate_confirmation_link(self):
        token = self.generate_confirmation_token()
        return token

    def generate_confirmation_token(self):
        token = token_urlsafe(10)

        if self.confirmation_token:
            return self.confirmation_token
        self.confirmation_token = token
        self.save()
        return token

    def confirm_user(self):
        if self.confirmed_at is not None:
            return False
        self.confirmed_at = datetime.now()
        self.save()
        return True

    def valid_token(self, token):
        if self.confirmation_token is None:
            return False
        return self.confirmation_token == token
