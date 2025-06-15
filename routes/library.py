from flask import Blueprint, request, jsonify
from database import get_db_connection

library_routes = Blueprint('library_routes', __name__)

@library_routes.route('/library/insert', methods=['POST'])
def insert_library():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''INSERT INTO library 
        (Mbtype, referenceno, firstname, lastname, address, post, mobileno, ID, title, author, borrow, due, loan) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (data['mbtype'], data['referenceno'], data['firstname'], data['lastname'], 
         data['address'], data['post'], data['mobileno'], data['id'], data['title'], 
         data['author'], data['borrow'], data['due'], data['loan']))
    
    conn.commit()
    conn.close()
    return jsonify({"message": "Library data inserted successfully!"}), 200
