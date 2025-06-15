from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Configuration (Change accordingly)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Tera MySQL username
app.config['MYSQL_PASSWORD'] = 'your_password'  # Tera MySQL ka password
app.config['MYSQL_DB'] = 'college_db'  # Tera database ka naam
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Example API: Get Students Data
@app.route('/students', methods=['GET'])
def get_students():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    cur.close()
    return {"students": data}

if __name__ == '__main__':
    app.run(debug=True)
