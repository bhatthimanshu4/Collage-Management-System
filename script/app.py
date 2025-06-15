
import pymysql
import bcrypt
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import random
import string
from pymysql.cursors import DictCursor


# ✅ Flask App Initialization


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}}, supports_credentials=True)


"""@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response"""

# ✅ Database Connection Function
def get_db_connection():    
    try:
        conn = pymysql.connect(
            host="127.0.0.1",
            user="admin",
            password="NewPass123!",
            database="college_management",
            cursorclass=pymysql.cursors.DictCursor
        )
        print("✅ Database Connection Successful!")
        return conn
    except pymysql.MySQLError as e:
        print(f"❌ Database Connection Failed: {e}")
        return None
    

# ✅ Signup API
def generate_unique_id():
    return "UID-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ✅ Updated Signup API
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    security_question = data.get('security_question')
    security_answer = data.get('security_answer')

    if not username or not email or not password:
        return jsonify({"error": "❌ All fields are required!"}), 400

    unique_id = generate_unique_id()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (unique_id, username, email, password, security_question, security_answer)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (unique_id, username, email, hashed_password, security_question, security_answer)
        )
        conn.commit()
        return jsonify({"message": "✅ Signup Successful!", "uniqueId": unique_id}), 201

    except pymysql.MySQLError as e:
        return jsonify({"error": f"❌ Database error: {e}"}), 500

    finally:
        conn.close()


