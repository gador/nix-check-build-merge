from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from nix_cbm.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.route("/")
def index():
    # this needs to be offloaded to a different worker
    return render_template("index.html", maintainer="")
