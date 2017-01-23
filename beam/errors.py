BEAM_SUCCESSFUL_TERMINATION = 0  # default successful termination exit code on unix
BEAM_GENERAL_ERROR = 1  # default general error code on unix
BEAM_COMMANDLINE_SYNTAX_ERROR = 2  # default command line syntax error code on unix


class BEAMException(Exception):
    def __init__(self, msg, exit_code=None, status_code=None):
        self.status = status_code
        self.msg = msg
        self.exit_code = exit_code


class BEAMCommandlineParserException(BEAMException):
    pass


class BEAMConfParserException(BEAMException):
    pass


class BEAMErrorException(BEAMException):
    pass


class BEAMExitException(BEAMException):
    pass
