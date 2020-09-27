from datetime import datetime
from os import environ
from secrets import token_urlsafe


class Confirmable(object):
    def generate_confirmation_link(self):
        token = self.generate_confirmation_token()
        client_url = environ.get('CLIENT_URL')
        endpoint = '/confirm_account'
        query = f'?token={token}'
        return f'{client_url}{endpoint}{query}'

    def generate_confirmation_token(self):
        token = token_urlsafe(10)

        if self.confirmation_token:
            return self.confirmation_token
        self.confirmation_token = token
        self.save()
        return token

    def confirm_user(self):
        if self.confirmed_at is not None or self.confirmed:
            return False
        self.confirmed_at = datetime.now()
        self.confirmed = True
        self.save()
        return True

    def valid_confirmation_token(self, token):
        if self.confirmation_token is None:
            return False
        return self.confirmation_token == token
