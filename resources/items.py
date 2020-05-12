from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import(jwt_required,
                               get_jwt_claims,
                               jwt_optional,
                               get_jwt_identity,
                               fresh_jwt_required)

from models.items_model import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help='This field must be included')
    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help='This field must be included')

    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {"Message": "Item not found"}, 404

    @jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {"Message": f"Item: '{name}' already created"}, 400

        request_data = Item.parser.parse_args()
        item = ItemModel(name, **request_data)
        try:
            item.save_to_db()
        except:
            return {"Message": "Something went wrong"}, 500
        return item.json(), 201

    @jwt_required
    def put(self, name):
        request_data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(
                name, **request_data)
        else:
            item.price = request_data['price']

        item.save_to_db()
        return item.json()

    @fresh_jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims["is_admin"]:
            return {"Message": "Require Admin grants"}, 401

        item = ItemModel.find_by_name(name)
        if not item:
            return "Item not found", 404
        item.delete_from_db()
        return {"Message": "Item deleted"}


class Items(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        if user_id:
            return {"Items": items}
        return {"Items": [item['name']for item in items],
                "Message": "For more data, login adding the 'Authorization' header"}
        # return {"Items": list(map(lambda x:x.json(), ItemModel.query.all()))}
