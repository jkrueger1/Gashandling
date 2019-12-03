from time import process_time

from fsm.common.Cooler import Cooler
from fsm.common.FSM import Reader, Writer
from fsm.common.logging import MyLogger

LOGGER = MyLogger().get_logger()
# DEBUG: Detailed information, typically of interest only when diagnosing problems.

# INFO: Confirmation that things are working as expected.

# WARNING: An indication that something unexpected happened,
# or indicative of some problem in the near future (e.g. ‘disk space low’).
# The software is still working as expected.

# ERROR: Due to a more serious problem, the software has not been able to perform some function.

# CRITICAL: A serious error, indicating that the program itself may be unable to continue running.

# todo at the start clear the *.csv files
if __name__ == "__main__":
    """ the main function """
# create a class CONTROLLER and there put the start logic
# cool down process
    Writer.reset_csv_file()
    cool = Cooler()
# ==================================================
    data = Reader.read_config('fsm/configuration/config.yml')
    # Global time interval for FMS
    time_interval = data['Main']['global_time_interval']
    # Running time of FSM in seconds
    global_running_time = data['Main']['global_running_time']
    while global_running_time > process_time():
        start_time = process_time()
        LOGGER.info('===> main in {0}'.format(process_time()))
        #
        while start_time + time_interval > process_time():
            pass
        cool.execute()
        LOGGER.info('<=== main out {0}'.format(process_time()))
# ========================================================

# temperature controller
# # =======================================================
# # .......
# # ========================================================

# warm-up process
# =======================================================
# .......
# ========================================================
    LOGGER.info('FINISH')
