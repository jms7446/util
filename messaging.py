import requests
from abc import ABC, abstractmethod
import sys

from .custom import CustomLogger

logger = CustomLogger.__call__().get_logger()

# for messaging
BOLD_BEGIN = "_(b)_"
BOLD_END = "_(/b)_"
NEW_LINE = "_(n)_"


class Messenger(ABC):

    @abstractmethod
    def send(self, message):
        pass

    @classmethod
    def from_dict(cls, info):
        messenger_type = info["messenger_type"]
        if messenger_type == "telegram":
            return TelegramMessenger(info["token"], info["chat_id"], info["parse_mode"], info["header"])
        elif messenger_type == "slack":
            return SlackMessenger(info['api_url'], info['header'])
        elif messenger_type == "stream":
            return StreamMessenger(sys.stdout)
        elif messenger_type == "null":
            return NullMessenger()


class StreamMessenger(Messenger):
    def __init__(self, stream):
        super().__init__()
        self._stream = stream

    def send(self, message):
        self._stream.write(message + '\n')


class NullMessenger(Messenger):
    def __init__(self):
        super().__init__()

    def send(self, message):
        pass


class TelegramMessenger(Messenger):

    def __init__(self, token, chat_id, parse_mode, header):
        from telegram import Bot
        super().__init__()
        self.bot = Bot(token=token)
        self._chat_id = chat_id
        self._parse_mode = parse_mode
        self.header = header

    def _send(self, message, chat_id=None, parse_mode=None):
        chat_id = chat_id if chat_id else self._chat_id
        parse_mode = parse_mode or self._parse_mode
        total_message = self.header + message
        self.bot.send_message(chat_id=chat_id, text=total_message, parse_mode=parse_mode)

    def send(self, message, parse_mode=None):
        try:
            self._send(message, parse_mode)
        except Exception:
            self._send("TelegramMessenger: message_send_fail")
            logger.exception(f"TelegramMessenger: message_send_fail, ({message})")
            raise


class SlackMessenger(Messenger):

    def __init__(self, api_url, header='', parse_mode=None):
        super().__init__()
        self.api_url = api_url
        self.header = header
        self.parse_mode = parse_mode

    def send(self, message, parse_mode=None):
        payload = {
            'text': self.header + message
        }
        requests.post(self.api_url, json=payload)


class SharedMessenger(object):
    __shared_state = {
        "_messenger": Messenger.from_dict({"messenger_type": "stream"})
    }

    def __init__(self):
        self._messenger = None
        self.__dict__ = self.__shared_state

    def set(self, messenger_info=None, messenger=None):
        if messenger_info is None and messenger is None:
            raise ValueError('messenger_type or messenger must have value')
        if messenger is not None:
            self._messenger = messenger
        else:
            self._messenger = Messenger.from_dict(messenger_info)

    def send(self, message):
        return self._messenger.send(message)
