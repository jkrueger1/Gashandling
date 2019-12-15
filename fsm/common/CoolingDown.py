from fsm.common.State import State
from fsm.common.logging import MyLogger
from fsm.common.FSM import Reader, Writer
from fsm.data.models import Device
from datetime import datetime

LOGGER = MyLogger.__call__().get_logger()


class CoolingDown(State):
    """ wird eine bestimmte Zeit abgekühlt """
    def __init__(self, FSM):
        super(CoolingDown, self).__init__(FSM)
        self.open_valves = False
        self.cooldown_csv = self.FSM.data['FilePaths']['cooldown_csv']
        self.pseudo_parameters_csv = self.FSM.data['FilePaths']['pseudoparameters_yml']

    def enter(self):
        LOGGER.info('====> CoolingDown enter')
        # enter state timer
        super(CoolingDown, self).enter(self.FSM.data['CoolingDown']['cooldown_timer']
                                       , self.FSM.data['CoolingDown']['time_interval'])

    def execute(self):
        """ execute the cool down state """
        LOGGER.info('Cooling Down execute')
        LOGGER.info(self.state_timer)
        self.state_timer = self.state_timer + process_time()
        LOGGER.info(self.state_timer)
        valves = self.FSM.data['CoolingDown']['valves']

        if not self.open_valves:
            self.open_valves = True
            for i in valves:
                self.FSM.valves[i] = Device('V' + str(i), True)
                LOGGER.info('Device V{0}, status: {1}'.format(i, self.FSM.valves[i].get_status()))

        while self.state_timer > process_time():
            start_timer = process_time()
            test_data = Reader.read_config(self.pseudo_parameters_csv)
            test_current_pressure_pVac = test_data['test_current_pressure_pVac']
            test_current_temperature_in_isolationskammer = test_data['test_current_temperature_in_isolationskammer']
            test_current_pressure_pPreVac = test_data['test_current_pressure_pPreVac']
            while start_timer + self.time_interval > process_time():
                pass
            time = datetime.now().strftime('%Y%d%m %H:%M:%S')
            Writer.write_cooling_down_csv_file(self.cooldown_csv
                                               , time
                                               , test_current_pressure_pPreVac
                                               , self.FSM.pPreVac_max
                                               , test_current_pressure_pVac
                                               , self.FSM.pVac_max
                                               , test_current_temperature_in_isolationskammer
                                               , self.FSM.set_point_temp_stage_1
                                               , self.FSM.set_point_pressure_stage_1)

        self.FSM.to_transition("to_measure_cooldown")

    def exit(self):
        """ Exit from cool down state """
        LOGGER.info('<==== CoolingDown exit')
