import time
from datetime import datetime

from flask.globals import current_app
from flask_jwt_extended.config import config
from flask_jwt_extended.utils import get_csrf_token


def set_access_cookies(response, encoded_access_token, max_age=None, legacy=False):
    """
    Modifiy a Flask Response to set a cookie containing the access JWT.
    Also sets the corresponding CSRF cookies if ``JWT_CSRF_IN_COOKIES`` is ``True``
    (see :ref:`Configuration Options`)
    :param response:
        A Flask Response object.
    :param encoded_access_token:
        The encoded access token to set in the cookies.
    :param max_age:
        The max age of the cookie. If this is None, it will use the
        ``JWT_SESSION_COOKIE`` option (see :ref:`Configuration Options`). Otherwise,
        it will use this as the cookies ``max-age`` and the JWT_SESSION_COOKIE option
        will be ignored. Values should be the number of seconds (as an integer).
    """
    cookie_expiration_time = datetime.now() + config.access_expires
    microsecond_length = len(str(cookie_expiration_time.microsecond))

    if microsecond_length < 6:
        microsecond_format = '0'*(6-microsecond_length)+str(cookie_expiration_time.microsecond)
    else:
        microsecond_format = str(cookie_expiration_time.microsecond)

    cookie_expiration_time_struct = time.strptime(
        str(cookie_expiration_time), '%Y-%m-%d %H:%M:%S.{}'.format(microsecond_format))

    if legacy:
        response.set_cookie(
            current_app.name,
            config.access_cookie_name,
            value=encoded_access_token,
            max_age=max_age or config.cookie_max_age,
            expires=cookie_expiration_time_struct,
            path=config.access_cookie_path,
            domain=config.cookie_domain,
            secure=config.cookie_secure,
            httponly=True,
            samesite=config.cookie_samesite
        )
        if config.csrf_protect and config.csrf_in_cookies:
            response.set_cookie(
                current_app.name,
                config.access_csrf_cookie_name,
                value=get_csrf_token(encoded_access_token),
                max_age=max_age or config.cookie_max_age,
                expires=cookie_expiration_time_struct,
                path=config.access_csrf_cookie_path,
                domain=config.cookie_domain,
                secure=config.cookie_secure,
                httponly=False,
                samesite=config.cookie_samesite
            )
    else:
        response.set_cookie(
            config.access_cookie_name,
            value=encoded_access_token,
            max_age=max_age or config.cookie_max_age,
            secure=config.cookie_secure,
            httponly=True,
            domain=config.cookie_domain,
            path=config.access_cookie_path,
            samesite=config.cookie_samesite,
        )
        if config.csrf_protect and config.csrf_in_cookies:
            response.set_cookie(
                config.access_csrf_cookie_name,
                value=get_csrf_token(encoded_access_token),
                max_age=max_age or config.cookie_max_age,
                secure=config.cookie_secure,
                httponly=False,
                domain=config.cookie_domain,
                path=config.access_csrf_cookie_path,
                samesite=config.cookie_samesite,
            )


def set_refresh_cookies(response, encoded_refresh_token, max_age=None, legacy=False):
    """
    Modifiy a Flask Response to set a cookie containing the refresh JWT.
    Also sets the corresponding CSRF cookies if ``JWT_CSRF_IN_COOKIES`` is ``True``
    (see :ref:`Configuration Options`)
    :param response:
        A Flask Response object.
    :param encoded_refresh_token:
        The encoded refresh token to set in the cookies.
    :param max_age:
        The max age of the cookie. If this is None, it will use the
        ``JWT_SESSION_COOKIE`` option (see :ref:`Configuration Options`). Otherwise,
        it will use this as the cookies ``max-age`` and the JWT_SESSION_COOKIE option
        will be ignored. Values should be the number of seconds (as an integer).
    # """
    cookie_expiration_time = datetime.now() + config.refresh_expires
    microsecond_length = len(str(cookie_expiration_time.microsecond))

    if microsecond_length < 6:
        microsecond_format = '0'*(6-microsecond_length)+str(cookie_expiration_time.microsecond)
    else:
        microsecond_format = str(cookie_expiration_time.microsecond)

    cookie_expiration_time_struct = time.strptime(
        str(cookie_expiration_time), '%Y-%m-%d %H:%M:%S.{}'.format(microsecond_format))

    if legacy:
        response.set_cookie(
            current_app.name,
            config.refresh_cookie_name,
            value=encoded_refresh_token,
            max_age=max_age or config.cookie_max_age,
            expires=cookie_expiration_time_struct,
            path=config.refresh_cookie_path,
            domain=config.cookie_domain,
            secure=config.cookie_secure,
            httponly=True,
            samesite=config.cookie_samesite,
        )

        if config.csrf_protect and config.csrf_in_cookies:
            response.set_cookie(
                current_app.name,
                config.refresh_csrf_cookie_name,
                value=get_csrf_token(encoded_refresh_token),
                max_age=max_age or config.cookie_max_age,
                expires=cookie_expiration_time_struct,
                path=config.refresh_csrf_cookie_path,
                domain=config.cookie_domain,
                secure=config.cookie_secure,
                httponly=False,
                samesite=config.cookie_samesite,
            )
    else:
        response.set_cookie(
            config.refresh_cookie_name,
            value=encoded_refresh_token,
            max_age=max_age or config.cookie_max_age,
            secure=config.cookie_secure,
            httponly=True,
            domain=config.cookie_domain,
            path=config.refresh_cookie_path,
            samesite=config.cookie_samesite,
        )

        if config.csrf_protect and config.csrf_in_cookies:
            response.set_cookie(
                config.refresh_csrf_cookie_name,
                value=get_csrf_token(encoded_refresh_token),
                max_age=max_age or config.cookie_max_age,
                secure=config.cookie_secure,
                httponly=False,
                domain=config.cookie_domain,
                path=config.refresh_csrf_cookie_path,
                samesite=config.cookie_samesite,
            )
