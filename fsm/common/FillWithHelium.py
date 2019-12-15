from datetime import datetime
from time import process_time

from fsm.common.FSM import Reader, Writer
from fsm.common.logging import MyLogger
from fsm.common.State import State
from fsm.data.models import Device

LOGGER = MyLogger().get_logger()


class FillWithHelium(State):
    """ fill with helium """
    def __init__(self, FSM):
        super(FillWithHelium, self).__init__(FSM)
        self.open_valves = False
        self.pOut = 0.0
        self.pseudo_parameter_yml = self.FSM.data['FilePaths']['pseudoparameters_yml']
        self.fillwithhelium_csv = self.FSM.data['FilePaths']['fillwithhelium_csv']

    def enter(self):
        LOGGER.info('====> FillWithHelium enter')
        # enter state timer
        super(FillWithHelium, self).enter(self.FSM.data['FillWithHelium']['fill_timer']
                                          , self.FSM.data['FillWithHelium']['time_interval'])

    def execute(self):
        LOGGER.info('FillWithHelium execute')
        LOGGER.info('State timer : {0}'.format(self.state_timer))
        self.state_timer = self.state_timer + process_time()
        LOGGER.info('State timer + process time: {0}'.format(self.state_timer))
        valves = self.FSM.data['FillWithHelium']['valves']

        # open the valves
        if not self.open_valves:
            self.open_valves = True
            for i in valves:
                self.FSM.valves[i] = Device('V' + str(i), True)
                LOGGER.info('Device V{0}, status: {1}'.format(i, self.FSM.valves[i].get_status()))
        self.FSM.booster_pump = Device('booster_pump', True)
        self.FSM.compressor = Device('compressor', True)
        LOGGER.info('booster pump status: {0}, compressor status: {1}'
                    .format(self.FSM.booster_pump.get_status(), self.FSM.compressor.get_status()))

        while self.state_timer > process_time():
            start_timer = process_time()
            LOGGER.info('>>> Get feedback')
            test_data = Reader.read_config(self.pseudo_parameter_yml)
            while start_timer + self.time_interval > process_time():
                pass
            time = datetime.now().strftime('%Y%d%m %H:%M:%S')
            test_current_pressure = test_data['test_current_pressure']
            self.pOut = test_data['test_pressure_on_pOut']
            Writer.write_fill_with_helium_csv_file(self.fillwithhelium_csv
                                                   , time, self.FSM.current_pressure, test_current_pressure, self.pOut)
            # todo get pOut value from NICOS
            if self.pOut >= self.FSM.pressure_between_booster_pump_and_compressor_max:
                self.FSM.valves[13].change_status('V13', False)
                LOGGER.info('Device V13, status: {0}'.format(self.FSM.valves[13].get_status()))

            elif self.pOut <= self.FSM.pressure_between_booster_pump_and_compressor_min \
                    and not self.FSM.valves[13].get_status():
                self.FSM.valves[13].change_status('V13', True)
                LOGGER.info('Device V13, status: {0}'.format(self.FSM.valves[13].get_status()))

            else:
                LOGGER.info('Device V13, status: {0}'.format(self.FSM.valves[13].get_status()))
                LOGGER.info('Device pOut, status: {0}'.format(self.pOut))
            LOGGER.info('<<< Get feedback')
        # todo helium difference 200 mbar
        # todo if pOut (between vorpumpe and kompressor) > 1000 mbar should be vale 13 closed
        # todo if pOut < 300 mbar open valve 13, while the differece < 200 mbar

        self.FSM.to_transition("to_measure_fill_helium")

    def exit(self):
        LOGGER.info('<==== FillWithHelium exit')
        # exit from cool down state
