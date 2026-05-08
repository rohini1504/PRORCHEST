
class PriorityGuard:
    def __init__(self):
        self.allowed = {"low", "medium", "high"}

    def validate(self, priority):
       
