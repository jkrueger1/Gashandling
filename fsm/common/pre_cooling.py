from datetime import datetime
from time import process_time

from .fsm import Reader, Writer
from .state import State


class Precooling(State):
    """ wird eine bestimmte Zeit vorgekühlt"""
    def __init__(self, fsm):
        super(Precooling, self).__init__(fsm)
        self.pseudo_parameter_yml = self.fsm.data['FilePaths']['pseudoparameters_yml']
        self.precooldown_csv = self.fsm.data['FilePaths']['precooling_csv']

    def enter(self):
        self.log.info('===> Precooling enter')
        # enter state timer
        super(Precooling, self).enter(self.fsm.data['Precooling']['precooling_timer'], self.fsm.data['Precooling']['time_interval'])

    def execute(self):
        self.log.info('Precooling execute method')
        self.state_timer = self.state_timer + process_time()

        while self.state_timer > process_time():
            start_time = process_time()
            # todo read test values from NICOS
            test_data = Reader.read_config(self.pseudo_parameter_yml)
            self.log.info('test data: {0}'.format(test_data))
            self.log.info('>>> Get feedback for P and T')
            # interval zwischen die einzelne Messungen
            while start_time + self.time_interval > process_time():
                pass
            time = datetime.now().strftime('%Y%d%m %H:%M:%S')
            # todo only for test
            test_current_temperature = test_data['current_temperature']
            test_current_pressure = test_data['current_pressure']
            self.log.info('test_current_temperature {0} K, test_current_pressure: {1} mbar'
                          .format(test_current_temperature, test_current_pressure))

            self.fsm.current_temp = test_current_temperature  # todo read current temperature from sensor
            self.fsm.current_pressure = test_current_pressure  # todo read current pressure form sensor
            Writer.write_csv(self.precooldown_csv, time, self.fsm.current_pressure, self.fsm.current_temp,
                             self.fsm.setpoint_temperature_in_tank, Reader.read_initial_temp(self.precooldown_csv))
            self.log.info('Precooling timer: {0}'.format(process_time()))
            self.log.info('<<< Get feedback for P and T')
        self.fsm.to_transition("to_measure_precooling")

    def exit(self):
        self.log.info('<=== Precooling exit')
