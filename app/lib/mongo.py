from app import mongo
from bson import ObjectId
from app.lib.auth import current_user_info

def get_mongo_data(collection, search=None, start=None, end=None, limit=None, order=None):

    criteria = {"project": {"$in": current_user_info.viewable_projects_id}}
    time_range = {}

    if search:
        criteria.update(search)

    if start:
        time_range.update({"$gt": str(start)})

    if end:
        time_range.update({"$lt": str(end)})

    if time_range:
        criteria.update({"timestamp": time_range})

    data = mongo.db[collection].find(criteria)

    if limit:
        data = data.limit(limit)

    if order:
        data = data.sort(order)

    res = list(data) if data else []

    return res


def update_mongo_data(collection, mid, **data):

    mongo.db[collection].update({"_id": ObjectId(mid)}, {'$set': data})
