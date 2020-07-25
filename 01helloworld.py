from flask import Flask

app=Flask(__name__)
@app.route('/')
def indexhome():
    return 'hello world'



@app.route('/index')
def index():
    return 'index'
if __name__=='__main__':
    app.run()
