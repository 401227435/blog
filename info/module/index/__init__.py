# __init__ 只做包的初始化
from flask import Blueprint

index_blu = Blueprint('index', __name__)

from .view import *
