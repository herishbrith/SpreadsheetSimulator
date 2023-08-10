

class UnsupportedOperationError(Exception):

    def __init__(self, message, *args):
        self.message = message
        super(UnsupportedOperationError, self).__init__(message, *args) 
