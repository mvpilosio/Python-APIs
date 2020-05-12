import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                jwt_required,
                                jwt_refresh_token_required,
                                get_jwt_identity,
                                fresh_jwt_required,
                                get_raw_jwt)
from werkzeug.security import safe_str_cmp

from models.user_model import UserModel
from blacklist import BLACKLIST

_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    'username', type=str, required=True, help='Required field'
)
_user_parser.add_argument(
    'password', type=str, required=True, help='Required field'
)


class UsersRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"Message": f"Username '{data['username']}' already created"}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {"Message": "Username created"}, 201


class Users(Resource):
    def get(self):
        return {"Users": [user.json() for user in UserModel.find_all()]}


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"Message": f"User id: {user_id} not found"}, 404
        return user.json()

    @fresh_jwt_required
    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"Message": f"User id: {user_id} not found"}, 404
        else:
            try:
                user.delete_from_db()
                return {"Message": "User deleted"}
            except:
                return {"Message": "Something went wrong"}, 500


class UserLogin(Resource):
    @classmethod
    def post(cls):
        # get data from parser
        request_data = _user_parser.parse_args()
        # find user in db
        user = UserModel.find_by_username(request_data['username'])
        # check pass
        if user and safe_str_cmp(user.password, request_data['password']):
            # create access token
            access_token = create_access_token(identity=user.id, fresh=True)
            # create refresh token
            refresh_token = create_refresh_token(user.id)
            # return them
            return {
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 200
        return {"Message": "Invalid credentials"}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']  # jti == JWT ID
        BLACKLIST.add(jti)
        return {"Message": "Logged out successfully"}


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}
