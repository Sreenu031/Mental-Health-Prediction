from flask import Blueprint
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from model import predict_value
from datetime import datetime
main = Blueprint('main', __name__)

# Database connection
def get_db_connection():
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="epics"
    )
    return con
@main.route("/")
def home():
    return render_template("index.html")
@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        name = request.form['name']
        contact_number = request.form['contact_number']
        address = request.form.get('address')  # Only for organization users

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert into users table
        try:
            cursor.execute("INSERT INTO users (username, password, user_type) VALUES (%s, %s, %s)",
                           (username, password, user_type))
            conn.commit()
        except mysql.connector.IntegrityError:
            conn.close()
            return "Username already exists."
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()[0]
        # Get the last inserted user_id
        cursor.close()

        cursor = conn.cursor()
        if user_type == 'organization':
            cursor.execute("INSERT INTO organization (organization_id, name, address, contact_num) VALUES (%s ,%s, %s, %s)",
                           ( user_id,name, address, contact_number))
        elif user_type == 'individual':

            cursor.execute("INSERT INTO individual_user ( user_id,name, contact_num) VALUES (%s, %s, %s)",
                           (user_id, name, contact_number))
        elif user_type == 'doctor':
            cursor.execute("INSERT INTO doctor ( doctor_id,name, contact_num) VALUES (%s, %s, %s)",
                           (user_id, name, contact_number))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('main.login'))
    return render_template('signup.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username = %s and password = %s", (username,password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session['user_id'] = user['user_id']
            session['user_type'] = user['user_type']
            return redirect(url_for('main.dashboard'))
        else:
            return "Login Failed"
    return render_template('login.html')

@main.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_type = session['user_type']

        # Redirect based on the user_type
        if user_type == 'doctor':
            return redirect(url_for('main.doctor_dashboard'))
        elif user_type == 'individual':
            return render_template('individual.html')
        elif user_type == 'organization':
            if 'user_id' in session and session['user_type'] == 'organization':
                org_id = session['user_id']  # Assuming org_id is stored in the session

                # Connect to the database
                conn = get_db_connection()
                cursor = conn.cursor()
                print(session['user_id'])
                # Fetch students related to the organization
                cursor.execute("SELECT stud_id, name,age FROM students WHERE org_id = %s", (org_id,))
                students = cursor.fetchall()  # students will be a list of tuples [(id, name), ...]

                cursor.close()
                conn.close()

                # Pass the fetched students to the template
                return render_template('organisation.html', students=students)
        else:
            return "Unknown user type", 400  # Return an error for unknown user types
    return redirect(url_for('main.login'))
@main.route("/add_student", methods=['GET', 'POST'])
def add_student():
    id  =request.form['id']
    org_id= session['user_id']
    name=request.form['name']
    age=request.form['age']
    print(id,name,age,org_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (org_id,stud_id,name,age) VALUES (%s, %s, %s,%s)",
                   (org_id,id,name,age))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('main.dashboard'))

@main.route("/update_student/<student_id>",methods=['GET','POST'])
def update_student(student_id):
    name = request.form.get('name')
    print(student_id,name)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET name= %s where stud_id = %s",(name,student_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('main.dashboard'))


