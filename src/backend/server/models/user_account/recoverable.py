from datetime import datetime
from os import environ
from secrets import token_hex


class Recoverable(object):

    def get_reset_link(self):
        client_url = environ.get('CLIENT_URL')
        endpoint = '/change_password'
        token = self.get_reset_token()
        query = f'?token={token}&email={self.email}'
        return f'{client_url}{endpoint}{query}'

    def get_reset_token(self):
        token = token_hex(16)
        self.recovery_token = token
        self.save()
        return token

    def reset_account(self, token, new_password_hash):
        if self.valid_recovery_token(token):
            self.update_password(new_password_hash)
            self.update_recovery_date()
            self.recovery_token = None
            self.save()
            return True

        return False

    def valid_recovery_token(self, token):
        if self.recovery_token is not None or self.recovery_token == token:
            return True

        return False

    def update_recovery_date(self):
        self.recovered_at = datetime.now()
        self.save()

    def update_password(self, new_password):
        self.password = new_password
        self.save()
