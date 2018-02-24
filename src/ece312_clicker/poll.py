
class PollError(Exception):
    pass

class PollAlreadyVoted(PollError):
    pass

class Poll:
    def __init__(self, question, answers):
        self.question = question

        if len(answers) != 3:
            raise ValueError('Only 3 answers in a poll are supported.')
        
        self.answers = answers

        self.registered_ip_addresses = []

        self.votes = {'A': 0, 'B': 0, 'C': 0}

    def register_vote_updated_callback(self, cb):
        self.vote_updated_cb = cb

    def vote(self, ip, choice):
        if ip in self.registered_ip_addresses:
            raise PollAlreadyVoted('IP {} already voted.'.format(ip))
        
        if not Poll.check_choice_is_valid(choice):
            raise PollError('Invalid choice "{}"'.format(choice))
        
        self.votes[choice] += 1

        self.registered_ip_addresses.append(ip)

        self.vote_updated_cb()

    def get_votes(self, choice):
        if isinstance(choice, int):
            choice = ['A', 'B', 'C'][choice]
        return self.votes[choice]
        
    def ip_voted(self, ip):
        return ip in self.registered_ip_addresses

    @staticmethod
    def check_choice_is_valid(choice):
        return choice in ['A', 'B', 'C']