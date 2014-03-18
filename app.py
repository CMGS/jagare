#!/usr/bin/python
#coding:utf-8

import logging
import config
config.init_config('config.yaml', 'local_config.yaml')

from flask import Flask
from views import init_view
from libs.colorlog import ColorizingStreamHandler

app = Flask(__name__)
app.debug = config.DEBUG
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

logging.StreamHandler = ColorizingStreamHandler
logging.BASIC_FORMAT = "%(asctime)s [%(name)s] %(message)s"
logging.basicConfig(level=logging.DEBUG if config.DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

init_view(app)

@app.route('/')
def index():
    '''
jagare 首页，返回描述文字以及当前运行版本号。
    '''
    return "This is Jägare, the git backend server of titan."

