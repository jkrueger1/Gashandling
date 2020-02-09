from .fsm import Reader
from .state import State


class MeasurementOfPrecooling(State):
    """ measure pressure und temperature """
    def __init__(self, fsm):
        super(MeasurementOfPrecooling, self).__init__(fsm)
        self.precoolingdown_csv = self.fsm.data['FilePaths']['precooling_csv']

    def enter(self):
        self.log.info('===> Measure Precooling State enter')
        # this state need no time parameters
        super(MeasurementOfPrecooling, self).enter(0, 0)

    def execute(self):
        self.log.info('Measure Precooling State execute')
        if self.fsm.preview_state == self.fsm.states["Initialize"]:
            result = 'to_precool'
        elif self.fsm.preview_state == self.fsm.states["Precooling"]:
            values = Reader.get_current_pressure_and_temperature(self.precoolingdown_csv)
            # if pressure > 220 mbar and temperature < 4 K go to state FillWithHelium
            if float(values[1]) > self.fsm.min_pressure_in_tank:
                if float(values[2]) < self.fsm.setpoint_temperature_in_tank:
                    result = 'to_fill_helium'
                else:
                    result = Reader.read_precooling_csv(self.precoolingdown_csv,
                                                        self.fsm.min_pressure_in_tank,
                                                        self.fsm.setpoint_temperature_in_tank)
            else:
                result = "to_error"
                self.log.error('Current pressure in tank: {0} mbar. The pressure in tank should be higher as {1} mbar'
                               .format(values[1], self.fsm.min_pressure_in_tank))

        self.fsm.to_transition(result)

    def exit(self):
        self.log.info('<=== Measure Precooling State exit')


class FillLevelMeasurement(State):
    """ measure helium level """
    def __init__(self, fsm):
        super(FillLevelMeasurement, self).__init__(fsm)
        self.fillwithhelium_csv = self.fsm.data['FilePaths']['fillwithhelium_csv']

    def enter(self):
        self.log.info('===> Measure helium level enter')
        # this state need no time parameters
        super(FillLevelMeasurement, self).enter(0, 0)

    def execute(self):
        self.log.info('Measure helium level execute')
        result = 'to_fill_helium'
        pressure = Reader.get_pressure_difference(self.fillwithhelium_csv)
        if float(pressure[1]) > float(self.fsm.pressure_difference):
            if float(pressure[2]) > float(self.fsm.pressure_between_booster_pump_and_compressor_min):
                result = 'to_error'
                # todo was passiert wenn
                self.log.error('Undefined state. todo was passiert wenn ->')
            else:
                result = 'to_cooldown'
        self.log.info('current pressure in tank: {0} mbar, pOut: {1} mbar, state: {2}'
                      .format(pressure[1], pressure[2], result))
        self.fsm.to_transition(result)

    def exit(self):
        self.log.info('<=== Measure helium level exit')


class CooldownMeasurement(State):
    """ measure pressure and temperature """
    def __init__(self, fsm):
        super(CooldownMeasurement, self).__init__(fsm)
        self.cooldown_csv = self.fsm.data['FilePaths']['cooldown_csv']

    def enter(self):
        self.log.info('===> Measure cool down state enter')
        # this state need no time parameters
        super(CooldownMeasurement, self).enter(0, 0)

    def execute(self):
        self.log.info('Measure cool down execute')
        result = 'to_cooldown'
        values = Reader.get_cooldown_values(self.cooldown_csv)
        # if current pPreVac > pPreVac_max
        if float(values[1]) > float(values[2]):
            result = 'to_error'
            self.log.error('current pPreVac: {0} mbar, pPreVac_max: {1} mbar'.format(values[0], values[1]))
        # if current pVac > pVac_max
        elif float(values[3]) > float(values[4]):
            result = 'to_error'
            self.log.error('current pVac: {0} mbar, pVac_max: {1} mbar'.format(values[3], values[4]))
        # if current temperature < stage 1 temperature
        elif float(values[5]) >= float(values[6]):
            result = 'to_cooldown'
            self.log.info('current temperature: {0} K, stage 1 temperature: {1} K'.format(values[5], values[6]))
            self.log.info('current pPreVac: {0} mbar, pPreVac_max: {1} mbar'.format(values[0], values[1]))
            self.log.info('current pVac: {0} mbar, pVac_max: {1} mbar'.format(values[3], values[4]))
        else:
            # if pressure in isolation chamber is > set point pressure stage 1
            if float(values[3]) > float(values[7]):
                result = 'to_cooldown'
                self.log.info('Pressure in isolation chamber {0} is higher as {1}'
                              .format(values[3], values[7]))
            else:
                result = 'to_error'
                self.log.info('Das Ziel wurde erreicht. Es ist keine Fehlermeldung. Folgt Erweiterung...')

            self.log.info('current temperature: {0} K, stage 1 temperature: {1} K'.format(values[5], values[6]))
            self.log.info('current pPreVac: {0} mbar, pPreVac_max: {1} mbar'.format(values[0], values[1]))
            self.log.info('current pVac: {0} mbar, pVac_max: {1} mbar'.format(values[3], values[4]))

        self.log.info('State: {0}'.format(result))
        self.fsm.to_transition(result)

    def exit(self):
        self.log.info('<=== Measure cool down exit')
