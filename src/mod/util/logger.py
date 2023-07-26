import logging

def setup_logger(log_file='LFM_bot.log', level=logging.DEBUG):
    # 로거 생성
    logger = logging.getLogger('LFM_bot')
    logger.setLevel(level)

    # 파일 핸들러 생성
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    # 콘솔 핸들러 생성
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 로그 메시지 포맷 설정
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 핸들러를 로거에 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()