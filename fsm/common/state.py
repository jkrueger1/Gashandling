from .logging import MyLogger


class State(object):
    """ base state class """
    def __init__(self, fsm):
        self.fsm = fsm
        self.state_timer = 0
        self.time_interval = 0
        self.log = MyLogger().get_logger()

    def enter(self, state_timer, time_interval):
        self.state_timer = state_timer
        self.time_interval = time_interval
        self.log.info('State timer: {0}, time interval (recording interval): {1}'.format(state_timer, time_interval))

    def execute(self):
        pass

    def exit(self):
        pass
