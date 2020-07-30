# 在view.py中创建路由
from . import index_blu
import logging
from info import redis_store
from flask import render_template, current_app


# 给当前的主页返回一个图标
@index_blu.route('/favicon.ico')
def get_favicon():
    # 将本地资源图片返还给浏览器
    # current_app 等价于 app =Flask（__name__）
    # send_static_file 将静态资源图片返回给浏览器
    return current_app.send_static_file('news/favicon.ico')


# 由主页路由渲染主页
@index_blu.route('/')
def index():
    return render_template('news/index.html')