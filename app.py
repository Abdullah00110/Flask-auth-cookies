import datetime
from flask import Flask, jsonify, request, abort, session, make_response,g
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisissecret'


db = SQLAlchemy(app)
ma = Marshmallow(app)


class User(db.Model):
    __tabelname__ = "user"
    __table_args__ = (
        db.CheckConstraint(
            "length(name) >= 3 AND length(name) <= 64", name="user_name_check"
        ),
        db.CheckConstraint(
            "length(username) >= 3 AND length(username) <= 32",
            name="user_username_check",
        ),
        db.CheckConstraint(
            "length(email) >= 3 AND length(email) <= 64", name="user_email_check"
        ),
        
        db.UniqueConstraint("email")
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    username = db.Column(db.String(150))
    email = db.Column(db.String(150) , unique = True)
    _password = db.Column(db.String(150))

    @property
    def password(self):
        raise AttributeError("cannot read password")
    
    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self._password, password)
    

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    username = fields.Str()
    email = fields.Str()


def token_required(f):

    @wraps(f)

    def decorated(*args , **kwargs):
        token = None
        token = request.cookies.cookies.get('currentuser')

        if not token:
            return jsonify({
                'message' : 'Token is missing'
            })
        
       