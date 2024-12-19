from types import SimpleNamespace

from user.admin import UserAdmin
from user.models import User


def test__useradmin__github_url():
    admin = UserAdmin(User, None)
    user = SimpleNamespace()
    user.gh_username = None

    assert admin.github_url(user) == ''

    user.github_url = 'https://github.com/username'
    user.gh_username = 'username'

    assert (
        admin.github_url(user)
        == "<a href='https://github.com/username'>username</a>"
    )


def test__useradmin__tg_url():
    admin = UserAdmin(User, None)
    user = SimpleNamespace()
    user.tg_username = None

    assert admin.tg_url(user) == ''

    user.tg_url = 'https://t.me/username'
    user.tg_username = 'username'

    assert admin.tg_url(user) == "<a href='https://t.me/username'>username</a>"


def test__useradmin__email_url():
    admin = UserAdmin(User, None)
    user = SimpleNamespace()
    user.email = None

    assert admin.email_url(user) == ''

    user.email_url = 'mailto:username@mail.com'
    user.email = 'username@mail.com'

    assert (
        admin.email_url(user)
        == "<a href='mailto:username@mail.com'>username@mail.com</a>"
    )
