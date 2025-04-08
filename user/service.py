from user.models import User


class UserService:
    def __init__(self, user):
        self.user = user

    def approve_or_reject(self, action):
        if action == 'approve':
            self.user.role = User.ADMIN
            self.user.is_staff = True

        self.user.is_admin_requested = False
        self.user.save()
