from app.utils.logger import *
from config.mas_config import *
from gevent.pywsgi import WSGIServer

from app import create_app    

if __name__ == "__main__":
    
    try:
        system_logger_agent = Logger('server_logger', info_flag = True)
        system_logger = system_logger_agent.setup_logger('server_logger', os.path.join(LOG_PATH, 'system.log'), 'INFO')
    
        app = create_app()
        app_server = WSGIServer(('0.0.0.0', 7000), app)
        
        logging.info("The flask app has been started!")
        system_logger_agent.start_logging(system_logger, 'The server has started')
        app_server.serve_forever()
           
    except Exception as e:
        
        system_logger_agent.start_logging(system_logger, 'Exception - ' + str(e))

    except KeyboardInterrupt as e:
        
        system_logger_agent.start_logging(system_logger, 'Keyboard Interrupt')
