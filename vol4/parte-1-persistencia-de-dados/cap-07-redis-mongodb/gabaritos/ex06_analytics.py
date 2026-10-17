"""Gabarito do exercício 6."""


def sales_by_category(collection, min_amount=0):
    pipeline = [
        {"$match": {"amount": {"$gte": min_amount}}},
        {"$group": {"_id": "$category", "total": {"$sum": "$amount"}, "n": {"$sum": 1}}},
        {"$sort": {"total": -1, "_id": 1}},
    ]
    return [(row["_id"], row["total"], row["n"]) for row in collection.aggregate(pipeline)]


def top_customers(collection, n=3):
    if n < 1:
        raise ValueError("n >= 1")
    pipeline = [
        {"$group": {"_id": "$customer", "total": {"$sum": "$amount"}}},
        {"$sort": {"total": -1, "_id": 1}},
        {"$limit": n},
    ]
    return [(row["_id"], row["total"]) for row in collection.aggregate(pipeline)]


def ensure_ttl_index(collection, field, seconds):
    if seconds < 0:
        raise ValueError("seconds >= 0")
    for index in collection.list_indexes():
        if list(index["key"].keys()) == [field] and index.get("expireAfterSeconds") == seconds:
            return False
    collection.create_index(field, expireAfterSeconds=seconds)
    return True


def winning_stages(collection, query):
    node = collection.find(query).explain()["queryPlanner"]["winningPlan"]
    stages = []
    while node:
        stages.append(node["stage"])
        node = node.get("inputStage")
    return stages
