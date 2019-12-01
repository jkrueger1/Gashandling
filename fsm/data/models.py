from fsm.common.logging import *
LOGGER = MyLogger.__call__().get_logger()


class Device(object):
    def __init__(self, name, status):
        self.name = name
        self.status = status
        # todo get feedback from device

    def change_status(self, name, status):
        self.name = name
        self.status = status
        LOGGER.info('Device: {0}, Status: {1}'.format(name, status))
        # todo change the status of device

    def get_status(self):
        return self.status
