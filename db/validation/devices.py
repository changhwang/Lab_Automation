from mongodb_helper import MongoDBHelper

mongo = MongoDBHelper(
    "mongodb+srv://ppahuja2:s5eMFr1js8iEcMt8@diaogroup.nrcgqsq.mongodb.net/?retryWrites=true&w=majority",
    "diaogroup",
)

db = mongo.db

device_dict = {
    "device": {
        "electrode_etl": {
            "material": {
                "metadata": {
                    "solvent": "string",
                    "concentration": "float",
                    "printing_speed": "float",
                    "printing_temperature": "float",
                    "additive": {
                        "molecule": "string",
                        "concentration": "float",
                    },
                }
            }
        },
        "etl": {
            "material": {
                "metadata": {
                    "solvent": "string",
                    "concentration": "float",
                    "printing_speed": "float",
                    "printing_temperature": "float",
                    "additive": {
                        "molecule": "string",
                        "concentration": "float",
                    },
                }
            }
        },
        "active_layer": {
            "donor": {
                "material": {
                    "metadata": {
                        "solvent": "string",
                        "concentration": "float",
                        "printing_speed": "float",
                        "printing_temperature": "float",
                        "additive": {
                            "molecule": "string",
                            "concentration": "float",
                        },
                    }
                }
            },
            "acceptor": {
                "material": {
                    "metadata": {
                        "solvent": "string",
                        "concentration": "float",
                        "printing_speed": "float",
                        "printing_temperature": "float",
                        "additive": {
                            "molecule": "string",
                            "concentration": "float",
                        },
                    }
                }
            },
        },
        "htl": {
            "material": {
                "metadata": {
                    "solvent": "string",
                    "concentration": "float",
                    "printing_speed": "float",
                    "printing_temperature": "float",
                    "additive": {
                        "molecule": "string",
                        "concentration": "float",
                    },
                }
            }
        },
        "electrode_htl": {
            "material": {
                "metadata": {
                    "solvent": "string",
                    "concentration": "float",
                    "printing_speed": "float",
                    "printing_temperature": "float",
                    "additive": {
                        "molecule": "string",
                        "concentration": "float",
                    },
                }
            }
        },
    },
    "result": {
        "jv_curve": ["object_id", "null"],
        "t80": ["float", "null"],
    },
}

