"""Gabarito do exercício 5."""
from bson import Decimal128
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError


class ProductStore:
    def __init__(self, collection):
        self.collection = collection

    def ensure_indexes(self):
        self.collection.create_index("sku", unique=True)

    @staticmethod
    def _out(doc):
        if doc is not None and isinstance(doc.get("price"), Decimal128):
            doc["price"] = doc["price"].to_decimal()
        return doc

    def add(self, sku, name, price, stock=0):
        if stock < 0:
            raise ValueError("stock >= 0")
        doc = {"sku": sku, "name": name, "price": Decimal128(price), "stock": stock}
        try:
            doc["_id"] = self.collection.insert_one(doc).inserted_id
        except DuplicateKeyError as error:
            raise ValueError(f"SKU repetido: {sku!r}") from error
        return self._out(doc)

    def get(self, sku):
        return self._out(self.collection.find_one({"sku": sku}))

    def remove_stock(self, sku, quantity):
        if quantity < 1:
            raise ValueError("quantity >= 1")
        updated = self.collection.find_one_and_update(
            {"sku": sku, "stock": {"$gte": quantity}}, {"$inc": {"stock": -quantity}}, return_document=ReturnDocument.AFTER)
        if updated is not None:
            return updated["stock"]
        if self.collection.count_documents({"sku": sku}, limit=1) == 0:
            raise KeyError(sku)
        raise ValueError("estoque insuficiente")

    def page(self, after_id=None, limit=3):
        query = {} if after_id is None else {"_id": {"$gt": after_id}}
        docs = list(self.collection.find(query).sort("_id", 1).limit(limit + 1))
        has_more = len(docs) > limit
        docs = [self._out(d) for d in docs[:limit]]
        return docs, (docs[-1]["_id"] if has_more else None)
