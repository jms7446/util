from unittest.mock import patch, Mock

from ..messaging import SharedMessenger


@patch('sys.stdout')
def test_messenger_stream(mock_stdout):
    messenger = SharedMessenger()
    messenger.set({'messenger_type': 'stream'})
    messenger.send('hello')
    mock_stdout.write.assert_called_with('hello\n')


def test_shared_messenger_share_messenger1():
    sm1 = SharedMessenger()
    sm2 = SharedMessenger()

    m1 = Mock()
    m2 = Mock()

    sm1.set(messenger=m1)
    sm2.set(messenger=m2)

    sm1.send('hi')
    m1.send.assert_not_called()
    m2.send.assert_called_with('hi')


def test_shared_messenger_share_messenger2():
    sm1 = SharedMessenger()
    sm2 = SharedMessenger()

    m1 = Mock()
    m2 = Mock()

    sm1.set(messenger=m1)
    sm2.set(messenger=m2)

    sm2.send('hi')
    m1.send.assert_not_called()
    m2.send.assert_called_with('hi')
