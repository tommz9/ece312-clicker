
from .poll import Poll, PollAlreadyVoted

class PollProtocol:
    def __init__(self, send_message_callback, broadcast_callback):
        self.send_message_callback = send_message_callback
        self.broadcast_callback = broadcast_callback
        self.deactivate()

    def activate(self, poll):
        assert self.poll is None

        self.poll = poll
        self.broadcast_callback('active')

    def deactivate(self):
        self.broadcast_callback('inactive')
        self.poll = None

    def on_new_connection(self, ip):
        if self.poll:
            if self.poll.ip_voted(ip):
                self.send_message_callback(ip, 'voted')
            else:
                self.send_message_callback(ip, 'active')
        else:
            self.send_message_callback(ip, 'inactive')

    def on_data(self, ip, data):
        data = data.strip()

        if not Poll.check_choice_is_valid(data):
            self.send_message_callback(ip, 'error')
            return

        if self.poll:
            try:
                self.poll.vote(ip, data)
                self.send_message_callback(ip, 'OK')
            except PollAlreadyVoted:
                self.send_message_callback(ip, 'voted')
        else:
            self.send_message_callback(ip, 'inactive')
