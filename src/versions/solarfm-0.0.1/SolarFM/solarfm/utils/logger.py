# Python imports
import os, logging

# Application imports


class Logger:
    """
        Create a new logging object and return it.
        :note:
            NOSET     # Don't know the actual log level of this... (defaulting or literally none?)
            Log Levels (From least to most)
                Type      Value
                CRITICAL   50
                ERROR      40
                WARNING    30
                INFO       20
                DEBUG      10
        :param loggerName: Sets the name of the logger object. (Used in log lines)
        :param createFile: Whether we create a log file or just pump to terminal

        :return: the logging object we created
    """

    def __init__(self, config_path: str, _ch_log_lvl = logging.CRITICAL,  _fh_log_lvl = logging.INFO):
        self._CONFIG_PATH = config_path
        self.global_lvl   = logging.DEBUG  # Keep this at highest so that handlers can filter to their desired levels
        self.ch_log_lvl   = _ch_log_lvl    # Prety much the only one we ever change
        self.fh_log_lvl   = _fh_log_lvl

    def get_logger(self, loggerName: str = "NO_LOGGER_NAME_PASSED", createFile: bool = True) -> logging.Logger:
        log          = logging.getLogger(loggerName)
        log.setLevel(self.global_lvl)

        # Set our log output styles
        fFormatter   = logging.Formatter('[%(asctime)s] %(pathname)s:%(lineno)d %(levelname)s - %(message)s', '%m-%d %H:%M:%S')
        cFormatter   = logging.Formatter('%(pathname)s:%(lineno)d] %(levelname)s - %(message)s')

        ch = logging.StreamHandler()
        ch.setLevel(level=self.ch_log_lvl)
        ch.setFormatter(cFormatter)
        log.addHandler(ch)

        if createFile:
            folder = self._CONFIG_PATH
            file   = f"{folder}/application.log"

            if not os.path.exists(folder):
                os.mkdir(folder)

            fh = logging.FileHandler(file)
            fh.setLevel(level=self.fh_log_lvl)
            fh.setFormatter(fFormatter)
            log.addHandler(fh)

        return log
