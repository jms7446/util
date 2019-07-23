from urllib.request import urlopen
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
            return SlackMessenger(info["token"], info["user"], info["channel"])
        elif messenger_type == "stream":
            return StreamMessenger(sys.stdout)
        elif messenger_type == "null":
            return NullMessenger()

    @staticmethod
    def _alt_message_by_parse_mode(message, parse_mode):
        def remove_html_tag_pattern(s):
            return (s
                    .replace("<", "(")
                    .replace(">", ")"))

        def remove_markdown_pattern(s):
            return (s
                    .replace("*", "%")
                    .replace("*", "%"))

        def replace_html_tag_pattern(s):
            return (s
                    .replace(NEW_LINE, "\n")
                    .replace(BOLD_BEGIN, "<b>")
                    .replace(BOLD_END, "</b>"))

        def replace_markdown_pattern(s):
            return (s
                    .replace(NEW_LINE, "\n")
                    .replace(BOLD_BEGIN, "*")
                    .replace(BOLD_END, "*"))

        if parse_mode.lower() == "html":
            message = remove_html_tag_pattern(message)
            message = replace_html_tag_pattern(message)
        elif parse_mode.lower() == "markdown":
            message = remove_markdown_pattern(message)
            message = replace_markdown_pattern(message)
        else:
            raise Exception("Unknown parse mode : {}".format(parse_mode))
        return message


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
        parse_mode = parse_mode if parse_mode else self._parse_mode
        total_message = self.header + message
        total_message = self._alt_message_by_parse_mode(total_message, parse_mode)
        self.bot.send_message(chat_id=chat_id, text=total_message, parse_mode=parse_mode)

    def send(self, message, parse_mode=None):
        try:
            self._send(message, parse_mode)
        except Exception:
            self._send("TelegramMessenger: message_send_fail")
            logger.exception(f"TelegramMessenger: message_send_fail, ({message})")
            raise


class SlackMessenger(Messenger):
    TARGET_URL_FORMAT = "https://%s.slack.com/services/hooks/slackbot?token=%s&channel=%s"

    def __init__(self, token, user, channel):
        super().__init__()
        self._target_url = self.TARGET_URL_FORMAT % (user, token, channel)

    def send(self, message):
        urlopen(self._target_url, data=message).read()


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