# ✅ **Login API**
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"error": "❌ All fields are required!"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT unique_id, username, password FROM users WHERE username = %s AND email = %s",
                       (username, email))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "❌ User not found!"}), 404

        db_unique_id = user['unique_id']
        db_username = user['username']
        db_password = user['password'].encode('utf-8')

        if bcrypt.checkpw(password.encode('utf-8'), db_password):
            return jsonify({
                "message": "✅ Login Successful!",
                "unique_id": db_unique_id,
                "username": db_username
            }), 200
        else:
            return jsonify({"error": "❌ Invalid Credentials!"}), 401

    except pymysql.MySQLError as e:
        return jsonify({"error": f"❌ Database Error: {str(e)}"}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    unique_id = data.get('uniqueId')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE unique_id = %s", (unique_id,))
    user = cursor.fetchone()

    conn.close()

    if user:
        return jsonify({"message": "User found"}), 200
    else:
        return jsonify({"error": "Invalid Unique ID!"}), 400


@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    unique_id = data.get('uniqueId')
    new_password = data.get('newPassword')

    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET password = %s WHERE unique_id = %s", (hashed_password, unique_id))
    conn.commit()

    conn.close()

    return jsonify({"message": "Password reset successful!"}), 200



@app.route('/change-password', methods=['POST'])
def update_password():
    data = request.get_json()
    email = data.get('uniqueId')
    new_password = data.get('newPassword')

    if not email or not new_password:
        return jsonify({"error": "Missing data"}), 400

    try:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
        conn.commit()
        conn.close()

        return jsonify({"message": "✅ Password updated successfully!"}), 200

    except Exception as e:
        print("❌ Error updating password:", e)
        return jsonify({"error": "Server error"}), 500

  # ✅ Import DictCursor

@app.route('/verify-email', methods=['POST', 'OPTIONS'])
def verify_email():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight passed"}), 200  

    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(DictCursor)  # ✅ Correct way to use dictionary cursor

    cursor.execute("SELECT security_question FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    conn.close()

    if user:
        return jsonify({"security_question": user["security_question"]}), 200
    else:
        return jsonify({"error": "User not found or Invalid Email!"}), 404

    

@app.route('/verify-security-answer', methods=['POST'])
def verify_security_answer():
    data = request.json
    email = data.get('email')
    security_answer = data.get('security_answer')

    if not email or not security_answer:
        return jsonify({"error": "Email and Answer are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(DictCursor)

    cursor.execute("SELECT * FROM users WHERE email = %s AND security_answer = %s", (email, security_answer))
    user = cursor.fetchone()

    conn.close()

    if user:
        return jsonify({"message": "✅ Security Answer Verified!", "success": True}), 200  # ✅ सही Answer का Response
    else:
        return jsonify({"error": "❌ Incorrect Answer, please try again."}), 401  # ❌ गलत Answer का Response



# ✅ Insert Student API
@app.route('/insert', methods=['POST', 'OPTIONS'])
def insert_student():
    if request.method == "OPTIONS":
        return jsonify({"success": True, "message": "Preflight OK"}), 200  # ✅ Fixes CORS Preflight Issue

    data = request.json
    if not data:
        return jsonify({"success": False, "message": "❌ Invalid Data"}), 400
    
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "❌ Database Connection Failed"}), 500

        with conn.cursor() as cursor:
            sql = """
            INSERT INTO students_info (name, father_name, mother_name, address, mobileno, email_address, date_of_birth, gender)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data["name"], data["father_name"], data["mother_name"], 
                data["address"], data["mobileno"], data["email_address"], 
                data["date_of_birth"], data["gender"]
            ))
            conn.commit()

        return jsonify({"success": True, "message": "✅ Student Inserted Successfully"}), 201

    except pymysql.MySQLError as e:
        return jsonify({"success": False, "message": f"❌ Database Error: {e}"}), 500

    finally:
        if 'conn' in locals():
            conn.close()


# ✅ Fetch All Students API
@app.route('/studentsList', methods=['GET'])
def get_students():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '❌ Database connection failed!'}), 500

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM students_info ORDER BY student_id ASC")
            students = cursor.fetchall()
        return jsonify({'success': True, 'studentsList': students}), 200

    except pymysql.MySQLError as e:
        return jsonify({'success': False, 'message': f'❌ Database error: {e}'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# ✅ Search Student API
@app.route('/search/<int:student_id>', methods=['GET'])
def search_student(student_id):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '❌ Database connection failed!'}), 500

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM students_info WHERE student_id = %s", (student_id,))
            student = cursor.fetchone()

        if student:
            return jsonify({'success': True, 'student': student}), 200
        else:
            return jsonify({'success': False, 'message': '❌ Student not found!'}), 404

    except pymysql.MySQLError as e:
        return jsonify({'success': False, 'message': f'❌ Database error: {e}'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# ✅ Generate Student ID API
@app.route('/generateStudentID', methods=['GET'])
def generate_student_id():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '❌ Database connection failed!'}), 500

        with conn.cursor() as cursor:
            cursor.execute("SELECT MAX(student_id) AS max_id FROM students_info")
            result = cursor.fetchone()
            new_id = (result.get("max_id") or 0) + 1

        return jsonify({'success': True, 'new_student_id': new_id}), 200

    except pymysql.MySQLError as e:
        return jsonify({'success': False, 'message': f'❌ Database error: {e}'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# ✅ Find All Students API (Fixing 404 Error)
@app.route('/findAllStudents', methods=['GET'])
def get_all_students():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '❌ Database connection failed!'}), 500

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM students_info")
            students = cursor.fetchall()

        return jsonify({'success': True, 'studentsList': students}), 200

    except pymysql.MySQLError as e:
        return jsonify({'success': False, 'message': f'❌ Database error: {e}'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Get student details by ID
@app.route('/get_student/<int:student_id>', methods=['GET'])
def get_student(student_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "❌ Database connection failed!"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM students_info WHERE student_id = %s", (student_id,))
            student = cursor.fetchone()

        if student:
            return jsonify({"success": True, "student": student}), 200
        else:
            return jsonify({"success": False, "message": "❌ Student not found!"}), 404
    except pymysql.MySQLError as e:
        return jsonify({"success": False, "message": f"❌ Database error: {e}"}), 500
    finally:
        conn.close()



# Update student details
@app.route('/update_student/<int:student_id>', methods=['PUT', 'OPTIONS'])
def update_student(student_id):
    if request.method == "OPTIONS":  # Handle CORS preflight request
        response = jsonify({"message": "CORS preflight successful!"})
        response.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
        response.headers["Access-Control-Allow-Methods"] = "PUT, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response, 200  # ✅ Preflight request success

    data = request.json
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE students_info 
            SET name = %s, father_name = %s, mother_name = %s, address = %s, 
                mobileno = %s, email_address = %s, date_of_birth = %s, gender = %s 
            WHERE student_id = %s
        """, (data['name'], data['father_name'], data['mother_name'], data['address'],
              data['mobileno'], data['email_address'], data['date_of_birth'], data['gender'], student_id))
        conn.commit()

    if cursor.rowcount > 0:
        return jsonify({"success": True, "message": "✅ Student updated successfully!"}), 200
    else:
        return jsonify({"success": False, "message": "❌ Student not found or no changes made!"}), 404

@app.route('/delete_student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM students_info WHERE student_id = %s", (student_id,))
        conn.commit()
        conn.close()

        if cursor.rowcount > 0:
            return jsonify({'success': True, 'message': 'Student deleted successfully!'}), 200
        else:
            return jsonify({'success': False, 'message': 'Student not found!'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/save_fee_receipt', methods=['POST'])
def save_fee_receipt():
    try:
        data = request.get_json()

        receipt_no = data.get('receipt_no')
        student_name = data.get('student_name')
        admission_no = data.get('admission_no')
        branch = data.get('branch')
        date = data.get('date')
        total_amount = float(data.get('total_amount', 0))
        paid_amount = float(data.get('paid_amount', 0))
        balance = total_amount - paid_amount  # ✅ Calculate balance before saving

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO Fee_Management (receipt_no, student_name, admission_no, branch, date, total_amount, paid_amount, balance) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (receipt_no, student_name, admission_no, branch, date, total_amount, paid_amount, balance))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Fee receipt saved successfully!'}), 200

    except Exception as e:
        print("❌ Database Error:", str(e))  # ✅ Debugging ke liye print kar
        return jsonify({'success': False, 'message': f"Database Error: {str(e)}"}), 500





@app.route('/get_receipt/<receipt_no>', methods=['GET'])
def get_receipt(receipt_no):
   try:
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "❌ Database connection failed!"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Fee_Management WHERE LOWER(receipt_no) = LOWER(%s)", (receipt_no,))

    receipt = cursor.fetchone()

    if receipt:
        return jsonify({"success": True, "receipt": receipt}), 200
    else:
        return jsonify({"success": False, "message": "❌ Receipt not found!"}), 404
   except Exception as e:
       return jsonify({"success": False, "message": f"❌ Error: {str(e)}"}), 500
   finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()



# ✅ Get All Fee Receipts API
@app.route('/get_all_receipts', methods=['GET'])
def get_all_receipts():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed!'}), 500

        with conn.cursor() as cursor:
            cursor.execute("SELECT receipt_no, student_name, admission_no, branch, total_amount, paid_amount, balance FROM Fee_Management")
            receipts = cursor.fetchall()

        return jsonify({'success': True, 'receipts': receipts}), 200

    except pymysql.MySQLError as e:
        return jsonify({'success': False, 'message': f'Database error: {e}'}), 500
    finally:
        if 'conn' in locals():
            conn.close()


@app.route('/insert_library_details', methods=['POST'])
def insert_library_details():
    try:
        data = request.get_json()

        mbtype = data['mbtype']
        referenceno = data['referenceno']
        firstname = data['firstname']
        lastname = data['lastname']
        address = data['address']
        post = data['post']
        mobileno = data['mobileno']
        title = data['title']
        author = data['author']
        borrow = data['borrow']
        due = data['due']
        year_of_pub = data['year_of_pub']

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO library_management (mbtype, referenceno, firstname, lastname, address, post, mobileno, title, author, borrow, due, year_of_pub)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (mbtype, referenceno, firstname, lastname, address, post, mobileno, title, author, borrow, due, year_of_pub))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Data Inserted Successfully!'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/get_library_record/<referenceno>', methods=['GET'])
def get_library_record(referenceno):

    if not referenceno:
        return jsonify({'success': False, 'message': "Reference No is required!"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetching the record based on Reference No.
        cursor.execute("""
            SELECT * FROM library_management
            WHERE referenceno=%s
        """, (referenceno,))

        record = cursor.fetchone()

        conn.close()

        if record:
            # Sending back the fetched record as JSON
            return jsonify({
                'success': True,
                'record': {
                    'mbtype': record[0],
                    'referenceno': record[1],
                    'firstname': record[2],
                    'lastname': record[3],
                    'address': record[4],
                    'post': record[5],
                    'mobileno': record[6],
                    'title': record[7],
                    'author': record[8],
                    # 'borrow': record[9].strftime('%Y-%m-%d'),
                    # 'due': record[10].strftime('%Y-%m-%d'),
                    'year_of_pub': record[11]
                }
            }), 200
        else:
            return jsonify({'success': False, 'message': "Record not found!"}), 404

    except pymysql.MySQLError as e:
        return jsonify({'success': False, 'message': f"Database error: {e}"}), 500


    
    # ✅ Get Single Record API


@app.route('/get_single_record', methods=['GET'])
def get_single_record():
    referenceno = request.args.get('referenceno')

    print("referenceno:::", referenceno)

    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)  # Ensure cursor returns results as dictionaries
        cursor.execute("SELECT * FROM library_management WHERE referenceno = %s", (referenceno))
        record = cursor.fetchone()

        conn.close()

        if record:
            # ✅ Convert Date Format in Response
            if record['borrow'] and isinstance(record['borrow'], datetime):
                record['borrow'] = record['borrow'].strftime("%Y-%m-%d")
            if record['due'] and isinstance(record['due'], datetime):
                record['due'] = record['due'].strftime("%Y-%m-%d")

            return jsonify({'success': True, 'record': record}), 200
        else:
            return jsonify({'success': False, 'message': "No record found"}), 404
    except pymysql.MySQLError as e:
        return jsonify({'success': False, 'message': f"Database error: {e}"}), 500





    
# ✅ Update Record API
@app.route('/update_library_record', methods=['POST'])
def update_library_record():
    data = request.json

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE library_management SET
            mbtype=%s, firstname=%s, lastname=%s, address=%s, post=%s, mobileno=%s,
            title=%s, author=%s, borrow=%s, due=%s, year_of_pub=%s
            WHERE referenceno=%s
        """, (data['mbtype'], data['firstname'], data['lastname'], data['address'],
              data['post'], data['mobileno'], data['title'], data['author'],
              data['borrow'], data['due'], data['year_of_pub'], data['referenceno']))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': "Record updated successfully!"}), 200

    except pymysql.MySQLError as e:
        return jsonify({'success': False, 'message': f"Database error: {e}"}), 500
    
@app.route('/get_library_data', methods=['GET'])
def get_library_data():
    try:
        # ✅ Database connection with DictCursor
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)  # ✅ Use DictCursor

        # ✅ Fetch all library records
        cursor.execute("SELECT * FROM library_management")
        records = cursor.fetchall()  # ✅ Now records will be a list of dictionaries

        # Debugging: Print records to check fetched data
        print("Fetched Records:", records)

        # ✅ No need to manually convert, because DictCursor returns dict directly
        return jsonify({'success': True, 'data': records}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Error: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/insert_marksheet', methods=['POST'])
def insert_marksheet():
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ Ensure DOB is in correct format (YYYY-MM-DD)
        dob = data["dob"]
        if dob:
            dob = datetime.strptime(dob, "%Y-%m-%d").date()

        # ✅ Calculate Total Marks & Percentage
        total_marks = sum([data["marks"]["mathematics"], data["marks"]["english"],
                           data["marks"]["physics"], data["marks"]["chemistry"], data["marks"]["programming"]])
        percentage = round((total_marks / 5), 2)

        # ✅ Grade Calculation
        def get_grade(percentage):
            if percentage >= 90:
                return "A+"
            elif percentage >= 80:
                return "A"
            elif percentage >= 70:
                return "B"
            elif percentage >= 60:
                return "C"
            elif percentage >= 50:
                return "D"
            elif percentage >= 40:
                return "E"
            else:
                return "F"

        grade = get_grade(percentage)
        result = "Pass" if percentage >= 40 else "Fail"

        # ✅ Insert or Update Query
        query = """
        INSERT INTO student_marksheet (roll_number, name, father_name, mother_name, dob, gender, school_name, email, 
                                       mathematics, english, physics, chemistry, programming, total_marks, percentage, grade, result)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            name=VALUES(name), father_name=VALUES(father_name), mother_name=VALUES(mother_name),
            dob=VALUES(dob), gender=VALUES(gender), school_name=VALUES(school_name), email=VALUES(email),
            mathematics=VALUES(mathematics), english=VALUES(english), physics=VALUES(physics),
            chemistry=VALUES(chemistry), programming=VALUES(programming), total_marks=VALUES(total_marks),
            percentage=VALUES(percentage), grade=VALUES(grade), result=VALUES(result)
        """

        values = (
            data["rollNumber"], data["name"], data["fatherName"], data["motherName"], dob, data["gender"],
            data["schoolName"], data["email"], data["marks"]["mathematics"], data["marks"]["english"],
            data["marks"]["physics"], data["marks"]["chemistry"], data["marks"]["programming"],
            total_marks, percentage, grade, result
        )

        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Marksheet saved successfully!"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": f"Database Error: {str(e)}"}), 500
    

# API to Get Student Marksheet Details
@app.route('/get_marksheet', methods=['GET'])
def get_marksheet():
    roll_number = request.args.get('roll_number')
    
    if not roll_number:
        return jsonify({"success": False, "message": "Roll Number is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM student_marksheet WHERE roll_number = %s", (roll_number,))
        student = cursor.fetchone()
        conn.close()

        if student:
            return jsonify({"success": True, "data": student}), 200
        else:
            return jsonify({"success": False, "message": "No records found"}), 404

    except Exception as e:
        return jsonify({"success": False, "message": f"Database Error: {str(e)}"}), 500
    

@app.route('/fetch_marksheet_data', methods=['GET'])
def fetch_marksheet_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM student_marksheet")  # ⚡ Replace with your table name
        students = cursor.fetchall()

        conn.close()
        
        return jsonify({'success': True, 'students': students}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f"Database Error: {str(e)}"}), 500
    





# ✅ Run Flask App
if __name__ == '__main__':
    app.run(debug=True, port=5000)
