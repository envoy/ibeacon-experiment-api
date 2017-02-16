from flask import Flask
app = Flask(__name__)


@app.route("/sign-up")
def sign_up():
    # TODO: create user record for iPhone
    return 'FIXME'


@app.route("/upload-log")
def upload_log():
    # TODO: handle uploaded log file from iPhone
    return 'FIXME'


@app.route("/i-am-here")
def i_am_here():
    # TODO: create an i am here record from iPad
    return 'FIXME'


if __name__ == "__main__":
    app.run()
