from threading import Lock

class Logger:
    """
    Prints all the logs in an orderly fashion (using mutexes)
    """
    @staticmethod
    def info(string):
        Logger.lock.acquire()
        print(string)
        Logger.lock.release()
    
