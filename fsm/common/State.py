from time import process_time
from fsm.common.logging import *

LOGGER = MyLogger.__call__().get_logger()


class State(object):
    """ base state class """
    def __init__(self, FSM):
        self.FSM = FSM
        self.state_timer = 0
        self.time_interval = 0

    def enter(self, state_timer, time_interval):
        self.state_timer = state_timer
        self.time_interval = time_interval
        LOGGER.info('State timer: {0}, time interval (recording interval): {1}'.format(state_timer, time_interval))

    def execute(self):
        pass

    def exit(self):
        pass
