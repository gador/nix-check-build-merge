from nix_cbm.frontend import db


class Packages(db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    hydra_status = db.Column(db.Boolean())
    build_url = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime())
    last_checked = db.Column(db.DateTime())

    def __repr__(self) -> str:
        return "<Package {}>".format(self.name)
