from nix_cbm.frontend import db


class Packages(db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    hydra_status = db.Column(db.Boolean())
    build_url = db.Column(db.String(128))
    arch = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime())
    last_checked = db.Column(db.DateTime())

    def __repr__(self) -> str:
        return "<Package {}>".format(self.name)


class PersistentConfig(db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    maintainer = db.Column(db.String(64), index=True)
    nixpkgs_path = db.Column(db.String(256))
    # comma, separated list, just like the environment variable
    archs_to_check = db.Column(db.String(256))

    def __repr__(self) -> str:
        return f"<Maintainer {self.maintainer}, Path {self.nixpkgs_path}, Archs {self.archs_to_check}>"