@main.route("/delete_student/<student_id>",methods=["GET","POST"])
def delete_student(student_id):

    print(student_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE stud_id=%s", (student_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('main.dashboard'))

@main.route("/record_student/<student_id>",methods=["GET","POST"])
def record_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM results WHERE stud_id=%s ORDER BY sno DESC LIMIT 5", (student_id,))
    records = cursor.fetchall()
    print(records)
    conn.commit()
    # Close the database connection
    cursor.close()
    conn.close()

@main.route("/test/<student_id>", methods=["GET", "POST"])
def test(student_id):
    return render_template("test.html",student_id=student_id)
@main.route("/predict/<student_id>",methods=["POST"])
def predict(student_id):
    input=[]
    for i in range(1,36):
        value = request.form.get("q"+str(i))
        input.append(value)
    int_list = [int(item) for item in input]
    predict_val = predict_value([int_list])
    result=""
    score = sum(int_list)
    if score>=0 and score<=22:
        actual_val="Mild"
    elif score>=23 and score<=29:
        actual_val="Moderate"
    elif score>=30 and score<=999:
        actual_val = "Serious"
    if actual_val == predict_val:
        result+= predict_val
    else:
        result += actual_val
    now = datetime.now()

    # Format the date as 'YYYY-MM-DD'
    formatted_date = now.strftime('%Y-%m-%d')

    # Store the formatted date in a variable
    date = formatted_date

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM latest_results WHERE stud_id = %s", (student_id,))
    rows = cursor.fetchall()

    # Get the count of rows returned
    row_count = len(rows)

    if row_count > 0:
        # If record exists, update it
        print('update called')
        query = """
            UPDATE latest_results
            SET score = %s, result = %s, date = %s
            WHERE stud_id = %s
            """
        cursor.execute(query, (score, result, date, student_id))
    else:
        # If no record exists, insert a new row
        query = """
            INSERT INTO latest_results (stud_id, score, result, date)
            VALUES (%s, %s, %s, %s)
            """
    cursor.execute(query, (student_id, score, result, date))
    conn.commit()

    cursor.execute("INSERT INTO results (stud_id, result, score,date) VALUES (%s, %s, %s,%s)",(student_id,result,score, date))
    conn.commit()
    cursor.close()
    conn.close()
    return render_template("precautions.html",result=result)

@main.route("/report")
def report():
    org_id = session['user_id'] # Get the org_id from the query parameters



    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to get the latest 5 records for each student

    query = """
           SELECT s.name, r.result, r.score, r.date
           FROM students s
           JOIN results r ON s.stud_id = r.stud_id
           JOIN (
               SELECT stud_id, date
               FROM (
                   SELECT stud_id, date
                   FROM results
                   WHERE stud_id IN (
                       SELECT stud_id
                       FROM students
                       WHERE org_id = %s
                   )
                   ORDER BY date DESC
               ) AS sorted_results
               GROUP BY stud_id
               HAVING COUNT(*) <= 5
           ) latest_results ON r.stud_id = latest_results.stud_id AND r.date = latest_results.date
           WHERE s.org_id = %s
           ORDER BY s.name, r.date DESC
       """

    cursor.execute(query, (org_id, org_id))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # Organize data by student
    reports_by_student = {}
    for name, result, score, date in rows:
        if name not in reports_by_student:
            reports_by_student[name] = []
        reports_by_student[name].append({'result': result, 'score': score, 'date': date})

    # Ensure only the latest 5 records are shown
    for student in reports_by_student:
        reports_by_student[student] = reports_by_student[student][:5]

    return render_template("report.html", reports_by_student=reports_by_student)

@main.route('/api/session')
def get_session():
    # Return session data as JSON
    return jsonify({
        'is_logged_in': 'user_id' in session,
        'user_type': session.get('user_type')
    })
@main.route("/logout")
def logout():
    session.pop('user_id', None)  # Remove the user ID from the session
    session.pop('user_type', None)  # Remove the user type from the session
    return redirect(url_for('main.login'))


@main.route('/doctor_dashboard', methods=['GET', 'POST'])
def doctor_dashboard():
    doctor_id = session.get("user_id") # You can get the logged-in doctor ID dynamically if needed
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch organizations where the organization's address matches the doctor's address
    cursor.execute("""
        SELECT o.organization_id ,o.name, o.contact_num
        FROM organization o
        JOIN doctor d ON o.address = d.address
        WHERE d.doctor_id = %s
    """, (doctor_id,))

    organizations = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('doctor.html', organizations=organizations)


@main.route('/view_students/<int:org_id>', methods=['GET'])
def view_students(org_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch students from the selected organization with serious results
    cursor.execute("""
        SELECT s.name, lr.result, lr.score, lr.date
        FROM students s
        JOIN latest_results lr ON s.stud_id = lr.stud_id
        WHERE s.org_id = %s AND lr.result = 'serious'
    """, (org_id,))

    students_with_serious_results = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('results.html', students=students_with_serious_results)
@main.route("/thankyou",methods=["GET"])
def thankyou():
    return render_template("thankyou.html")


@main.route('/student_report', methods=['GET'])
def student_report():
    org_id = session.get('user_id')  # Get org_id from request parameters (can be passed via form/button)
    print(org_id)
    if org_id:
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL query to join students with their latest results based on org_id
        query = """
        SELECT students.name, latest_results.result, latest_results.score, latest_results.date
        FROM students
        JOIN latest_results ON students.stud_id = latest_results.stud_id
        WHERE students.org_id = %s
        """
        cursor.execute(query, (org_id,))

        student_data = cursor.fetchall()
        print(student_data)
        conn.close()

        # Render the result on a report HTML page
        return render_template('student_report.html', students=student_data, org_id=org_id)
    else:
        return ("Organization ID is required to generate the report", 400)


@main.route('/doctors', methods=['GET'])
def doctors():
    result = request.args.get('result')  # Get the result (Mild, Moderate, Serious)
    org_id =session.get('user_id')  # Get organization ID

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Query to get the organization address
    cursor.execute("SELECT address FROM organization WHERE organization_id = %s", (org_id,))
    org_address_row = cursor.fetchone()
    print(org_address_row['address'])
    if org_address_row:
        org_address = org_address_row['address']
        print('if block executed')
        # Fetch doctors based on the result
        if result == "Serious":
            query = """
            SELECT *
            FROM doctors_details
            WHERE location = %s
            ORDER BY rating DESC
            LIMIT 3
            """
        elif result == "Moderate":
            query = """
            SELECT *
            FROM doctors_details
            WHERE location = %s
            ORDER BY rating ASC
            LIMIT 3
            """
        else:
            # For Mild condition, return an empty list or handle accordingly
            doctors = []
            return render_template('doctors_list.html', doctors=doctors)

        cursor.execute(query, (org_address,))
        doctors = cursor.fetchall()
        print(doctors)
    else:
        doctors = []
    cursor.close()
    conn.close()

    return render_template('doctors_list.html', doctors=doctors)

