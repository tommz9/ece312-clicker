import tkinter as tk
from tkinter import ttk
import logging
import click
import signal

from .server import ClickerServer
from .server_messaging import ServerMessaging
from .poll import Poll, PollError
from .questions import poll_questions
from .protocol import PollProtocol


class PollWindow(ttk.Frame):

    """The GUI class for this application.

    The communication between the Tkinter GUI and the threaded TCP server
    is done through a double queue represented by a class Server Messaging.
    The GUI checks the queue periodically for new messages to avoid blocking
    the GUI thread.
    """

    """The period for checking the comminication queue."""
    MESSAGING_CHECK_PERIOD = 100

    def __init__(self, on_close_callback, poll, master=None):
        super().__init__(master, padding=(10, 10, 12, 12))

        self.logger = logging.getLogger('PollWindow')

        self.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        self.poll = poll
        poll.register_vote_updated_callback(self.update_poll)

        self.create_widgets()

        self.on_close_callback = on_close_callback
        self.master.protocol("WM_DELETE_WINDOW", self.close_window)

    def close_window(self):
        self.on_close_callback()
        self.master.destroy()

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
        answer_b.grid(column=1, row=1, padx=50)
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

    def periodic_messaging_check(self):
        # self.logger.debug('Checking the queue')
        self.server_messaging.gui_check()
        self.after(PollWindow.MESSAGING_CHECK_PERIOD,
                   self.periodic_messaging_check)


class PollSelectionWindow(ttk.Frame):
    def __init__(self, poll_protocol, master=None):
        """"""
        super().__init__(master, padding=(10, 10, 12, 12))

        self.poll_protocol = poll_protocol
        self.logger = logging.getLogger('PollSelectionWindow')

        self.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        self.check_ip_variable = tk.IntVar()
        self.check_ip_variable.set(1)

        # Handle SIGINT
        signal.signal(signal.SIGINT, lambda a, b: master.destroy())

        self.create_widgets()

    def create_widgets(self):

        first_row_padding = 20

        label = ttk.Label(self, text='Question: ')
        label.grid(row=1, column=1, pady=(0, first_row_padding), sticky='E')

        self.question_combo_box = ttk.Combobox(self,
                                               values=list(poll_questions.keys()),
                                               state='readonly',
                                               width=30)
        self.question_combo_box.current(0)
        self.question_combo_box.grid(row=1, column=2, columnspan=2, pady=(0, first_row_padding))

        self.ip_checking_checkbox = ttk.Checkbutton(self, text='IP Checking Enable', variable=self.check_ip_variable,
                                                    state=tk.DISABLED)
        self.ip_checking_checkbox.grid(row=3, column=1, columnspan=3, sticky='W')

        self.open_poll_button = ttk.Button(self, text='Open Poll', command=self.open_poll_clicked)
        self.open_poll_button.grid(row=10, column=1)

        self.close_poll_button = ttk.Button(self, text='Close Poll', command=self.close_poll_clicked)
        self.close_poll_button.grid(row=10, column=2)

        self.exit_button = ttk.Button(self, text='Exit application', command=self.master.destroy)
        self.exit_button.grid(row=10, column=3)

        self.set_state('inactive')

    def open_poll_clicked(self):
        question = self.question_combo_box.get()
        answers = poll_questions[question]

        self.logger.info('Poll selected. Question: "%s", Answers: %s', question, answers)

        poll = Poll(question, answers)
        self.poll_protocol.activate(poll)

        self.set_state('active')

        def on_close_callback():
            self.set_state('inactive')
            self.poll_protocol.deactivate()

        toplevel = tk.Toplevel(self.master)
        self.poll_window = PollWindow(
            master=toplevel,
            poll=poll,
            on_close_callback=on_close_callback
        )

    def close_poll_clicked(self):
        self.logger.debug('Closing the poll window.')
        self.poll_window.close_window()

    def set_state(self, state):
        if state == 'inactive':
            self.open_poll_button['state'] = tk.NORMAL
            self.close_poll_button['state'] = tk.DISABLED
        elif state == 'active':
            self.open_poll_button['state'] = tk.DISABLED
            self.close_poll_button['state'] = tk.NORMAL
        else:
            raise RuntimeError('Invalid state {}'.format(state))


@click.command('The server application for ECE312 Lab 3')
@click.option('--host', default='0.0.0.0', help='The address the TCP server listens on.')
@click.option('--port', default=2000, help='The port the TCP server listens on.')
@click.option('--verbose', is_flag=True, default=False, help='Enables additional debug prints.')
def main(host, port, verbose):

    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    server_messaging = ServerMessaging()
    server = ClickerServer(host, port, server_messaging)

    poll_protocol = PollProtocol(
        lambda ip, message: server_messaging.gui_post('send_message', (ip, message)),
        lambda message: server_messaging.gui_post('broadcast_message', message)
    )

    server_messaging.gui_register_callbacks(
        'received', lambda message: poll_protocol.on_data(message[0], message[1]))

    server_messaging.gui_register_callbacks(
        'connected', poll_protocol.on_new_connection)

    server_messaging.gui_register_callbacks(
        'disconnected', lambda message: None)

    server_messaging.server_register_callback('broadcast_message', server.broadcast)

    root = tk.Tk()

    def periodic_messaging_check():
        server_messaging.gui_check()
        root.after(100, periodic_messaging_check)

    root.after(100, periodic_messaging_check)

    app = PollSelectionWindow(poll_protocol, master=root)
    app.mainloop()

    server.stop()


if __name__ == '__main__':
    main()
