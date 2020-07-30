from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import Config
from info import create_app, db, models


'''
步骤：
    1.初始化
    2.将配置比如数据库等配置文件都写在Config类中
    3.添加数据库
    4.添加redis
    5.添加csrf保护
    6.添加session 并且存储在redis中
    7.添加命令行操作
    8.添加数据库迁移
    9.拆config配置文件
    10.拆功能加载内容
    11.拆路由变成蓝图
    12.添加日志系统
'''
# 创建 app，并传入配置模式：development / production
app = create_app('dev')

# Flask-script
manager = Manager(app)
# 数据库迁移
Migrate(app, db)
manager.add_command('db', MigrateCommand)


# @app.route('/index')
# def index():
#     return 'index'


if __name__ == '__main__':
    manager.run()
# python manage.py runserver