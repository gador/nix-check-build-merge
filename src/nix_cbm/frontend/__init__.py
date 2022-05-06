from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    # this needs to be offloaded to a different worker
    return render_template("index.html", maintainer="")
