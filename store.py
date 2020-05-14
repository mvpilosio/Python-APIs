from ma import ma
from models.items_model import ItemModel
from models.store_model import StoreModel
from schemas.item import ItemSchema


class StoreSchema(ma.SQLAlchemyAutoSchema):
    items = ma.Nested(ItemSchema, many=True)

    class Meta:
        model = StoreModel
        dump_only = ("id",)
        include_fk = True
