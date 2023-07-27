from mongodb_helper import MongoDBHelper


mongo = MongoDBHelper(
    "mongodb+srv://ppahuja2:s5eMFr1js8iEcMt8@diaogroup.nrcgqsq.mongodb.net/?retryWrites=true&w=majority",
    "diaogroup",
)

db = mongo.db


film_dict = {
    "metadata": {
        "solvent": "string",
        "concentration": "float",
        "printing_speed": "float",
        "printing_temperature": "float",
    },
    "result": {
        "uv_vis": ["object_id", "null"],
        "t80": ["float", "null"],
    },
}


film_dict_schema = {
    "bsonType": "object",
    "title": "Film Object Validation",
    "required": ["metadata", "result"],
    "properties": {
        "metadata": {
            "bsonType": "object",
            "title": "Metadata Object Validation",
            "required": ["solvent", "concentration", "printing_speed", "printing_temperature"],
            "properties": {
                "solvent": {
                    "bsonType": "string",
                    "description": "'solvent' must be a string and is required",
                },
                "concentration": {
                    "bsonType": "double",
                    "description": "'concentration' must be a double and is required",
                },
                "printing_speed": {
                    "bsonType": "double",
                    "description": "'printing_speed' must be a double and is required",
                },
                "printing_temperature": {
                    "bsonType": "double",
                    "description": "'printing_temperature' must be a double and is required",
                },
            },
        },
        "result": {
            "bsonType": "object",
            "title": "Result Object Validation",
            "required": ["uv_vis", "t80"],
            "properties": {
                "uv_vis": {
                    "bsonType": ["objectId", "null"],
                    "description": "'uv_vis' must be an objectId and is required",
                },
                "t80": {
                    "bsonType": ["double", "null"],
                    "description": "'t80' must be a double and is required",
                },
            },
        },
    },
}



collection_name = "film"
collection_options = {"validator": {"$jsonSchema": film_dict_schema}}
db.create_collection(collection_name, **collection_options)
quit()