import logging
import colorlog

# Tạo một logger mới với cấu hình màu sắc
logger = colorlog.getLogger()
logger.setLevel(logging.INFO)

# Tạo định dạng màu cho các thông điệp log
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        'DEBUG': 'reset',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
)

# Tạo một handler mới để định dạng log và thêm vào logger
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
