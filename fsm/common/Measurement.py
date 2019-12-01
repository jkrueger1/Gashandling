from fsm.common.State import *
from fsm.common.logging import *
from fsm.common.FSM import Reader

LOGGER = MyLogger.__call__().get_logger()


class MeasurementOfPrecooling(State):
    """ measure pressure und temperature """
    def __init__(self, FSM):
        super(MeasurementOfPrecooling, self).__init__(FSM)
        self.precoolingdown_csv = self.FSM.data['FilePaths']['precooling_csv']

    def enter(self):
        LOGGER.info('===> Measure Precooling State enter')
        # this state need no time parameters
        super(MeasurementOfPrecooling, self).enter(0, 0)

    def execute(self):
        LOGGER.info('Measure Precooling State execute')
        if self.FSM.preview_state == self.FSM.states["Initialize"]:
            result = 'to_precool'
        elif self.FSM.preview_state == self.FSM.states["Precooling"]:
            values = Reader.get_current_pressure_and_temperature(self.precoolingdown_csv)
            # if pressure > 220 mbar and temperature < 4 K go to state FillWithHelium
            if float(values[1]) > self.FSM.min_pressure_in_tank:
                if float(values[2]) < self.FSM.setpoint_temperature_in_tank:
                    result = 'to_fill_helium'
                else:
                    result = Reader.read_precooling_csv(self.precoolingdown_csv
                                                        , self.FSM.min_pressure_in_tank
                                                        , self.FSM.setpoint_temperature_in_tank)
            else:
                result = "to_error"
                LOGGER.error('Current pressure in tank: {0} mbar. The pressure in tank should be higher as {1} mbar'
                             .format(values[1], self.FSM.min_pressure_in_tank))

        self.FSM.to_transition(result)

    def exit(self):
        LOGGER.info('<=== Measure Precooling State exit')


class FillLevelMeasurement(State):
    """ measure helium level """
    def __init__(self, FSM):
        super(FillLevelMeasurement, self).__init__(FSM)
        self.fillwithhelium_csv = self.FSM.data['FilePaths']['fillwithhelium_csv']

    def enter(self):
        LOGGER.info('===> Measure helium level enter')
        # this state need no time parameters
        super(FillLevelMeasurement, self).enter(0, 0)

    def execute(self):
        LOGGER.info('Measure helium level execute')
        result = 'to_fill_helium'
        pressure = Reader.get_pressure_difference(self.fillwithhelium_csv)
        if float(pressure[1]) > float(self.FSM.pressure_difference):
            if float(pressure[2]) > float(self.FSM.pressure_between_booster_pump_and_compressor_min):
                result = 'to_error'
                # todo was passiert wenn
                LOGGER.error('Undefined state. todo was passiert wenn ->')
            else:
                result = 'to_cooldown'
        LOGGER.info('current pressure in tank: {0} mbar, pOut: {1} mbar, state: {2}'
                    .format(pressure[1], pressure[2], result))
        self.FSM.to_transition(result)

    def exit(self):
        LOGGER.info('<=== Measure helium level exit')


class CooldownMeasurement(State):
    """ measure pressure and temperature """
    def __init__(self, FSM):
        super(CooldownMeasurement, self).__init__(FSM)
        self.cooldown_csv = self.FSM.data['FilePaths']['cooldown_csv']

    def enter(self):
        LOGGER.info('===> Measure cool down state enter')
        # this state need no time parameters
        super(CooldownMeasurement, self).enter(0, 0)

    def execute(self):
        LOGGER.info('Measure cool down execute')
        result = 'to_cooldown'
        values = Reader.get_cooldown_values(self.cooldown_csv)
        # if current pPreVac > pPreVac_max
        if values[1] > values[2]:
            result = 'to_error'
            LOGGER.error('current pPreVac: {0} mbar, pPreVac_max: {1} mbar'.format(values[0], values[1]))
        # if current pVac > pVac_max
        elif values[3] > values[4]:
            result = 'to_error'
            LOGGER.error('current pVac: {0} mbar, pVac_max: {1} mbar'.format(values[3], values[4]))
        # if current temperature < stage 1 temperature
        elif values[5] < values[6]:
            result = 'to_cooldown'
            LOGGER.info('current temperature: {0} K, stage 1 temperature: {1} K'.format(values[5], values[6]))
            LOGGER.info('current pPreVac: {0} mbar, pPreVac_max: {1} mbar'.format(values[0], values[1]))
            LOGGER.info('current pVac: {0} mbar, pVac_max: {1} mbar'.format(values[3], values[4]))
        else:
            LOGGER.info('current temperature: {0} K, stage 1 temperature: {1} K'.format(values[5], values[6]))
            LOGGER.info('current pPreVac: {0} mbar, pPreVac_max: {1} mbar'.format(values[0], values[1]))
            LOGGER.info('current pVac: {0} mbar, pVac_max: {1} mbar'.format(values[3], values[4]))

        LOGGER.info('State: {0}'.format(result))
        self.FSM.to_transition(result)

    def exit(self):
        LOGGER.info('<=== Measure cool down exit')
