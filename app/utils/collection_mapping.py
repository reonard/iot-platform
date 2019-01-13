from app.lib.const import MONGO_METRIC_COLLECTION


def get_collection(interval):

    collection = MONGO_METRIC_COLLECTION

    if interval:
        collection = collection + '_' + str(interval)

    return collection
