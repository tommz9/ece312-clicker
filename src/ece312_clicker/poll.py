
class PollError(Exception):
    pass

class Poll:
    def __init__(self, question, answers):
        self.question = question

        if len(answers) != 3:
            raise ValueError('Only 3 answers in a poll are supported.')
        
        self.answers = answers

        self.registered_ip_addresses = []

        self.votes = {'A': 0, 'B': 0, 'C': 0}

    def vote(self, ip, choice):
        if ip in self.registered_ip_addresses:
            raise PollError('IP {} already voted.'.format(ip))
        
        if choice not in ['A', 'B', 'C']:
            raise PollError('Invalid choice "{}"'.format(choice))
        
        self.votes[choice] += 1

        self.registered_ip_addresses.append(ip)

    def get_votes(self, choice):
        if isinstance(choice, int):
            choice = ['A', 'B', 'C'][choice]
        return self.votes[choice]
        
