# Python imports
import os, logging

# Application imports


class Logger:
    def __init__(self):
        pass

    def get_logger(self, loggerName = "NO_LOGGER_NAME_PASSED", createFile = True):
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

        globalLogLvl = logging.DEBUG    # Keep this at highest so that handlers can filter to their desired levels
        chLogLevel   = logging.CRITICAL # Prety musch the only one we change ever
        fhLogLevel   = logging.DEBUG
        log          = logging.getLogger(loggerName)
        log.setLevel(globalLogLvl)

        # Set our log output styles
        fFormatter   = logging.Formatter('[%(asctime)s] %(pathname)s:%(lineno)d %(levelname)s - %(message)s', '%m-%d %H:%M:%S')
        cFormatter   = logging.Formatter('%(pathname)s:%(lineno)d] %(levelname)s - %(message)s')

        ch = logging.StreamHandler()
        ch.setLevel(level=chLogLevel)
        ch.setFormatter(cFormatter)
        log.addHandler(ch)

        if createFile:
            folder = "logs"
            file   = folder + "/application.log"

            if not os.path.exists(folder):
                os.mkdir(folder)

            fh = logging.FileHandler(file)
            fh.setLevel(level=fhLogLevel)
            fh.setFormatter(fFormatter)
            log.addHandler(fh)

        return log
