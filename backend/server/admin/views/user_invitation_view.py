from .base_view import BaseView


class UserInvitationView(BaseView):
    can_create = False
    can_edit = False
    column_exclude_list = ["invite_sent_at"]
