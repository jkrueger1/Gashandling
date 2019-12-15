from fsm.common.State import State
from fsm.common.logging import MyLogger
from fsm.data.models import Device

LOGGER = MyLogger.__call__().get_logger()


class Initialize(State):
    """ start Zustand """
    def __init__(self, FSM):
        super(Initialize, self).__init__(FSM)
        self.valves = {}

    def enter(self):
        LOGGER.info('Initialize enter')
        # this state does not need a time parameters
        super(Initialize, self).enter(0, 0)

    def execute(self):
        # todo set all device to false or check if the are working
        LOGGER.info('Initialize execute')
        for i in range(1, 16):
            self.valves[i] = Device('V' + str(i), "false")
            self.valves[i].get_status()
        self.FSM.to_transition("to_measure_precooling")

    def exit(self):
        LOGGER.info('initialize successful')
