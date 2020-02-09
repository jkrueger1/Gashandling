import sys

from .state import State


class Error(State):
    """ gibt die fehlermeldung """
    def __init__(self, fsm):
        super(Error, self).__init__(fsm)
        self.log.info('')

    def enter(self):
        super(Error, self).enter(0, 0)

    def execute(self):
        # todo stop the FSM
        self.log.error('ERROR')
        sys.exit()

    def exit(self):
        self.log.info('Close the FSM')
