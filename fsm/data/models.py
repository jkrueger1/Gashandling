from fsm.common.logging import MyLogger


class Device(object):
    def __init__(self, name, status):
        self._name = name
        self._status = status
        self.log = MyLogger().get_logger()
        # todo get feedback from device

    def move(self, status):
        self._status = status
        self.log.info('Device: {0}, Status: {1}'.format(self._name, self._status))
        # todo change the status of device

    def read(self):
        return self._status
