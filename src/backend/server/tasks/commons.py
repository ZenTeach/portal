
from flask import render_template
from server import mail

DEFAULT_MAIL_TEMPLATE_DIR = "/mail"


def send_mail(msg):
    mail.send(msg)


def send_mail_with_html(msg, template_name, **kwargs):
    template_path = "/mail/{}".format(template_name)
    msg.html = render_template(template_path, **kwargs)
    mail.send(msg)
