from flask import Flask, render_template, request, redirect,session
import mysql.connector

app = Flask(__name__)
app.secret_key="mysecretkey123"

def get_db_connection():
    return mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql@2026",   # Replace with your MySQL password
    database="studentdb"
)
@app.route("/marks")
def marks():
    if "user" not in session:
        return redirect("/login")
    return render_template("add_marks.html")

def grade_to_point(grade):
    grade = grade.upper()

    if grade == "A":
        return 10
    elif grade == "B":
        return 8
    elif grade == "C":
        return 6
    elif grade == "D":
        return 4
    else:
        return 0

@app.route("/add_marks", methods=["POST"])
def add_marks():

    try:
        student_id = int(request.form["student_id"])
    except:
        return "Invalid Student ID"

    conn = get_db_connection()
    cursor = conn.cursor()

    total = 0
    marks_data = []

    # Read 6 subjects
    for i in range(1, 7):
        subject = request.form[f"subject{i}"]
        grade = request.form[f"grade{i}"]

        points = grade_to_point(grade)
        total += points

        marks_data.append((subject, grade, points))

    # Calculate CGPA
    cgpa = round(total / 6, 2)

    # Save all subjects with CGPA
    for subject, grade, points in marks_data:
        cursor.execute("""
            INSERT INTO marks
            (student_id, subject, grade, points, cgpa)
            VALUES (%s, %s, %s, %s, %s)
        """, (student_id, subject, grade, points, cgpa))

    conn.commit()
    cursor.close()
    conn.close()

    return f"Marks Saved Successfully.<br><br>CGPA = {cgpa}"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )

        user = cursor.fetchone()
        print(user)
        cursor.close()
        conn.close()

        if user:
            session["user"] = username

            if username == "admin":
                return redirect("/dashboard")
            else:
                return redirect("/my_result")
            

        return "Invalid login"

    return render_template("login.html")
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

 

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, password)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/login")

    return render_template("register.html") 

@app.route("/profile")
def profile():

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE name=%s",
        (session["user"],)
    )

    student = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("profile.html", student=student)

@app.route("/my_result")
def my_result():

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get student details
    cursor.execute(
        "SELECT * FROM students WHERE roll_no=%s",
        (session["user"],)
    )
    student = cursor.fetchone()

    if student:
        cursor.execute("""
            SELECT subject, grade, points, cgpa
            FROM marks
            WHERE student_id=%s
        """, (student[0],))

        marks = cursor.fetchall()
    else:
        marks = []

    cursor.close()
    conn.close()

    return render_template(
        "result.html",
        student=student,
        marks=marks
    )
@app.route("/")

