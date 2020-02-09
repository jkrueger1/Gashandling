from .logging import MyLogger


class Transition(object):
    """ """
    def __init__(self, to_state):
        self.to_state = to_state
        self.log = MyLogger().get_logger()

    def execute(self):
        self.log.info('Transitioning to state {0} ...'.format(self.to_state))