device_dict_schema = {
    "bsonType": "object",
    "title": "Device Object Validation",
    "required": ["device", "result"],
    "properties": {
        "device": {
            "bsonType": "object",
            "title": "Device Validation",
            "required": ["electrode_etl", "active_layer", "electrode_htl"],
            "properties": {
                "electrode_etl": {
                    "bsonType": "object",
                    "title": "Electrode ETL Validation",
                    "required": ["material"],
                    "properties": {
                        "material": {
                            "bsonType": "object",
                            "title": "Material Validation",
                            "required": ["metadata"],
                            "properties": {
                                "metadata": {
                                    "bsonType": "object",
                                    "title": "Metadata Validation",
                                    "required": [
                                        "solvent",
                                        "concentration",
                                        "printing_speed",
                                        "printing_temperature",
                                        "additive",
                                    ],
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
                                            "description": "'speed' must be a double and is required",
                                        },
                                        "printing_temperature": {
                                            "bsonType": "double",
                                            "description": "'temperature' must be a double and is required",
                                        },
                                        "additive": {
                                            "bsonType": "object",
                                            "title": "Additive Validation",
                                            "required": ["molecule", "concentration"],
                                            "properties": {
                                                "molecule": {
                                                    "bsonType": "string",
                                                    "description": "'molecule' must be a string and is required",
                                                },
                                                "concentration": {
                                                    "bsonType": "double",
                                                    "description": "'concentration' must be a double and is required",
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                "active_layer": {
                    "bsonType": "object",
                    "title": "Active Layer Validation",
                    "required": ["donor", "acceptor"],
                    "properties": {
                        "donor": {
                            "bsonType": "object",
                            "title": "Donor Validation",
                            "required": ["material"],
                            "properties": {
                                "material": {
                                    "bsonType": "object",
                                    "title": "Material Validation",
                                    "required": ["metadata"],
                                    "properties": {
                                        "metadata": {
                                            "bsonType": "object",
                                            "title": "Metadata Validation",
                                            "required": [
                                                "solvent",
                                                "concentration",
                                                "printing_speed",
                                                "printing_temperature",
                                                "additive",
                                            ],
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
                                                    "description": "'speed' must be a double and is required",
                                                },
                                                "printing_temperature": {
                                                    "bsonType": "double",
                                                    "description": "'temperature' must be a double and is required",
                                                },
                                                "additive": {
                                                    "bsonType": "object",
                                                    "title": "Additive Validation",
                                                    "required": [
                                                        "molecule",
                                                        "concentration",
                                                    ],
                                                    "properties": {
                                                        "molecule": {
                                                            "bsonType": "string",
                                                            "description": "'molecule' must be a string and is required",
                                                        },
                                                        "concentration": {
                                                            "bsonType": "double",
                                                            "description": "'concentration' must be a double and is required",
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                        "acceptor": {
                            "bsonType": "object",
                            "title": "Acceptor Validation",
                            "required": ["material"],
                            "properties": {
                                "material": {
                                    "bsonType": "object",
                                    "title": "Material Validation",
                                    "required": ["metadata"],
                                    "properties": {
                                        "metadata": {
                                            "bsonType": "object",
                                            "title": "Metadata Validation",
                                            "required": [
                                                "solvent",
                                                "concentration",
                                                "printing_speed",
                                                "printing_temperature",
                                                "additive",
                                            ],
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
                                                    "description": "'speed' must be a double and is required",
                                                },
                                                "printing_temperature": {
                                                    "bsonType": "double",
                                                    "description": "'temperature' must be a double and is required",
                                                },
                                                "additive": {
                                                    "bsonType": "object",
                                                    "title": "Additive Validation",
                                                    "required": [
                                                        "molecule",
                                                        "concentration",
                                                    ],
                                                    "properties": {
                                                        "molecule": {
                                                            "bsonType": "string",
                                                            "description": "'molecule' must be a string and is required",
                                                        },
                                                        "concentration": {
                                                            "bsonType": "double",
                                                            "description": "'concentration' must be a double and is required",
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                "electrode_htl": {
                    "bsonType": "object",
                    "title": "Electrode HTL Validation",
                    "required": ["material"],
                    "properties": {
                        "material": {
                            "bsonType": "object",
                            "title": "Material Validation",
                            "required": ["metadata"],
                            "properties": {
                                "metadata": {
                                    "bsonType": "object",
                                    "title": "Metadata Validation",
                                    "required": [
                                        "solvent",
                                        "concentration",
                                        "printing_speed",
                                        "printing_temperature",
                                        "additive",
                                    ],
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
                                            "description": "'speed' must be a double and is required",
                                        },
                                        "printing_temperature": {
                                            "bsonType": "double",
                                            "description": "'temperature' must be a double and is required",
                                        },
                                        "additive": {
                                            "bsonType": "object",
                                            "title": "Additive Validation",
                                            "required": ["molecule", "concentration"],
                                            "properties": {
                                                "molecule": {
                                                    "bsonType": "string",
                                                    "description": "'molecule' must be a string and is required",
                                                },
                                                "concentration": {
                                                    "bsonType": "double",
                                                    "description": "'concentration' must be a double and is required",
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        "result": {
            "bsonType": "object",
            "title": "Result Object Validation",
            "required": ["jv_curve", "t80"],
            "properties": {
                "jv_curve": {
                    "bsonType": ["objectId", "null"],
                    "description": "'jv_curve' must be an objectId and is required",
                },
                "t80": {
                    "bsonType": ["double", "null"],
                    "description": "'t80' must be a double and is required",
                },
            },
        },
    },
}


collection_name = "devices"
collection_options = {"validator": {"$jsonSchema": device_dict_schema}}
db.create_collection(collection_name, **collection_options)
quit()
