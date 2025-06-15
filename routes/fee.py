from flask import Blueprint, request, jsonify
from database import get_db_connection

fee_routes = Blueprint('fee_routes', __name__)

@fee_routes.route('/fee/insert', methods=['POST'])
def insert_fee():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''INSERT INTO fee 
        (receipt_no, student_name, admission_no, date, branch, semester, total_amount, paid_amount, balance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (data['receipt_no'], data['student_name'], data['admission_no'], data['date'],
         data['branch'], data['semester'], data['total_amount'], data['paid_amount'], data['balance']))
    
    conn.commit()
    conn.close()
    return jsonify({"message": "Fee data inserted successfully!"}), 200

@fee_routes.route('/fee/view', methods=['GET'])
def view_fee():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM fee")
    rows = cur.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in rows])
