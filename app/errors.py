

class InvalidPayload(Exception):
    """error raised if payload does not pass pydentic validation"""
    status_code = 400

    def __init__(self, message, validation_error):

        Exception.__init__(self)
        self.message = message
        self.error_list = validation_error.errors()