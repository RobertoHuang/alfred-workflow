#!/usr/bin/python
# encoding: utf-8

import logging
import traceback
import logging.handlers
import os

logger = None
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


def _get_log_file_path():
    """
    获取日志文件路径（相对于项目根目录）
    
    返回:
        日志文件的绝对路径
    """
    # 获取当前文件所在目录（utils/）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录（上一级目录）
    project_root = os.path.dirname(current_dir)
    # 返回日志文件路径
    return os.path.join(project_root, 'alfred.log')

class LogUtils:
    def init():
        """
        初始化日志记录器
        """
        global logger
        logger = logging.getLogger('alfred')
        logger.setLevel(logging.DEBUG)
        
        log_file_path = _get_log_file_path()
        rotating_file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=1,
            encoding='utf-8'
        )
        rotating_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.handlers.clear()
        logger.addHandler(rotating_file_handler)

    def error(msg, extra={}):
        """
        记录错误日志
        
        参数:
            msg: 错误消息
            extra: 额外信息（可选）
        """
        s = traceback.format_exc()
        if logger is None:
            LogUtils.init()
        logger.error("{} : {}".format(msg, s), extra=extra)

    def info(msg, extra={}):
        """
        记录信息日志
        
        参数:
            msg: 信息消息
            extra: 额外信息（可选）
        """
        if logger is None:
            LogUtils.init()
        logger.info(msg, exc_info=True)