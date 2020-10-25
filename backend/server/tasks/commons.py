
import os

from flask import render_template
from server import mail

DEFAULT_MAIL_TEMPLATE_DIR = "/mail"


def attach_sender(msg):
    if msg is None:
        raise Exception("Got an empty Message")

    if msg.sender is None:
        msg.sender = os.environ.get("DEFAULT_MAIL_SENDER")


def send_mail(msg):
    attach_sender(msg)
    mail.send(msg)


def send_mail_with_html(msg, template_name, **kwargs):
    attach_sender(msg)
    template_path = "/mail/{}".format(template_name)
    msg.html = render_template(template_path, **kwargs)
    mail.send(msg)
