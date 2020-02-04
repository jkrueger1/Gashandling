from datetime import datetime
from time import process_time

from .fsm import Reader, Writer
from .state import State
from fsm.data.models import Device


class CoolingDown(State):
    """ wird eine bestimmte Zeit abgekühlt """
    def __init__(self, fsm):
        super(CoolingDown, self).__init__(fsm)
        self.open_valves = False
        self.cooldown_csv = self.fsm.data['FilePaths']['cooldown_csv']
        self.pseudo_parameters_csv = self.fsm.data['FilePaths']['pseudoparameters_yml']

    def enter(self):
        self.log.info('====> CoolingDown enter')
        # enter state timer
        super(CoolingDown, self).enter(self.fsm.data['CoolingDown']['cooldown_timer'],
                                       self.fsm.data['CoolingDown']['time_interval'])

    def execute(self):
        """ execute the cool down state """
        self.log.info('Cooling Down execute')
        self.log.info(self.state_timer)
        self.state_timer = self.state_timer + process_time()
        self.log.info(self.state_timer)
        valves = self.fsm.data['CoolingDown']['valves']

        if not self.open_valves:
            self.open_valves = True
            for i in valves:
                self.fsm.valves[i] = Device('V' + str(i), True)
                self.log.info('Device V{0}, status: {1}'.format(i, self.fsm.valves[i].read()))

        while self.state_timer > process_time():
            start_timer = process_time()
            test_data = Reader.read_config(self.pseudo_parameters_csv)
            test_current_pressure_pVac = test_data['test_current_pressure_pVac']
            test_current_temperature_in_isolationskammer = test_data['test_current_temperature_in_isolationskammer']
            test_current_pressure_pPreVac = test_data['test_current_pressure_pPreVac']
            while start_timer + self.time_interval > process_time():
                pass
            time = datetime.now().strftime('%Y%d%m %H:%M:%S')
            Writer.write_cooling_down_csv_file(self.cooldown_csv,
                                               time,
                                               test_current_pressure_pPreVac,
                                               self.fsm.pPreVac_max,
                                               test_current_pressure_pVac,
                                               self.fsm.pVac_max,
                                               test_current_temperature_in_isolationskammer,
                                               self.fsm.set_point_temp_stage_1,
                                               self.fsm.set_point_pressure_stage_1)

        self.fsm.to_transition("to_measure_cooldown")

    def exit(self):
        """ Exit from cool down state """
        self.log.info('<==== CoolingDown exit')
