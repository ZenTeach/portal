from flask import current_app, jsonify


class LoggedInUserMixin(object):
    def __init__(self, email, psswd, type, client):
        self._email = email
        self._psswd = psswd
        self._login_endpoint = "api/v1/{}/login".format(type)
        self._logout_endpoint = "api/v1/{}/logout".format(type)
        self.client = client

    def __enter__(self):
        self.client.post(
            self._login_endpoint,
            json=jsonify({"email": self._email, "password": self._psswd}),
        )
        current_app.test_request_context().push()
        return current_app.test_request_context()

    def __exit__(self):
        with current_app.test_request_context():
            self.client.post(self._logout_endpoint)
        current_app.test_request_context.pop()
        return

    def login_with_user(self, email, psswd, type):
        login_details = jsonify({"email": email, "password": psswd})
        url = "api/v1/{}/login".format(type)
        self.client.post(url, json=login_details)
        # return make_response(jsonify(response), 200)
