from flask import Flask

# https://github.com/401227435/blog.git

app=Flask(__name__)

@app.route('/index')
def index():
    return 'index'
if __name__=='__main__':
    app.run()
