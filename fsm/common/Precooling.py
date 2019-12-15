from fsm.common.State import State
from fsm.common.logging import MyLogger
from fsm.common.FSM import Reader
from datetime import datetime
from fsm.common.FSM import Writer
LOGGER = MyLogger.__call__().get_logger()


class Precooling(State):
    """ wird eine bestimmte Zeit vorgekühlt"""
    def __init__(self, FSM):
        super(Precooling, self).__init__(FSM)
        self.pseudo_parameter_yml = self.FSM.data['FilePaths']['pseudoparameters_yml']
        self.precooldown_csv = self.FSM.data['FilePaths']['precooling_csv']

    def enter(self):
        LOGGER.info('===> Precooling enter')
        # enter state timer
        super(Precooling, self).enter(self.FSM.data['Precooling']['precooling_timer'], self.FSM.data['Precooling']['time_interval'])

    def execute(self):
        LOGGER.info('Precooling execute method')
        self.state_timer = self.state_timer + process_time()

        while self.state_timer > process_time():
            start_time = process_time()
            # todo read test values from NICOS
            test_data = Reader.read_config(self.pseudo_parameter_yml)
            LOGGER.info('test data: {0}'.format(test_data))
            LOGGER.info('>>> Get feedback for P and T')
            # interval zwischen die einzelne Messungen
            while start_time + self.time_interval > process_time():
                pass
            time = datetime.now().strftime('%Y%d%m %H:%M:%S')
            # todo only for test
            test_current_temperature = test_data['current_temperature']
            test_current_pressure = test_data['current_pressure']
            LOGGER.info('test_current_temperature {0} K, test_current_pressure: {1} mbar'
                        .format(test_current_temperature, test_current_pressure))

            self.FSM.current_temp = test_current_temperature  # todo read current temperature from sensor
            self.FSM.current_pressure = test_current_pressure  # todo read current pressure form sensor
            Writer.write_csv(self.precooldown_csv, time, self.FSM.current_pressure, self.FSM.current_temp
                             , self.FSM.setpoint_temperature_in_tank, Reader.read_initial_temp(self.precooldown_csv))
            LOGGER.info('Precooling timer: {0}'.format(process_time()))
            LOGGER.info('<<< Get feedback for P and T')
        self.FSM.to_transition("to_measure_precooling")

    def exit(self):
        LOGGER.info('<=== Precooling exit')
