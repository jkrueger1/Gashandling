from .cooling_down import CoolingDown
from .error import Error
from .fsm import FSM
from .fill_with_helium import FillWithHelium
from .initialize import Initialize
from .logging import MyLogger
from .measurement import MeasurementOfPrecooling, \
    FillLevelMeasurement, CooldownMeasurement
from .pre_cooling import Precooling
from .transition import Transition


Char = type("Char", (object, ), {})
""" base class """


class Cooler(Char):
    """ define all states and transitions """
    def __init__(self):
        self.log = MyLogger().get_logger()
        self.fsm = FSM(self)
        # States
        self.fsm.add_state("Initialize", Initialize(self.fsm))
        self.fsm.add_state("MeasurementOfPrecooling",
                           MeasurementOfPrecooling(self.fsm))
        self.fsm.add_state("Precooling", Precooling(self.fsm))
        self.fsm.add_state("FillWithHelium", FillWithHelium(self.fsm))
        self.fsm.add_state("FillLevelMeasurement",
                           FillLevelMeasurement(self.fsm))
        self.fsm.add_state("CoolingDown", CoolingDown(self.fsm))
        self.fsm.add_state("CooldownMeasurement",
                           CooldownMeasurement(self.fsm))
        self.fsm.add_state("Error", Error(self.fsm))
        # Transition
        self.fsm.add_transition("to_init", Transition("Initialize"))
        self.fsm.add_transition("to_measure_precooling",
                                Transition("MeasurementOfPrecooling"))
        self.fsm.add_transition("to_precool", Transition("Precooling"))
        self.fsm.add_transition("to_fill_helium", Transition("FillWithHelium"))
        self.fsm.add_transition("to_measure_fill_helium",
                                Transition("FillLevelMeasurement"))
        self.fsm.add_transition("to_cooldown", Transition("CoolingDown"))
        self.fsm.add_transition("to_measure_cooldown",
                                Transition("CooldownMeasurement"))
        self.fsm.add_transition("to_error", Transition("Error"))
        # start state
        self.fsm.set_state("Initialize")

    def execute(self):
        try:
            self.fsm.execute()
        except Exception as ex:
            self.log.error(ex)
