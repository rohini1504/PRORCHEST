
class StateManager:
    def __init__(self):
        self.states = ["open", "in-progress", "closed"]

    def is_valid(self, state):
        return state in self.states
