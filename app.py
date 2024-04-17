from flask import Flask, jsonify, request, redirect, url_for, render_template
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from gridfs import GridFS
import os


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Feedback"
mongo = PyMongo(app)

fs = GridFS(mongo.db)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif' , 'xlsx'}

# Check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/create', methods=['POST'])
def create():
    # Assuming a 'users' collection and JSON data containing 'name' and 'email'
    users = mongo.db.users
    name = request.json['name']
    email = request.json['email']
    user_id = users.insert_one({'name': name, 'email': email}).inserted_id
    return jsonify({'id': str(user_id)})

@app.route('/read')
def read():
    users = mongo.db.users.find()
    response = []
    for users in users:
        users['_id'] = str(users['_id'])  # Convert ObjectId to string
        response.append(users)
    return jsonify(response)

@app.route('/update', methods=['PUT'])
def update():
    name = request.json['name']
    new_email = request.json['email']
    mongo.db.users.update_one({'name': name}, {'$set': {'email': new_email}})
    return jsonify({'message': 'users Updated'})

@app.route('/delete', methods=['DELETE'])
def delete():
    name = request.json['name']
    mongo.db.users.delete_one({'name': name})
    return jsonify({'message': 'users Deleted'})

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'})
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'})
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file_id = fs.put(file, filename=filename)
#         return jsonify({'file_id': str(file_id)})
#     else:
#         return jsonify({'error': 'File not allowed'})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if 'username' not in request.form or 'email' not in request.form:
        return jsonify({'error': 'Username and email required'})
    
    username = request.form['username']
    email = request.form['email']
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_id = fs.put(file, filename=filename, username=username, email=email)
        return jsonify({'file_id': str(file_id) , 'message': 'File Added successfully' })
    else:
        return jsonify({'error': 'File not allowed'})

@app.route('/file/<file_id>', methods=['GET'])
def get_file_details(file_id):
    file_obj = fs.find_one({"_id": ObjectId(file_id)})
    if file_obj:
        return jsonify({
            'file_id': str(file_obj._id),
            'filename': file_obj.filename,
            'username': file_obj.username,
            'email': file_obj.email
        })
    else:
        return jsonify({'error': 'File not found'})


@app.route('/update/<file_id>', methods=['PUT'])
def update_file(file_id):
    if not ObjectId.is_valid(file_id):
        return jsonify({'error': 'Invalid file_id'})
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if 'username' not in request.form or 'email' not in request.form:
        return jsonify({'error': 'Username and email required'})
    
    username = request.form['username']
    email = request.form['email']
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        fs.delete(ObjectId(file_id))  # Delete the old file
        new_file_id = fs.put(file, filename=filename, username=username, email=email)
        return jsonify({'file_id': str(new_file_id) , 'message': 'File UPDATED SUCCESSFULLY'})
    else:
        return jsonify({'error': 'File not allowed'})

