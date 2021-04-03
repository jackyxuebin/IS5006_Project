from threading import Lock
import logging

class Logger:
    """
    Prints all the logs in an orderly fashion (using mutexes)
    """
    def __init__(self, name, debug_flag = False, info_flag = False, warning_flag = False, error_flag = False, critical_flag = False):
        self.name = name

        # all the flags are turned off by default
        self.debug_flag = debug_flag
        self.info_flag = info_flag
        self.warning_flag = warning_flag
        self.error_flag = error_flag
        self.critical_flag = critical_flag
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%y/%Y %I:%M:%S %p')

    def setup_logger(self, logger_name, log_file_path, level):
        """To setup as many loggers as you want"""
        
        if(level == 'DEBUG'):
            self.debug_flag = True
            level = logging.DEBUG
        elif(level == 'INFO'):
            self.info_flag = True
            level = logging.INFO
        elif(level == 'WARNING'):
            self.warning_flag = True
            level = logging.WARNING
        elif(level == 'ERROR'):
            self.error_flag = True
            level = logging.ERROR            
        elif(level == 'CRITICAL'):
            self.critical_flag = True
            level = logging.CRITICAL 

        handler = logging.FileHandler(log_file_path)        
        handler.setFormatter(self.formatter)

        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        logger.addHandler(handler)
        return logger

    def start_logging(self, logger, msg):
        
        if(self.debug_flag):
            logger.debug(msg)
        elif(self.info_flag):
            logger.info(msg)
        elif(self.warning_flag):
            logger.warning(msg)
        elif(self.error_flag):
            logger.error(msg)        
        elif(self.critical_flag):
            logger.critical(msg)

##if __name__ == '__main__':
##
##    logger_agent = Logger('google_api_agent')
##    
##    # first file logger
##    loggerX = logger_agent.setup_logger('first_logger', './log/first_logfile.log', 'INFO')
##    logger_agent.start_logging(loggerX, 'This is just info message h')
##
##    # second file logger
##    loggerY = logger_agent.setup_logger('second_logger', './log/second_logfile.log','DEBUG')
##    logger_agent.start_logging(loggerY, 'This is just info message y')


