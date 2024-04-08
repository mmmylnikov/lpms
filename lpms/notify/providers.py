import urllib.request
import urllib.parse
import json
import ssl
from typing import Self

from config.settings import TELEGRAM_BOT_TOKEN
from user.models import User


class TelegramBot:
    token: str | None
    api_url: str | None
    ssl_context: ssl.SSLContext
    updates: list[dict] | None

    def __init__(self) -> None:
        self.set_token()
        self.set_api_url()
        self.ssl_context = ssl.SSLContext()

    def set_token(self) -> None:
        if not TELEGRAM_BOT_TOKEN:
            return None
        self.token = TELEGRAM_BOT_TOKEN

    def set_api_url(self) -> None:
        if not self.token:
            return None
        self.api_url = f'https://api.telegram.org/bot{self.token}/'

    def get_data_from_request(self,
                              endpoint: str,
                              kwargs: dict[str, str] | None = None) -> dict:

        url_path = f'{self.api_url}{endpoint}'
        if kwargs:
            params = urllib.parse.urlencode(kwargs)
            url_path += f'?{params}'
        with urllib.request.urlopen(
                url=url_path,
                context=self.ssl_context) as url:
            data = json.load(url)
            return data

    def get_updates(self) -> Self:
        updates = self.get_data_from_request('getUpdates')
        if updates['ok']:
            self.updates = updates['result']
        else:
            self.updates = None
        return self

    def get_last_users(self) -> list[str] | None:
        if not self.updates:
            return None
        users = set()
        for update in self.updates:
            message = update.get('message')
            if not message:
                continue
            users.add(message['from']['username'])
        return [user.lower() for user in users]

    def known_user(self, user: User) -> bool:
        self.get_updates()
        users = self.get_last_users()
        if not users:
            return False
        if not user.tg_username:
            return False
        if user.tg_username.lower() not in users:
            return False
        return True

    def get_user_chat_id(self, username: str) -> str | None:
        if not self.updates:
            return None
        username = username.lower()
        for update in self.updates:
            message = update.get('message')
            if not message:
                continue
            tg_username = message['from']['username'].lower()
            if username != tg_username:
                continue
            return str(message['chat']['id'])
        return None

    def send_message(self, chat_id: str, text: str) -> dict:
        return self.get_data_from_request('sendMessage', kwargs={
            'chat_id': chat_id, 'text': text, 'parse_mode': 'markdown'
        })
