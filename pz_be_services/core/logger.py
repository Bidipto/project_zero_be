import logging
import os
from colorlog import ColoredFormatter  

def get_logger(name: str = "health_logger", db : bool = False) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    log_dir_path = os.path.join("pz_be_services\logs")

    if not logger.handlers:

        os.makedirs("pz_be_services\logs", exist_ok=True)

        if db == True:
            filename = "db.log"
        else:
            filename = "app.log"

        file_path = os.path.join(log_dir_path, filename)

        fh = logging.FileHandler(file_path)
        fh.setLevel(logging.DEBUG)

        formatter = ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            
        )
        fh.setFormatter(formatter)

        logger.addHandler(fh)

    return logger