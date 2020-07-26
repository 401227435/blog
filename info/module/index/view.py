# 在view.py中创建路由
from . import index_blu
import logging


@index_blu.route('/')
def index():
    # 启动使用日志
    logging.debug('这是一个debug日志')
    logging.info('这是一个info日志')
    logging.warning('这是一个warning日志')
    return '这是路由'
