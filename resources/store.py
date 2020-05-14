from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, fresh_jwt_required
from marshmallow import ValidationError

from models.store_model import StoreModel
from schemas.store import StoreSchema

store_schema = StoreSchema()
store_list_schema = StoreSchema(many=True)


class Store(Resource):
    @classmethod
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if not store:
            return {"Message": f"Store: '{name}' was not found"}, 404
        return store_schema.dump(store)

    @classmethod
    @jwt_required
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return {"Message": f"Store: '{name}' already created"}, 400

        store = StoreModel(name=name)

        try:
            store.save_to_db()
        except ValidationError as err:
            return err.messages, 500
        return store_schema.dump(store), 201

    @classmethod
    @fresh_jwt_required
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            try:
                store.delete_from_db()
                return {"Message": f"Store: '{name}' deleted", }
            except:
                return {"Message": "Delete the store's items first"}, 400
        else:
            return {"Message": f"Store: '{name}' was not found"}, 404


class Stores(Resource):
    @classmethod
    def get(cls):
        stores = store_list_schema.dump(StoreModel.find_all())
        return {"Stores": stores}
