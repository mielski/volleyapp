from flask import Flask
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
app.secret_key = 'dev'

bootstrap = Bootstrap5(app)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
