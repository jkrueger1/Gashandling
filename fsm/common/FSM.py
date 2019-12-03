
import csv
import math
from time import process_time

import yaml

from fsm.common.logging import MyLogger

LOGGER = MyLogger().get_logger()


class FSM(object):
    """ FSM parameter """

    def __init__(self, character):
        self.char = character
        self.states = {}
        self.transitions = {}
        self.cur_state = None
        self.preview_state = None
        self.trans = None
        # todo fsm parameter
        # temperature parameters
        self.data = Reader.read_config('fsm/configuration/config.yml')
        self.setpoint_temperature_in_tank = self.data['Precooling']['Einsatztemperatur']
        self.temp_max = None
        self.setpoint_temp = None
        self.current_temp = None
        self.set_point_temp_stage_1 = self.data['CoolingDown']['set_point_temp_stage_1']
        # pressure parameters
        self.min_pressure_in_tank = self.data['Precooling']['MinPressureInTank']
        self.max_pressure = None
        self.setpoint_pressure = None
        self.current_pressure = None
        self.pressure_difference = self.data['FillWithHelium']['pressure_difference']
        self.pressure_between_booster_pump_and_compressor_max = \
            self.data['FillWithHelium']['pressure_between_booster_pump_and_compressor_max']
        self.pressure_between_booster_pump_and_compressor_min = \
            self.data['FillWithHelium']['pressure_between_booster_pump_and_compressor_min']
        self.pVac_max = self.data['CoolingDown']['pVac_max']
        self.pPreVac_max = self.data['CoolingDown']['pPreVac_max']
        self.set_point_pressure_stage_1 = self.data['CoolingDown']['set_point_pressure_stage_1']
        # devices
        self.valves = {}
        self.booster_pump = False
        self.compressor = False

    def add_transition(self, trans_name, transition):
        self.transitions[trans_name] = transition
        LOGGER.info('FSM method add_transition trans name: {0}, transition: {1}'.format(trans_name, transition.to_state))

    def add_state(self, state_name, state):
        self.states[state_name] = state
        LOGGER.info('FSM method add_state state name: {0}, preview state: {1}, current state: {2}'
                    .format(state_name, state.FSM.preview_state, state.FSM.cur_state))

    def set_state(self, state_name):
        self.preview_state = self.cur_state
        self.cur_state = self.states[state_name]
        LOGGER.info('FSM method set_state state name: {0}'.format(state_name))

    def to_transition(self, to_trans):
        self.trans = self.transitions[to_trans]
        LOGGER.info('FSM method to_transition to trans: {0}'.format(to_trans))

    def execute(self):
        LOGGER.info('>> FSM execute')
        if self.trans:
            LOGGER.info('FSM execute trans: {0}'.format(self.trans.to_state))
            self.cur_state.exit()
            self.trans.execute()
            self.set_state(self.trans.to_state)
            self.cur_state.enter()
            self.trans = None
        self.cur_state.execute()

# --------- Static methods --------------


