from queue import Queue, Empty
import logging

class ServerMessaging:
    def __init__(self):
        self.logger = logging.getLogger('Server messaging')
        self.gui_queue = Queue()
        self.gui_callbacks = {}

        self.server_queue = Queue()
        self.server_callbacks = {}

    def server_register_callback(self, subject, callback):
        self.logger.debug('Server registered a callback "%s"', subject)
        self.server_callbacks[subject] = callback

    def server_check(self):
        try:
            while True:
                subject, message = self.server_queue.get_nowait()
                self.server_callbacks[subject](message)
        except Empty:
            pass

    def server_post(self, subject, message):
        self.logger.debug('Server posted a message "%s"', subject)
        self.gui_queue.put((subject, message))

    def gui_register_callbacks(self, subject, callback):
        self.logger.debug('GUI registered a callback "%s"', subject)
        self.gui_callbacks[subject] = callback

    def gui_check(self):
        try:
            while True:
                subject, message = self.gui_queue.get_nowait()
                self.gui_callbacks[subject](message)
        except Empty:
            pass

    def gui_post(self, subject, message):
        self.logger.debug('GUI posted a message "%s"', subject)
        self.server_queue.put((subject, message))
