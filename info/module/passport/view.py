import re
import random

from info.libs.yuntongxun.sms import CCP
from info.models import User
from . import passport_blu
from flask import request, jsonify, make_response
from info.response_code import *
from info.utils.captcha.captcha import captcha
from info import redis_store, db
from info.constants import *

'''
    写路由的步骤
        1.获取数据（获取参数）
        2.验证数据为空 手机号码是否符合规范
        3.将数据保存起来
        4.发送成功或者失败信息
'''

# 创建一个注册的路由
@passport_blu.route('/register',methods=['POST'])
def register():
    # 注册
    '''
    步骤
        1. 获取传递过来数据（手机号码 短信验证码  密码）
        2. 看你的短信验证码和redis中短信验证码是否一致
        3. 提交到数据库中mysql中存储起来
        4.放回数据给浏览器告诉注册成功和注册失败

    '''
    #  1. 获取传递过来数据（手机号码 短信验证码  密码）
    req_dir = request.json
    mobile = req_dir['mobile']
    smscode = req_dir['smscode']
    password = req_dir['password']
    # 2. 看你的短信验证码和redis中短信验证码是否一致
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    # 判断手机号码
    if not re.match(r'^1[3-9]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机格式不对')
    # 判断redis中的手机号码的验证短信是否一致
    # redis_store.set('sms_code:%s' % mobile, sms_rand_id, SMS_CODE_REDIS_EXPIRES)
    sms_rand_id = redis_store.get('sms_code:%s' % mobile)
    # 判断sms_rand_id 为不为空
    if not sms_rand_id:
        return jsonify(errno=RET.PARAMERR, errmsg='验证码过期')
    # 判断传递过来的smscode不一致
    if sms_rand_id.upper() != smscode.upper():
        return jsonify(errno=RET.PARAMERR, errmsg='验证码过期重新设置验证码')
    # Todo 如果学的不错 可以从mysql中找到手机号 如果有这个手机表示注册过 如果没有表示新用户
    # 3. 提交到数据库中mysql中存储起来
    user = User()
    # 将数据添加到User中
    user.mobile = mobile
    user.nick_name = mobile
    user.password = password
    # 将数据添加到事务中
    db.session.add(user)
    # 将事务提交到数据库中
    db.session.commit()
    #提交数据以后返回结果
    return jsonify(errno=RET.OK,errmsg='注册成功')


# 创建一个发送短信的验证码的路由
@passport_blu.route('/sms_code', methods=['POST'])
def sms_code():
    """
    步骤：
        1.收集手机号码 验证码image_code 验证码图片中的内容image_code_id
        2.校验手机 验证码 验证码过期
        3.比对验证码和 redis是否相同       手机号码是否存在（放一下）
        4.通过云通讯发送验证码给手机
        5.并把验证码保存一下
        6.告诉页面发送成功
    """
    '''
    mobile	string	是	手机号
    image_code	string	是	用户输入的图片验证码内容
    image_code_id	string	是	真实图片验证码编号
    '''
    #  1.收集手机号码 验证码image_code 验证码图片中的内容image_code_id
    # 这种方式比较繁琐 request.data.get['mobile'] request.data.get['image_code']
    req_dic = request.json
    # 将获取好的参数接受一下
    mobile = req_dic['mobile']
    image_code = req_dic['image_code']
    image_code_id = req_dic['image_code_id']
    # 验证手机 验证 的信息
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    # 判断手机号码
    if not re.match(r'^1[3-9]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机格式不对')
    # 3比对redis
    # 获取redis存储的验证码 获取result_image_code_id（格式输出的问题）
    #  decode_responses=True 保证redis获取数据的时候是一个字符串
    result_image_code_id = redis_store.get('image_code:%s' % image_code_id)
    # 判断数据是否过期
    if not result_image_code_id:
        return jsonify(errno=RET.PARAMERR, errmsg='验证码过期重新设置验证码')
    # 判断验证码是否和redis的相同
    # result_image_code_id image_code
    if result_image_code_id.upper() != image_code.upper():
        return jsonify(errno=RET.PARAMERR, errmsg='验证码过期重新设置验证码')
    # 4 将验证码发送给手机 1 2   0004  0010
    sms_rand_id = '%04d' % random.randint(0, 9999)
    # 将生成好的sms_rand_id 通过运通讯发送出去
    # mobile= 手机号码 sms_rand_id 验证码 SMS_CODE_REDIS_EXPIRES 过期时间 1以短信的形式发送过去
    res = CCP().send_template_sms(mobile, [sms_rand_id, SMS_CODE_REDIS_EXPIRES], 1)
    # 判断res的参数 0 成功 -1 失败
    if res != 0:
        return jsonify(errno=RET.PARAMERR, errmsg='手机发送验证码失败')
    # sms_rand_id存储到数据库中redis mysql
    redis_store.set('sms_code:%s' % mobile, sms_rand_id, SMS_CODE_REDIS_EXPIRES)
    # 6将成功的数据发给浏览器
    return jsonify(errno=RET.OK, errmsg='发送短信成功')


# 创建一个路由用来创建验证码
@passport_blu.route('/image_code')
def image_code():
    # 根据浏览器发送过来的随机数生成图片
    # http://127.0.0.1:5000/passport/image_code?image_code_id=8fb0c3dc-5f4b-4664-9116-0b5c08837b0e
    # 获取随机数#
    # 1.判断随机数不为空
    image_code_id = request.args.get('image_code_id')
    if not image_code_id:
        # 发送一条错误信息  错误信息一般由错误编码和错误信息组成  404    msg 页面找不到
        return jsonify(errno=RET.PARAMERR, errmsg='随机参数错误')
    # 2.生成图片
    # name 图片名称 text图片的内容 content就是我们的真实图片
    name, text, content = captcha.generate_captcha()
    # 3. 将生成好的图片内容存储到redis中 图片失效时间
    redis_store.set('image_code:%s' % image_code_id, text, IMAGE_CODE_REDIS_EXPIRES)
    # 4 将生成好的图片返回给浏览器 text/html(浏览器默认格式) 将图片返回浏览器
    response = make_response(content)
    # response里面设置请求头 通知浏览器以什么样的方式解析
    response.headers['Content-Type'] = 'image/jpg'
    return response