def home():
    if "user" not in session:
        return redirect("/login")

    search = request.args.get("search")

    conn = get_db_connection()
    cursor = conn.cursor()

    if search:
        cursor.execute("""
            SELECT * FROM students
            WHERE name LIKE %s OR roll_no LIKE %s
        """, (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("students.html", students=students)
@app.route("/add", methods=["POST"])
def add_student():
    name = request.form["name"]
    roll_no = request.form["roll_no"]
    department = request.form["department"]
    grade=request.form["grade"]
    result=request.form["result"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, roll_no, department,grade,result) VALUES (%s, %s, %s,%s,%s)",
        (name, roll_no, department,grade,result)
    )
    cursor.execute(
        "INSERT INTO users(username,password) VALUES(%s,%s)",(roll_no,"student123")
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/")

@app.route("/attendance")
def attendance():

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, roll_no FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT * FROM attendance")
    attendance = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "attendance.html",
        students=students,
        attendance=attendance
    )

@app.route("/add_attendance", methods=["POST"])
def add_attendance():

    student_id = request.form["student_id"]
    date = request.form["date"]
    status = request.form["status"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO attendance(student_id, date, status) VALUES(%s,%s,%s)",
        (student_id, date, status)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/attendance")

@app.route("/courses")
def courses():

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM courses")

    courses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("courses.html", courses=courses)

@app.route("/add_course", methods=["POST"])
def add_course():

    course_name = request.form["course_name"]
    course_code = request.form["course_code"]
    department = request.form["department"]
    semester = request.form["semester"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO courses(course_name, course_code, department, semester) VALUES(%s,%s,%s,%s)",
        (course_name, course_code, department, semester)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/courses")


@app.route("/edit/<id>", methods=["GET", "POST"])
def edit_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        print("update button clicked")

        name = request.form["name"]
        new_roll_no = request.form["roll_no"]
        department = request.form["department"]
        grade=request.form["grade"]
        result=request.form["result"]    
        cursor.execute(
            "UPDATE students SET name=%s, roll_no=%s, department=%s, grade=%s, result=%s WHERE id=%s",
            (name, new_roll_no, department, grade, result, id)
        )
        print(cursor.rowcount)
        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/")

    cursor.execute(
        "SELECT * FROM students WHERE id=%s",
        (id,)
    )
    student = cursor.fetchone()
    cursor.close()

    return render_template("edit.html", student=student)


@app.route("/delete/<id>")
def delete_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM students WHERE id=%s",
        (id,)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/")


@app.route("/students")
def students():

    if "user" not in session:
        return redirect("/login")

    search = request.args.get("search")

    conn = get_db_connection()
    cursor = conn.cursor()

    if search:
        cursor.execute("""
            SELECT * FROM students
            WHERE name LIKE %s OR roll_no LIKE %s
        """, (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("students.html", students=students)

@app.route("/teachers")
def teachers():
    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM teachers")
    teachers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("teachers.html", teachers=teachers)

@app.route("/add_teacher", methods=["POST"])
def add_teacher():

    name = request.form["name"]
    subject = request.form["subject"]
    phone = request.form["phone"]
    email = request.form["email"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO teachers(name, subject, phone, email) VALUES(%s,%s,%s,%s)",
        (name, subject, phone, email)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/teachers")

@app.route("/edit_teacher/<int:id>", methods=["GET", "POST"])
def edit_teacher(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        subject = request.form["subject"]
        phone = request.form["phone"]
        email = request.form["email"]

        cursor.execute("""
            UPDATE teachers
            SET name=%s, subject=%s, phone=%s, email=%s
            WHERE id=%s
        """, (name, subject, phone, email, id))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/teachers")

    cursor.execute("SELECT * FROM teachers WHERE id=%s", (id,))
    teacher = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("edit_teacher.html", teacher=teacher)

@app.route("/delete_teacher/<int:id>")
def delete_teacher(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM teachers WHERE id=%s", (id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/teachers")

@app.route("/add_student")
def add_student_page():

    if "user" not in session:
        return redirect("/login")

    return render_template("add_student.html")


@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM teachers")
    total_teachers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM courses")
    total_courses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM notices")
    total_notices = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_teachers=total_teachers,
        total_courses=total_courses,
        total_notices=total_notices
    )


@app.route("/fees")
def fees():

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id,name FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT * FROM fees")
    fees = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "fees.html",
        students=students,
        fees=fees
    )


@app.route("/add_fee", methods=["POST"])
def add_fee():

    student_id = request.form["student_id"]
    amount = request.form["amount"]
    paid_date = request.form["paid_date"]
    status = request.form["status"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO fees(student_id,amount,paid_date,status)
        VALUES(%s,%s,%s,%s)
        """,
        (student_id, amount, paid_date, status)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/fees")
@app.route("/exams")
def exams():
    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM exams")
    exams = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("exams.html", exams=exams)


@app.route("/add_exam", methods=["POST"])
def add_exam():

    exam_name = request.form["exam_name"]
    subject = request.form["subject"]
    exam_date = request.form["exam_date"]
    semester = request.form["semester"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO exams(exam_name,subject,exam_date,semester)
        VALUES(%s,%s,%s,%s)
        """,
        (exam_name, subject, exam_date, semester)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/exams")

@app.route("/notice")
def notice():

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM notices")
    notices = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("notice.html", notices=notices)

@app.route("/add_notice", methods=["POST"])
def add_notice():

    title = request.form["title"]
    message = request.form["message"]
    posted_date = request.form["posted_date"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO notices(title, message, posted_date)
        VALUES(%s,%s,%s)
        """,
        (title, message, posted_date)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/notice")

@app.route("/view_all_marks")
def view_all_marks():

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            students.name,
            students.roll_no,
            MAX(marks.cgpa) AS cgpa
        FROM students
        JOIN marks
        ON students.id = marks.student_id
        GROUP BY students.id, students.name, students.roll_no
    """)

    marks = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("view_all_marks.html", marks=marks)
if __name__ == "__main__":
    app.run(debug=True)