@app.route('/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    if not ObjectId.is_valid(file_id):
        return jsonify({'error': 'Invalid file_id'})
    fs.delete(ObjectId(file_id))
    return jsonify({'message': 'File deleted successfully'})

# @app.route('/delete/<filename>', methods=['DELETE'])
# def delete_file(filename):
#     fs.delete(filename=filename)
#     return jsonify({'message': 'File deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)













# from flask import Flask, jsonify, request
# from flask_pymongo import PyMongo
# from urllib.parse import quote_plus

# app = Flask(__name__)

# # Original credentials
# username = 'hemanshur'
# password = 'HUCJ@123'  # This contains a special character that needs encoding

# # URL-encode the credentials
# encoded_username = quote_plus(username)
# encoded_password = quote_plus(password)

# # Construct the MONGO_URI with the encoded credentials
# app.config["MONGO_URI"] = f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.hpsocxl.mongodb.net/Feedback?retryWrites=true&w=majority&appName=Cluster0"

# mongo = PyMongo(app)

# @app.route('/')
# def index():
#     return "Welcome to the Flask-MongoDB CRUD App"

# @app.route('/create', methods=['POST'])
# def create():
#     # Use 'users' collection as per your database schema
#     user_collection = mongo.db.users
#     name = request.json['name']
#     email = request.json['email']
#     user_id = user_collection.insert_one({'name': name, 'email': email}).inserted_id
#     return jsonify({'id': str(user_id)})

# @app.route('/read')
# def read():
#     user_collection = mongo.db.users
#     users = user_collection.find()
#     response = []
#     for users in users:
#         users['_id'] = str(users['_id'])  # Convert ObjectId to string for JSON serialization
#         response.append(users)
#     return jsonify(response)

# @app.route('/update', methods=['POST'])
# def update():
#     user_collection = mongo.db.users
#     name = request.json['name']
#     new_email = request.json['email']
#     user_collection.update_one({'name': name}, {'$set': {'email': new_email}})
#     return jsonify({'message': 'users Updated'})

# @app.route('/delete', methods=['POST'])
# def delete():
#     user_collection = mongo.db.users
#     name = request.json['name']
#     user_collection.delete_one({'name': name})
#     return jsonify({'message': 'users Deleted'})

# if __name__ == '__main__':
#     app.run(debug=True)

# #!/usr/bin/env python
# # encoding: utf-8
# import json
# from flask import Flask, request, jsonify
# from flask_mongoengine import MongoEngine

# app = Flask(__name__)
# app.config['MONGODB_SETTINGS'] = {
#     'db': 'Feedback',
#     'host': 'localhost',
#     'port': 27017
# }
# db = MongoEngine()
# db.init_app(app)

# class users(db.Document):
#     name = db.StringField()
#     email = db.StringField()
#     def to_json(self):
#         return {"name": self.name,
#                 "email": self.email}

# @app.route('/', methods=['GET'])
# def query_records():
#     name = request.args.get('name')
#     users = users.objects(name=name).first()
#     if not users:
#         return jsonify({'error': 'data not found'})
#     else:
#         return jsonify(users.to_json())

# @app.route('/', methods=['PUT'])
# def create_record():
#     record = json.loads(request.data)
#     users = users(name=record['name'],
#                 email=record['email'])
#     users.save()
#     return jsonify(users.to_json())

# @app.route('/', methods=['POST'])
# def update_record():
#     record = json.loads(request.data)
#     users = users.objects(name=record['name']).first()
#     if not users:
#         return jsonify({'error': 'data not found'})
#     else:
#         users.update(email=record['email'])
#     return jsonify(users.to_json())

# @app.route('/', methods=['DELETE'])
# def delete_record():
#     record = json.loads(request.data)
#     users = users.objects(name=record['name']).first()
#     if not users:
#         return jsonify({'error': 'data not found'})
#     else:
#         users.delete()
#     return jsonify(users.to_json())

# if __name__ == "__main__":
#     app.run(debug=True)

# #!/usr/bin/env python
# # encoding: utf-8
# import json
# from flask import Flask, request, jsonify
# from flask_mongoengine import MongoEngine

# app = Flask(__name__)
# app.config['MONGODB_SETTINGS'] = {
#     'host': 'mongodb+srv://hemanshur:HUCJ@!23@cluster0.hpsocxl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'  # MongoDB URI
# }
# db = MongoEngine()
# db.init_app(app)

# class users(db.Document):
#     name = db.StringField()
#     email = db.StringField()

#     def to_json(self):
#         return {"name": self.name,
#                 "email": self.email}

# @app.route('/', methods=['GET'])
# def query_records():
#     name = request.args.get('name')
#     users = users.objects(name=name).first()
#     if not users:
#         return jsonify({'error': 'data not found'})
#     else:
#         return jsonify(users.to_json())

# @app.route('/', methods=['PUT'])
# def create_record():
#     record = json.loads(request.data)
#     users = users(name=record['name'],
#                 email=record['email'])
#     users.save()
#     return jsonify(users.to_json())

# @app.route('/', methods=['POST'])
# def update_record():
#     record = json.loads(request.data)
#     users = users.objects(name=record['name']).first()
#     if not users:
#         return jsonify({'error': 'data not found'})
#     else:
#         users.update(email=record['email'])
#     return jsonify(users.to_json())

# @app.route('/', methods=['DELETE'])
# def delete_record():
#     record = json.loads(request.data)
#     users = users.objects(name=record['name']).first()
#     if not users:
#         return jsonify({'error': 'data not found'})
#     else:
#         users.delete()
#     return jsonify(users.to_json())

# if __name__ == "__main__":
#     app.run(debug=True)
