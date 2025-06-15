from flask import Blueprint, request, jsonify
from database import get_db_connection

students_routes = Blueprint('students_routes', __name__)

@students_routes.route('/students/insert', methods=['POST'])
def insert_student():
    data = request.get_json()
    
    required_fields = ['name', 'father_name', 'mother_name', 'address', 'mobileno', 'email_address', 'date_of_birth', 'gender']
    if not all(data.get(field) for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields!'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''INSERT INTO students (name, father_name, mother_name, address, mobileno, email_address, date_of_birth, gender)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (data['name'], data['father_name'], data['mother_name'], data['address'],
                 data['mobileno'], data['email_address'], data['date_of_birth'], data['gender']))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Student inserted successfully!'}), 201
