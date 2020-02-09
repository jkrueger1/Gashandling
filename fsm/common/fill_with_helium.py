from datetime import datetime
from time import process_time

from .fsm import Reader, Writer
from .state import State
from fsm.data.models import Device


class FillWithHelium(State):
    """ fill with helium """
    def __init__(self, fsm):
        super(FillWithHelium, self).__init__(fsm)
        self.open_valves = False
        self.pOut = 0.0
        self.pseudo_parameter_yml = self.fsm.data['FilePaths']['pseudoparameters_yml']
        self.fillwithhelium_csv = self.fsm.data['FilePaths']['fillwithhelium_csv']

    def enter(self):
        self.log.info('====> FillWithHelium enter')
        # enter state timer
        super(FillWithHelium, self).enter(self.fsm.data['FillWithHelium']['fill_timer'],
                                          self.fsm.data['FillWithHelium']['time_interval'])

    def execute(self):
        self.log.info('FillWithHelium execute')
        self.log.info('State timer : {0}'.format(self.state_timer))
        self.state_timer = self.state_timer + process_time()
        self.log.info('State timer + process time: {0}'.format(self.state_timer))
        valves = self.fsm.data['FillWithHelium']['valves']

        # open the valves
        if not self.open_valves:
            self.open_valves = True
            for i in valves:
                self.fsm.valves[i] = Device('V%d', True)
                self.log.info('Device V{0}, status: {1}'.format(i, self.fsm.valves[i].read()))
        self.fsm.booster_pump = Device('booster_pump', True)
        self.fsm.compressor = Device('compressor', True)
        self.log.info('booster pump status: {0}, compressor status: {1}'
                      .format(self.fsm.booster_pump.read(), self.fsm.compressor.read()))

        while self.state_timer > process_time():
            start_timer = process_time()
            self.log.info('>>> Get feedback')
            test_data = Reader.read_config(self.pseudo_parameter_yml)
            while start_timer + self.time_interval > process_time():
                pass
            time = datetime.now().strftime('%Y%d%m %H:%M:%S')
            test_current_pressure = test_data['test_current_pressure']
            self.pOut = test_data['test_pressure_on_pOut']
            Writer.write_fill_with_helium_csv_file(self.fillwithhelium_csv,
                                                   time,
                                                   self.fsm.current_pressure,
                                                   test_current_pressure,
                                                   self.pOut)
            # todo get pOut value from NICOS
            if self.pOut >= self.fsm.pressure_between_booster_pump_and_compressor_max:
                self.fsm.valves[13].move(False)
                self.log.info('Device V13, status: {0}'.format(self.fsm.valves[13].read()))

            elif self.pOut <= self.fsm.pressure_between_booster_pump_and_compressor_min \
                    and not self.fsm.valves[13].read():
                self.fsm.valves[13].move(True)
                self.log.info('Device V13, status: {0}'.format(self.fsm.valves[13].read()))

            else:
                self.log.info('Device V13, status: {0}'.format(self.fsm.valves[13].read()))
                self.log.info('Device pOut, status: {0}'.format(self.pOut))
            self.log.info('<<< Get feedback')
        # todo helium difference 200 mbar
        # todo if pOut (between vorpumpe and kompressor) > 1000 mbar should be vale 13 closed
        # todo if pOut < 300 mbar open valve 13, while the differece < 200 mbar

        self.fsm.to_transition("to_measure_fill_helium")

    def exit(self):
        self.log.info('<==== FillWithHelium exit')
        # exit from cool down state
