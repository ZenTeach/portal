import flask_admin as admin
from flask import current_app, redirect, request, session, url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_login import current_user, login_user, logout_user
from flask_wtf.csrf import _FlaskFormCSRF
from server import bcrypt
from server.models import Admin
from wtforms import fields, form, validators
from wtforms.meta import DefaultMeta

from .base_view import logger


class CustomSecureForm(SecureForm):
    class Meta(DefaultMeta):
        csrf_class = _FlaskFormCSRF
        csrf_context = session

        @property
        def csrf_secret(self):
            return current_app.\
                config.\
                get("WTF_CSRF_SECRET_KEY",
                    current_app.secret_key)

        @property
        def csrf_time_limit(self):
            return current_app.config.get("WTF_CSRF_TIME_LIMIT", 3600)


class BaseView(ModelView):
    can_export = True
    list_template = "admin/list.html"
    create_template = "admin/create.html"
    edit_template = "admin/edit.html"
    form_base_class = CustomSecureForm

    def is_accessible(self):
        return current_user.is_authenticated


class LoginForm(form.Form):
    email = fields.StringField(
        validators=[validators.DataRequired()], render_kw={"placeholder": "email"}
    )
    password = fields.PasswordField(
        validators=[validators.DataRequired()],
        render_kw={"placeholder": "password"}
    )

    def validate(self):
        return self.validate_login()

    def validate_login(self):
        user = self.get_user()

        if user is None:
            self.email.errors = "User not found"
            return False
        # we're comparing the plaintext pw with the the hash from the sdb
        if not bcrypt.check_password_hash(user.password, self.password.data.encode('utf-8')):
            self.password.errors = "Incorrect password"
            return False

        logger.info('Password accepted')

        return True

    def get_user(self):
        return Admin.query.filter_by(email=self.email.data).first()


class ZenteachAdminIndexView(admin.AdminIndexView):
    @admin.expose("/")
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for(".login_view"))
        return super(ZenteachAdminIndexView, self).index()

    @admin.expose("/login/", methods=("GET", "POST"))
    def login_view(self):
        form = LoginForm(request.form)
        if admin.helpers.validate_form_on_submit(form):
            user = form.get_user()
            login_user(user)

        if current_user.is_authenticated:
            return redirect(url_for(".index"))
        self._template_args["form"] = form
        return super(ZenteachAdminIndexView, self).index()

    @admin.expose("/logout/")
    def logout_view(self):
        logout_user()
        return redirect(url_for(".index"))