class Reader:

    @staticmethod
    def read_initial_temp(path):
        """ read start temperature. State Precooling """
        try:
            with open(path, mode='r') as file:
                reader = csv.reader(file)
                next(reader)
                data = [row for row in reader]
                file.close()
            if not data:  # if data is empty return zero 0 item
                data = [['0', '0', '0', '0']]
            temp = data[0]
            return temp[2]  # return start temperature
        except Exception as ex:
            LOGGER.error('Exception: {0}. Method: read_initial_temp'.format(ex))

    @staticmethod
    def read_config(path):
        """ read the config files """
        try:
            with open(path, mode='r') as config_file:
                reader = yaml.load(config_file)
                config_file.close()
                return reader
        except Exception as ex:
            LOGGER.error(ex)

    @staticmethod
    def read_precooling_csv(path, set_point_pressure_in_tank, set_point_temperature):
        """ read state precooling csv file """
        try:
            # open the csv file
            result = ''
            with open(path) as csv_file:
                reader = csv.reader(csv_file, delimiter=',')
                # header
                next(reader)
                preview_temperature = 0.0
                current_temperature = 0.0
                for row in reader:
                    # check if *csv file is empty
                    if not row:
                        result = 'to_precool'
                        LOGGER.info('{0} is empty'.format(path))
                        return result
                    cur_pressure = float(row[1])
                    current_temperature = float(row[2])
                    if cur_pressure > set_point_pressure_in_tank:
                        LOGGER.info('Pressure in tank: {0} mbar'.format(cur_pressure))
                        if preview_temperature == 0.0:
                            LOGGER.info('preview temperature is equals current temperature {0} K'
                                        .format(current_temperature))
                        elif preview_temperature >= current_temperature:
                            LOGGER.info('preview temperature {0} K >= current temperature {1} K'
                                        .format(preview_temperature, current_temperature))
                        else:
                            LOGGER.error('preview temperature {0} K < current temperature {1} K'
                                         .format(preview_temperature, current_temperature))

                    preview_temperature = current_temperature
                csv_file.close()
                if current_temperature >= float(set_point_temperature):
                    result = 'to_precool'
                    LOGGER.info('current temperature in Tank {0} K is greater that set point temperature {1} K.'
                                .format(current_temperature, set))
                else:
                    LOGGER.info('current temperature is {0} K'.format(current_temperature))
                    result = 'to_error'
        except Exception as ex:
            LOGGER.error('Exception: {0}. Method: read_precooling_csv'.format(ex))
            result = 'to_error'
        return result

    @staticmethod
    def get_current_pressure_and_temperature(path):
        """ get current pressure and temperature in tank for precooling state"""
        try:
            with open(path, mode='r') as f:
                reader = csv.reader(f, delimiter=',')
                data = [row for row in reader]
                last_line = []
                if not data:
                    last_line = ['0', '0', '0', '0']
                else:
                    for row in data:
                        last_line = row
                return last_line
        except Exception as ex:
            LOGGER.error('Exception: {0}. Method: get_current_pressure_and_temperature'.format(ex))
        finally:
            f.close()

    @staticmethod
    def get_pressure_difference(path):
        """ fill with helium state read the pressure difference in tank and check pOut"""
        try:
            with open(path, mode='r') as f:
                reader = csv.reader(f, delimiter= ',')
                data = [row for row in reader]
                last_line = ['0', '0', '0']
                for row in data:
                    last_line = row
            return last_line
        except Exception as ex:
            LOGGER.error('Exception: {0}. Method: get_pressure_difference'.format(ex))
        finally:
            f.close()

    @staticmethod
    def get_cooldown_values(path):
        """" cool down state read the pressure and temperature """
        try:
            with open(path, mode='r') as f:
                reader = csv.reader(f, delimiter=',')
                data = [row for row in reader]
                last_line = ['0', '0', '0', '0', '0', '0', '0']
                for row in data:
                    last_line = row
                return last_line
        except Exception as ex:
            LOGGER.info('Exception: {0}. Method: get_cooldown_values'.format(ex))
        finally:
            f.close()


