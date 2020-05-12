from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import UsersRegister, Users, User, UserLogin, TokenRefresh, UserLogout
from resources.items import Item, Items
from resources.store import Store, Stores
from blacklist import BLACKLIST


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

app.secret_key = "test"  # app.config["JWT_SECRET_KEY"]
api = Api(app)


@app.before_first_request
def creat_tables():
    db.create_all()


jwt = JWTManager(app)


@jwt.user_claims_loader
def user_claims_to_jwt(identity):
    if identity == 1:
        return {"is_admin": True}
    return {"is_admin": False}


@jwt.token_in_blacklist_loader
def token_in_blacklist_callback(decrypted_token):
    return decrypted_token['identity'] in BLACKLIST


@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        "Message": "Your token has expired. You need to re-login",
        "Error": "expired_token"
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        "Message": "Verification failed. Please login",
        "Error": "invalid_token"
    }), 401


@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({
        "Message": "Request needs authorization. Please login",
        "Error": "authorization_required"
    }), 401


@jwt.needs_fresh_token_loader
def needs_fresh_token_callback():
    return jsonify({
        "Message": "For security, we need you to enter your credentials again. Please login /login",
        "Error": "need_access_token"
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        "Message": "Your token has been revoked. Please login",
        "Error": "token_revoked"
    }), 401


api.add_resource(Item, '/items/<string:name>')
api.add_resource(Items, '/items')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(Stores, '/stores')

api.add_resource(UsersRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(Users, '/users')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(TokenRefresh, '/refresh')


if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=3000, debug=True)
