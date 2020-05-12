from flask_restful import Resource
from flask_jwt_extended import jwt_required, fresh_jwt_required

from models.store_model import StoreModel


class Store(Resource):
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        return {"Message": f"Store: '{name}' was not found"}, 404

    @jwt_required
    def post(self, name):
        if StoreModel.find_by_name(name):
            return {"Message": f"Store: '{name}' already created"}, 400

        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {"Message": "Something went wrong"}, 500
        return store.json(), 201

    @fresh_jwt_required
    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            try:
                store.delete_from_db()
                return {"Message": f"Store: '{name}' deleted"}
            except:
                return {"Message": "Something went wrong"}, 500
        else:
            return {"Message": f"Store: '{name}' was not found"}, 404


class Stores(Resource):
    def get(self):
        return {"Stores": [store.json() for store in StoreModel.find_all()]}
