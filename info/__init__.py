# 10.拆功能加载内容
# 快速导包 alt + enter
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import config
from info.module.index import index_blu

# 初始化SQLAlchemy
db = SQLAlchemy()


# 14 添加日志系统
def create_log():
    logging.basicConfig(level=logging.DEBUG)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


# 工厂方式创建好app 将其返回出去
def create_app(config_name):
    """通过传入不同的配置名字，初始化其对应配置的应用实例"""
    # 项目一跑起来就开启日志
    create_log()
    app = Flask(__name__)
    # 加载配置
    # 使用工厂模式
    app.config.from_object(config[config_name])
    # 加载数据库调用SQLAlchemy内部初始app SQLAlchemy(app)
    db.init_app(app)
    # 加载redis
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    # 5 添加csrf
    CSRFProtect(app)
    # 加载session
    Session(app)

    # 添加 index 路由
    app.register_blueprint(index_blu)
    return app



