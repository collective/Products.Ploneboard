class ValidationError(Exception):

    def __init__(self, controller_state, message=None):
        self.message = message
        self.controller_state = controller_state

    def __str__(self):
        return 'ValidationError: %s\nstate=%s' % (str(self.message), str(self.controller_state))
