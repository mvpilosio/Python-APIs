from ma import ma
from models.items_model import ItemModel
from models.store_model import StoreModel


class ItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ItemModel
        load_only = ("store",)
        dump_only = ("id",)
        include_fk = True
