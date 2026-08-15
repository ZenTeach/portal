"""Password hashing facade.

Replicates the subset of :mod:`flask_bcrypt` used by the server without
requiring a Flask application object, so the same model layer runs under both
the legacy Flask app and the FastAPI app.

Behavior matches ``flask_bcrypt`` exactly:

* ``generate_password_hash`` returns *bytes* (callers ``.decode("utf-8")``).
* ``check_password_hash`` compares in constant time and returns ``bool``.
"""

import bcrypt as _bcrypt


class BcryptFacade:
    def __init__(self, app=None):
        self._log_rounds = 12
        self._prefix = "2b"
        self._handle_long_passwords = False
        if app is not None:
            self.init_app(app)

    def init_app(self, app=None):
        if app is not None:
            self._log_rounds = app.config.get("BCRYPT_LOG_ROUNDS", 12)
            self._prefix = app.config.get("BCRYPT_HASH_PREFIX", "2b")
            self._handle_long_passwords = app.config.get(
                "BCRYPT_HANDLE_LONG_PASSWORDS", False
            )

    def _unicode_to_bytes(self, value):
        if isinstance(value, str):
            return value.encode("utf-8")
        return value

    def generate_password_hash(self, password, rounds=None):
        if not password:
            raise ValueError("Password must be non-empty.")

        if rounds is None:
            rounds = self._log_rounds

        password = self._unicode_to_bytes(password)
        prefix = self._unicode_to_bytes(self._prefix)

        if self._handle_long_passwords:
            import hashlib

            password = hashlib.sha256(password).hexdigest().encode("utf-8")

        salt = _bcrypt.gensalt(rounds=rounds, prefix=prefix)
        return _bcrypt.hashpw(password, salt)

    def check_password_hash(self, pw_hash, password):
        return _bcrypt.checkpw(
            self._unicode_to_bytes(password), self._unicode_to_bytes(pw_hash)
        )


bcrypt = BcryptFacade()
"""Shared password hashing instance."""
