"""
Module for logging
"""
import logging
from logging import handlers
import sys
import os

console_log_level = None


def log_message(log_level, logger_name, logfilepath=None, logfilename=None):
    """
    This method is responsible to genrate logs during execution on console as well as in logfile.
    Log levels can be "debug" , "info", "error"
    """
    if logfilepath is None:
        logfilepath = os.getcwd() + os.path.sep + "logs"
        if not os.path.exists(logfilepath):
            os.mkdir(logfilepath)
    if logfilename is None:
        logfilename = "swagger_logs.log"

    logfile = logfilepath + os.path.sep + logfilename
    print(logfile)
    # Fomatter
    custom_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    # File Logging
    log = logging.getLogger(logger_name)
    log.setLevel(logging.DEBUG)
    file_handle = handlers.RotatingFileHandler(
        logfile, maxBytes=(1048576 * 5), backupCount=10)
    file_handle.setFormatter(custom_format)
    log.addHandler(file_handle)
    # Console Logging
    console_handle = logging.StreamHandler(sys.stdout)
    log = logging.getLogger(logger_name)
    console_handle.setLevel(getattr(logging, log_level))
    console_handle.setFormatter(custom_format)
    log.addHandler(console_handle)
    return log
