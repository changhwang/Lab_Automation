from mongodb_helper import MongoDBHelper
from gridfs import GridFS
from bson import ObjectId


mongo = MongoDBHelper(
    "mongodb+srv://ppahuja2:s5eMFr1js8iEcMt8@diaogroup.nrcgqsq.mongodb.net/?retryWrites=true&w=majority",
    "diaogroup",
)

db = mongo.db

fs = GridFS(db, collection="recipes")

# Open and store the CSV file using GridFS
with open("data.csv", "rb") as file:
    file_id = fs.put(file, filename="data.csv")
    # create ObjectId(file_id) in document to point to csv

# Retrieve the CSV file from GridFS
gridfs_file = fs.find_one({"filename": "data.csv"})

# Read the CSV data from the file
csv_data = gridfs_file.read()

# Print the CSV data
print(csv_data.decode())
