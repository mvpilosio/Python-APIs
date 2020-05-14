from flask_restful import Resource
from flask import request
from flask_jwt_extended import (jwt_required, fresh_jwt_required)
from marshmallow import ValidationError

from models.items_model import ItemModel
from schemas.item import ItemSchema

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):
    @classmethod
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item)
        return {"Message": "Item not found"}, 404

    @classmethod
    @jwt_required
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return {"Message": f"Item: '{name}' already created"}, 400

        item_json = request.get_json()
        item_json["name"] = name
        item_load = item_schema.load(item_json)
        item = ItemModel(**item_json)
        try:
            item.save_to_db()
        except ValidationError as err:
            return err.messages, 500

        return item_schema.dump(item_load), 201

    @classmethod
    @jwt_required
    def put(cls, name: str):
        item_json = request.get_json()
        item = ItemModel.find_by_name(name)

        if item:
            item.price = item_json['price']
        else:
            item_json["name"] = name
            item = ItemModel(**item_json)
            try:
                item_schema.load(item_json)
            except ValidationError as err:
                return err.messages, 400

        item.save_to_db()
        return item_schema.dump(item)

    @classmethod
    @fresh_jwt_required
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if not item:
            return "Item not found", 404
        item.delete_from_db()
        return {"Message": "Item deleted"}


class Items(Resource):
    @classmethod
    def get(cls):
        items = item_list_schema.dump(ItemModel.find_all())
        return {"Items": items}

