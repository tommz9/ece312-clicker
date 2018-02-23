import tkinter as tk
from tkinter import ttk
import logging

from .server import ClickerServer
from .server_messaging import ServerMessaging
from .poll import Poll, PollError
from .questions import poll_questions

class PoolWindow(ttk.Frame):

    MESSAGING_CHECK_PERIOD = 100

    def __init__(self, server, server_messanging, master=None, poll=None):
        super().__init__(master, padding=(10, 10, 12, 12))

        self.logger = logging.getLogger('PoolWindow')

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

        self.after(PoolWindow.MESSAGING_CHECK_PERIOD,
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
        self.after(PoolWindow.MESSAGING_CHECK_PERIOD,
                   self.periodic_messaging_check)

class PollSelectionWindow(ttk.Frame):
    def __init__(self, master=None):
        """"""
        super().__init__(master, padding=(10, 10, 12, 12))

        self.logger = logging.getLogger('PollSelectionWindow')

        self.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        self.check_ip_variable = tk.IntVar()
        self.check_ip_variable.set(1)

        self.create_widgets()

    def create_widgets(self):

        first_row_padding = 20

        label = ttk.Label(self, text='Question: ')
        label.grid(row=1, column=1, pady=(0, first_row_padding), sticky='E')

        self.question_combo_box = ttk.Combobox(self, values=list(poll_questions.keys()), state='readonly')
        self.question_combo_box.current(0)
        self.question_combo_box.grid(row=1, column=2, columnspan=2, pady=(0, first_row_padding))

        self.ip_checking_checkbox = ttk.Checkbutton(self, text='IP Checking Enable', variable=self.check_ip_variable)
        self.ip_checking_checkbox.grid(row=3, column=1, columnspan=3, sticky='W')

        self.open_poll_button = ttk.Button(self, text='Open Poll', command=self.open_poll_clicked)
        self.open_poll_button.grid(row=10, column=1)

        self.close_poll_button = ttk.Button(self, text='Close Poll')
        self.close_poll_button.grid(row=10, column=2)

        self.exit_button = ttk.Button(self, text='Exit application')
        self.exit_button.grid(row=10, column=3)

    def open_poll_clicked(self):
        question = self.question_combo_box.get()
        answers = poll_questions[question]

        self.logger.info('Poll selected. Question: "%s", Answers: %s', question, answers)

        print(question, answers)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)


    server_messanging = ServerMessaging()
    server = ClickerServer('192.168.1.145', 10000, server_messanging)


    root = tk.Tk()
    #app = PoolWindow(server, server_messanging, master=root)

    app = PollSelectionWindow(master=root)
    app.mainloop()
