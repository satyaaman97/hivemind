from pymongo import MongoClient
import os

DB_NAME = "WSB"
DB_COLLECTION = "historical"


class Mongo(MongoClient):
    def __init__(self):
        super().__init__(
            host=os.environ["MONGODB_SERVICE_HOST"],
            port=int(os.environ["MONGODB_SERVICE_PORT"]),
            username=os.environ["MONGO_ROOT_USERNAME"],
            password=os.environ["MONGO_ROOT_PASSWORD"],
            authSource="admin"
        )
        self.collection = self[DB_NAME][DB_COLLECTION]

    def get_comment(self, id):
        fields = (
            "score", "body", "created_utc", "distinguished", "id", "link_id", "parent_id", "stickied", "gilded",
            "controversiality", "downs", "total_awards_received", "ups", 'pos', 'neg', 'neu', 'tickers'
        )
        project_fields = {field: f'$comments.{field}' for field in fields}
        project_fields['_id'] = 0
        return list(self.collection.aggregate([
            {'$match': {"comments.id": id}},
            {'$unwind': "$comments"},
            {'$match': {"comments.id": id}},
            {'$project': project_fields}
        ]))[0]

    def get_submission(self, id, include_comments=False):
        if include_comments:
            submission = self.collection.find_one({"id": id}, {"_id": 0})
        else:
            submission = self.collection.find_one(
                {"id": id}, {"comments": 0, "_id": 0})
        return submission

    def add_fields_to_comment(self, id, fields):
        comment = self.get_comment(id)
        comment.update(fields)
        result = self.collection.update_one(
            {"id": comment['link_id'][3:], "comments.id": id},
            {"$set": {"comments.$": comment}}
        )
        return result

    def add_fields_to_submission(self, id, fields):
        self.collection.update_one({'id': id},
                                   {'$set': fields}
                                   )
