from flask_restful import Resource
from flask import request
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                jwt_required,
                                jwt_refresh_token_required,
                                get_jwt_identity,
                                fresh_jwt_required,
                                get_raw_jwt)
from werkzeug.security import safe_str_cmp
from marshmallow import ValidationError

from models.user_model import UserModel
from blacklist import BLACKLIST
from schemas.user import UserSchema

user_schema = UserSchema()
user__list_schema = UserSchema(many=True)


class UsersRegister(Resource):
    @classmethod
    def post(cls):
        try:
            user = user_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        if UserModel.find_by_username(user.username):
            return {"Message": f"Username '{user.username}' already created"}, 400

        user.save_to_db()

        return {"Message": "Username created"}, 201


class Users(Resource):
    @classmethod
    def get(cls):
        users = user__list_schema.dump(UserModel.find_all())
        return {"Users": users}


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"Message": f"User id: {user_id} not found"}, 404
        return user_schema.dump(user)

    @classmethod
    @fresh_jwt_required
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"Message": f"User id: {user_id} not found"}, 404
        else:
            try:
                user.delete_from_db()
                return {"Message": f"User: {user_id} deleted"}
            except ValidationError as err:
                return err.messages, 400


class UserLogin(Resource):
    @classmethod
    def post(cls):
        # get data from parser
        try:
            user_data = user_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        # find user in db
        user = UserModel.find_by_username(user_data.username)
        # check pass
        if user and safe_str_cmp(user.password, user_data.password):
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
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()['jti']  # jti == JWT ID
        BLACKLIST.add(jti)
        return {"Message": "Logged out successfully"}


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}
