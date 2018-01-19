import tkinter as tk
from tkinter import ttk
import logging

from .server import ClickerServer
from .server_messaging import ServerMessaging
from .poll import Poll, PollError

class Application(ttk.Frame):

    MESSAGING_CHECK_PERIOD = 100

    def __init__(self, server, server_messanging, master=None, poll=None):
        super().__init__(master, padding=(10, 10, 12, 12))

        self.logger = logging.getLogger('GUI')

        self.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        self.server = server
        self.server_messaging = server_messanging

        server_messanging.gui_register_callbacks(
            'received', self.message_received)

        server_messanging.gui_register_callbacks(
            'connected', self.client_connected)
        
        server_messanging.gui_register_callbacks(
            'disconnected', self.client_disconnected)

        if not poll:
            self.poll = Poll('What is your favorite?', ['I2C', 'SPI', 'UART'])
        else:
            self.poll = poll

        self.create_widgets()

        self.after(Application.MESSAGING_CHECK_PERIOD, 
                   self.periodic_messaging_check)

    def create_widgets(self):

        s = ttk.Style()
        s.configure('question.TLabel', font=('Helvetica', 50))

        s = ttk.Style()
        s.configure('answer.TLabel', font=('Helvetica', 32))

        s = ttk.Style()
        s.configure('counter.TLabel', font=('Helvetica', 32))

        self.question_label = ttk.Label(self,
                                        text='N/A',
                                        style='question.TLabel')

        self.question_label.grid(column=0, row=0, columnspan=3, pady=(10, 30))

        answer_a = ttk.Label(self, text='N/A', style='answer.TLabel')
        answer_b = ttk.Label(self, text='N/A', style='answer.TLabel')
        answer_c = ttk.Label(self, text='N/A', style='answer.TLabel')

        answer_a.grid(column=0, row=1)
        answer_b.grid(column=1, row=1)
        answer_c.grid(column=2, row=1)

        self.answer_labels = [answer_a, answer_b, answer_c]

        def create_counter(column):
            counter = ttk.Label(self, text='N/A', style='counter.TLabel')
            counter.grid(column=column, row=3)
            return counter

        self.counter_labels = [create_counter(x) for x in range(3)]

        self.log_text = tk.Text(self)

        self.update_poll()
    
    def update_poll(self):
        self.question_label['text'] = self.poll.question
        for n in range(3):
            self.answer_labels[n]['text'] = self.poll.answers[n]
            self.counter_labels[n]['text'] = '{}'.format(
                self.poll.get_votes(n))
    
    def message_received(self, message):
        ip, data = message
        self.logger.info('Data received from %s: "%s"', ip, data)
        
        try:
            self.poll.vote(ip, data.strip())
            self.update_poll()
        except PollError as e:
            self.logger.exception(e)
    
    def client_connected(self, ip):
        self.logger.info('Client connected %s', ip)
        # TODO
        pass

    def client_disconnected(self, ip):
        self.logger.info('Client disconnected %s', ip)
        # TODO
        pass

    def periodic_messaging_check(self):
        # self.logger.debug('Checking the queue')
        self.server_messaging.gui_check()
        self.after(Application.MESSAGING_CHECK_PERIOD,
                   self.periodic_messaging_check)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)


    server_messanging = ServerMessaging()
    server = ClickerServer('192.168.1.145', 10000, server_messanging)


    root = tk.Tk()
    app = Application(server, server_messanging, master=root)
    app.mainloop()
