from pymongo import MongoClient
from bson.objectid import ObjectId

# Your MongoDB URI
uri = "mongodb+srv://maaz0301301:5uI9SlSVLIGOzTgo@cluster0.prqfiyx.mongodb.net/"

# Connect to the MongoDB cluster
client = MongoClient(uri)

# Specify the database and collection
db = client['fabi-careDB']
collection = db['testing']

def create_object(data):
    """Create a new object in the collection."""
    result = collection.insert_one(data)
    print(f"Object inserted with ID: {result.inserted_id}")
    return result.inserted_id

# def get_object(object_id):
#     """Retrieve an object from the collection by its ID."""
#     result = collection.find_one({"_id": ObjectId(object_id)})
#     if result:
#         print(f"Object found: {result}")
#     else:
#         print("Object not found.")
#     return result


def get_object(object_id):
    """Retrieve an object from the collection by its ID and return the prompt as a string."""
    result = collection.find_one({"_id": ObjectId(object_id)})
    if result and 'prompt' in result:
        return result['prompt']
    else:
        return "Object not found."



def update_object(object_id, update_data):
    """Update an object in the collection by its ID."""
    result = collection.update_one({"_id": ObjectId(object_id)}, {"$set": update_data})
    if result.modified_count > 0:
        print(f"Object with ID {object_id} updated.")
    else:
        print("No object was updated.")
    return result

# Example usage
if __name__ == "__main__":
    # Create an example object
    # example_data = {
    #     "prompt": "Example Object"
    # }
    # object_id = create_object(example_data)

    # # Retrieve the object
    # get_object(object_id)

    # Update the object with a known ID
    update_data = {
        "prompt": "hello how are you "
    }
    update_object("667c0816937d7e42dbbe5748", update_data)

    # Retrieve the object again to see the changes
    print ("goooo .... ",get_object("667c0816937d7e42dbbe5748"))
