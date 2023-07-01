from devices.dummy_heater import DummyHeater
from mongodb_helper import MongoDBHelper

mongo = MongoDBHelper('mongodb+srv://ppahuja2:s5eMFr1js8iEcMt8@diaogroup.nrcgqsq.mongodb.net/?retryWrites=true&w=majority', 'diaogroup')

# print(mongo.insert_yaml_file('recipes',"e1.yaml"))
print(mongo.find_documents('recipes',{'file_name':'e1.yaml'})[0])

print('done')



mongo.close_connection()

# client = MongoClient('mongodb+srv://ppahuja2:s5eMFr1js8iEcMt8@diaogroup.nrcgqsq.mongodb.net/?retryWrites=true&w=majority')
# db = client['diaogroup']
# collection = db['recipes']