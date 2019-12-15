
LOGGER = MyLogger().get_logger()


Char = type("Char", (object, ), {})
""" base class """


class Cooler(Char):
    """ define all states and transitions """
    def __init__(self):
        self.FSM = FSM(self)
        # States
        self.FSM.add_state("Initialize", Initialize(self.FSM))
        self.FSM.add_state("MeasurementOfPrecooling", MeasurementOfPrecooling(self.FSM))
        self.FSM.add_state("Precooling", Precooling(self.FSM))
        self.FSM.add_state("FillWithHelium", FillWithHelium(self.FSM))
        self.FSM.add_state("FillLevelMeasurement", FillLevelMeasurement(self.FSM))
        self.FSM.add_state("CoolingDown", CoolingDown(self.FSM))
        self.FSM.add_state("CooldownMeasurement", CooldownMeasurement(self.FSM))
        self.FSM.add_state("Error", Error(self.FSM))
        # Transition
        self.FSM.add_transition("to_init", Transition("Initialize"))
        self.FSM.add_transition("to_measure_precooling", Transition("MeasurementOfPrecooling"))
        self.FSM.add_transition("to_precool", Transition("Precooling"))
        self.FSM.add_transition("to_fill_helium", Transition("FillWithHelium"))
        self.FSM.add_transition("to_measure_fill_helium", Transition("FillLevelMeasurement"))
        self.FSM.add_transition("to_cooldown", Transition("CoolingDown"))
        self.FSM.add_transition("to_measure_cooldown", Transition("CooldownMeasurement"))
        self.FSM.add_transition("to_error", Transition("Error"))
        # start state
        self.FSM.set_state("Initialize")

    def execute(self):
        try:
            self.FSM.execute()
        except Exception as ex:
            LOGGER.error(ex)
