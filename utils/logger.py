import logging

logging.basicConfig(
    filename="ai_system.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def log_info(message):
    logger.info(message)
    print(f"[INFO] {message}")

def log_warning(message):
    logger.warning(message)
    print(f"[WARNING] {message}")

def log_error(message):
    logger.error(message)
    print(f"[ERROR] {message}")