class Writer:

    @staticmethod
    def write_csv(path, date_time, cur_pressure, cur_temp, set_point_temp, initial_temp):
        """ write the current pressure and temperature in tank. State Precooling """
        try:
            data = Reader.read_config('fsm/configuration/config.yml')
            init_temperature = float(initial_temp)
            if init_temperature == 0:
                init_temperature = cur_temp

            with open(path, mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                time = process_time()
                e = math.exp(-data['Precooling']['k'] * time)
                cur_temp = cur_temp
                cur_temp = cur_temp + (init_temperature - cur_temp) * e
                writer.writerow([date_time, cur_pressure, cur_temp, set_point_temp])
                LOGGER.info('date: {0}'
                            ', current pressure: {1} mbar'
                            ', current temperature: {2} K'
                            ', set-point temperature: {3} K'
                            .format(date_time
                                    , cur_pressure
                                    , cur_temp
                                    , set_point_temp))
            csv_file.close()
        except Exception as ex:
            LOGGER.error('Exception: {0}. Method: write_csv'.format(ex))

    @staticmethod
    def reset_csv_file():
        header_precooling = ['date'
                             , 'current pressure [mbar]'
                             , 'current temperature Tank [K]'
                             , 'set-point temperature Tank [K]']

        header_fillwithhelium = ['date'
                                 , 'pressure difference'
                                 , 'pOut']

        header_cooldown = ['date'
                           , 'current pressure pPreVac [mbar]'
                           , 'max pressure pPreVac [mbar]'
                           , 'current pressure pVac [mbar]'
                           , 'max pressure pVac [mbar]'
                           , 'current temperature isolation chamber [K]'
                           , 'set-point temperature isolation chamber Stage 1 [K]'
                           , 'set-point pressure isolation chamber Stage 1 [mbar]']

        # todo refresh for next csv files
        header_keep_temp_constant = ['']
        header_warm_up = ['']

        try:
            data = Reader.read_config('fsm/configuration/config.yml')
            precooldown_csv = data['FilePaths']['precooling_csv']
            fillwithhelium_csv = data['FilePaths']['fillwithhelium_csv']
            cooldown_csv = data['FilePaths']['cooldown_csv']
            with open(precooldown_csv, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header_precooling)
            f.close()
            with open(fillwithhelium_csv, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header_fillwithhelium)
            f.close()
            with open(cooldown_csv, mode='w', newline='') as f:
                writer = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(header_cooldown)
            f.close()
            LOGGER.info('Reset all csv files')
        except Exception as ex:
            LOGGER.info('Exception: {0}. Method: reset_csv_file'.format(ex))

    @staticmethod
    def write_fill_with_helium_csv_file(path, time, tank_pressure, current_pressure, pOut):
        """ write pressure difference and pOut values in fill with helium cav file"""
        try:
            with open(path, mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                pressure_difference = tank_pressure - current_pressure
                LOGGER.info('Calculate pressure difference in tank')
                LOGGER.info('pressure in tank {0} mbar - current pressure {1} mbar = pressure difference {2} mbar'
                            .format(tank_pressure, current_pressure, pressure_difference))
                writer.writerow([time, pressure_difference, pOut])
                LOGGER.info('date: {0}'
                            ', pressure difference: {1} mbar'
                            ', pOut: {2} mbar'.format(time
                                                      , pressure_difference
                                                      , pOut))
        except Exception as ex:
            LOGGER.error('Exception: {0}. Method: write_fill_with_helium_csv_file'.format(ex))
        finally:
            csv_file.close()

    @staticmethod
    def write_cooling_down_csv_file(path, time, pPreVac, max_pPreVac, pVac,
                                    max_pVac, curr_temp_isolation_chamber
                                    , temp_isolation_chamber_set_point, pressure_isolation_chamber_set_point):
        """ write the pPreVac, max pPreVac, pVac, max pVac,
        current tempertature in isolation chamber and the set-point temperature value in cooldown.csv file """
        try:
            with open(path, mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                writer.writerow([time, pPreVac, max_pPreVac, pVac, max_pVac
                                , curr_temp_isolation_chamber, temp_isolation_chamber_set_point
                                , pressure_isolation_chamber_set_point])
                LOGGER.info('date: {0}'
                            ', pPreVac: {1} mbar'
                            ', max pPreVac: {2} mbar'
                            ', pVac: {3} mbar'
                            ', max pVac: {4} mbar'
                            ', current temperature in isolation chamber: {5} K'
                            ', set-point temperature in isolation chamber: {6} K'
                            ', set-point pressure in isolation chamber: {7} mbar'
                            .format(time
                                    , pPreVac
                                    , max_pPreVac
                                    , pVac
                                    , max_pVac
                                    , curr_temp_isolation_chamber
                                    , temp_isolation_chamber_set_point
                                    , pressure_isolation_chamber_set_point))
        except Exception as ex:
            LOGGER.error('Exception: {0}. Method: write_cooling_down_csv_file'.format(ex))
        finally:
            csv_file.close()
