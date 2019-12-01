import sys

from fsm.common.State import *
from fsm.common.logging import *

LOGGER = MyLogger.__call__().get_logger()


class Error(State):
    """ gibt die fehlermeldung """
    def __init__(self, FSM):
        super(Error, self).__init__(FSM)
        LOGGER.info('')

    def enter(self):
        super(Error, self).enter(0, 0)

    def execute(self):
        # todo stop the FSM
        LOGGER.error('ERROR')
        sys.exit()

    def exit(self):
        LOGGER.info('Close the FSM')
