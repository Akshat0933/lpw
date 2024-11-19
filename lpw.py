import flask
from flask import request, jsonify
from pymongo import MongoClient

app = flask.Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['LPW']
users_collection = db['users']
books_collection = db['books']

@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400
    user = users_collection.find_one({'name': username})
    if not user:
        return jsonify({'message': 'Invalid username'}), 401
    if user['password'] != password:
        return jsonify({'message': 'Invalid password'}), 401
    return jsonify({'message': 'Login Successful'}), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400
    if users_collection.find_one({'name': username}):
        return jsonify({'message': 'Username already exists'}), 409
    users_collection.insert_one({'name': username, 'password': password})
    return jsonify({'message': 'Register Successful'}), 201

@app.route('/admin/add_book', methods=['POST'])
def add_book():
    data = request.get_json()
    bname = data.get('bname')
    author = data.get('author')
    quantity = data.get('quantity', 1)  # Default to 1 if not provided
    if not bname or not author:
        return jsonify({'message': 'Book name and author are required'}), 400
    book = books_collection.find_one({'bname': bname})
    if not book:
        books_collection.insert_one({'bname': bname, 'author': author, 'rented': 0, 'sell': 0, 'quantity': quantity})
    else:
        books_collection.update_one({'bname': bname}, {'$inc': {'quantity': quantity}})
    return jsonify({'message': 'Book Added Successfully'}), 200

@app.route('/view_book', methods=['GET'])
def view_book():
    bname = request.args.get('bname')
    author = request.args.get('author')
    if not bname or not author:
        return jsonify({'message': 'Book name and author are required'}), 400
    book = list(books_collection.find({'bname': bname, 'author': author}))
    if not book:
        return jsonify({'message': 'Book is not there'}), 404
    return jsonify(book), 200

@app.route('/view', methods=['GET'])
def view():
    books = list(books_collection.find())
    return str(books), 200

@app.route('/')
def index():
    return jsonify({'message': 'Hello from LMS'}), 200

@app.route('/admin/delete_user', methods=['DELETE'])
def delete_user():
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({'message': 'Username is required'}), 400
    result = users_collection.delete_many({'name': username})
    if result.deleted_count == 0:
        return jsonify({'message': 'User  not found'}), 404
    return jsonify({'message': 'User  Deleted Successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)