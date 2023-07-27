from mongodb_helper import MongoDBHelper
from gridfs import GridFS
from bson import ObjectId
from pw import mongo_password, mongo_username, mongo_uri


mongo = MongoDBHelper(
    mongo_uri,
    "diaogroup",
)

db = mongo.db

fs = GridFS(db, collection="recipes")

# Open and store the CSV file using GridFS
with open("data.csv", "rb") as file:
    file_id = fs.put(file, filename="data.csv")
    # create ObjectId(file_id) in document to point to csv

# Retrieve the CSV file from GridFS
gridfs_file = fs.find_one({"_id": ObjectId("64c2d215255f257ee66d30e9")})

# Read the CSV data from the file
csv_data = gridfs_file.read()

# Print the CSV data
print(csv_data)
# print(csv_data.decode())
