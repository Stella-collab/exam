# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

"""
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
"""
import os
from datetime import datetime, timedelta
"""
import flask
from flask import render_template

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    #return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"
    return render_template('index.html');

@app.route('/mainpage', methods=['GET'])
def mainpage():
    #return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"
    return render_template('contact.html');

app.run();
"""
from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from flask_mysqldb import MySQL
import datetime

TEMPLATE_DIR = os.path.abspath('templates')
STATIC_DIR = os.path.abspath('static')

# app = Flask(__name__) # to make the app run without any
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'Exam'

mysql = MySQL(app)

print("Template Dir : ", TEMPLATE_DIR)

# app = Flask(__name__)
# app.config["DEBUG"] = True
# app.static_folder = 'static'


@app.route('/')
def homepage():
    date_object = datetime.date.today()
    session["mindate"] = date_object
    try:
        return render_template("index.html")
    except Exception as e:
        return str(e)


@app.route('/about')
def aboutpage():
    return render_template("about.html")


@app.route('/adminlogin')
def adminlogin():
    return render_template("adminlogin.html")


@app.route('/facultymainpage')
def facultymainpage():
    return render_template("facultymainpage.html")


@app.route('/facultyviewexams')
def facultyviewexams():
    cursor = mysql.connection.cursor()
    cursor.execute(
        ''' Select * from NewExam''')
    rows = cursor.fetchall()
    return render_template("facultyviewexams.html", rows=rows)


@app.route('/facultyalottime')
def facultyalottime():
    return render_template("facultyalottime.html")


@app.route('/facultyviewallotedexams')
def facultyviewallotedexams():
    cursor = mysql.connection.cursor()
    cursor.execute(
        ''' SELECT t1.allotedid, t1.examid, t1.facultyid, t1.timeid, t2.firstname, t2.lastname,t3.examname, t3.semester, t3.examdate, t3.examtime FROM AllotExamDate t1, newfaculty t2, newexam t3 WHERE(t1.FacultyId = t2.facultyid)    AND(t1.examid = t3.examid) ''')
    facultyrows = cursor.fetchall()
    return render_template("facultyviewallotedexams.html", rows=facultyrows)


@app.route('/adminmainpage')
def adminmainpage():
    return render_template("adminmainpage.html")


@app.route('/adminlogincheck', methods=['POST'])
def adminlogincheck():
    if request.method == 'POST':
        uname = request.form['uname']
        pwd = request.form['pwd']
    print("Uname : ", uname, " Pwd : ", pwd);
    if uname == "admin" and pwd == "admin":
        return render_template("adminmainpage.html")
    else:
        return render_template("adminlogin.html", msg="UserName/Password is Invalid")


@app.route('/facultylogincheck', methods=['POST'])
def facultylogincheck():
    if request.method == 'POST':
        uname = request.form['uname']
        pwd = request.form['pwd']
    print("Uname : ", uname, " Pwd : ", pwd)
    cursor = mysql.connection.cursor()
    cursor.execute(
        ''' Select * from NewFaculty where UserName = %s and Password =%s ''', (uname, pwd))
    row = cursor.fetchone()
    if row:
        session["facultyid"] = row[0]
        session["facultyname"] = row[1] + row[2]
        return render_template('facultymainpage.html')
    else:
        return render_template("facultylogin.html", msg="UserName/Password is Invalid")


@app.route('/adminselectexam', methods=['GET'])
def adminselectexam():
    print("Admin Select Exam")
    args = request.args
    roomid = args.get("roomid")
    session.roomid = roomid
    cursor = mysql.connection.cursor()
    query = "Select * from FacultyAllotTime where status = 'Free'"
    cursor.execute(query)
    facultyrows = cursor.fetchall()
    return render_template("adminallotfaculty.html", rows=facultyrows)


@app.route('/adminselectfaculty', methods=['GET'])
def adminselectfaculty():
    print("Admin Select Faculty")
    args = request.args
    timeid = args.get("timeid")
    facultyid = args.get("facultyid")
    roomid = args.get("roomid")
    cursor = mysql.connection.cursor()
    cursor.execute(
        ''' INSERT INTO AllotExamDate(RoomId, FacultyId, TimeId) VALUES(%s, %s, %s) ''',
        (roomid, facultyid, timeid))
    mysql.connection.commit()

    query = "update NewRoom set status = 'Occupied' where roomid = " + roomid
    print(query)
    cursor.execute(query)
    mysql.connection.commit()

    query = "update facultyallottime set status = 'Occupied' where allotid = " + timeid
    print(query)
    cursor.execute(query)
    mysql.connection.commit()

    cursor.close()
    return render_template("adminallotdate.html", msg="Date & Time Alloted for the exam Success")


@app.route('/facultylogin')
def facultylogin():
    return render_template("facultylogin.html")

@app.route('/newroom')
def newroom():
    date_object = datetime.date.today()
    print(date_object)
    date_object1 = datetime.date.today()
    print(date_object1)
    presentday = datetime.date.today()
    tomorrow = presentday + timedelta(1)
    print("Tomorrow = ", tomorrow.strftime('%d-%m-%Y'))
    date_object=tomorrow.strftime('%Y-%m-%d')
    return render_template("newroom.html", mindate=date_object)

@app.route('/addroom', methods=['POST'])
def addroom():
    print("Add Room Function")
    if request.method == 'POST':
        roomnum = request.form['roomnum']
        semester = request.form['semester']
        testtype = request.form['testtype']
        timings = request.form['timings']
        examdate = request.form['examdate']
        examname = request.form['examname']

        sql="";
        if(testtype=="Internals"):
            if(timings=="8:00-9:30" or timings=="10:00-11:30"):
                sql = "Select * from NewRoom where roomnum = '" + roomnum + "' and timings  in('8:00-9:30','10:00-11:30','9:00-10:30', '9:00-12:00')" +  " and testdate = '" + examdate + "'"
            elif(timings=="12:00-13:30" or timings=="15:00-16:30"):
                sql = "Select * from NewRoom where roomnum = '" + roomnum + "' and timings  in('12:00-13:30', '15:00-16:30', '13:00-16:00')" + " and testdate = '" + examdate + "'"
        else:
            if (timings == "9:00-12:00"):
                sql = "Select * from NewRoom where roomnum = '" + roomnum + "' and timings  in('9:00-12:00', '9:00-10:30', '11:00-12:30')" +  " and testdate = '" + examdate + "'"
            elif (timings == "13:00-16:00"):
                sql = "Select * from NewRoom where roomnum = '" + roomnum + "' and timings  in('13:00-16:00','12:00-13:30', '13:00-16:00')" + " and testdate = '" + examdate + "'"

        cursor = mysql.connection.cursor()
        print(sql)
        cursor.execute(sql)
        row = cursor.fetchone()
        if row:
            cursor.close()
            return render_template("newroom.html", msg="Sorry Room Already Alloted")
        else:
            cursor = mysql.connection.cursor()
            cursor.execute(
            ''' INSERT INTO NewRoom(RoomNum, Semester, ExamName, TestType, Timings, TestDate, Status) VALUES(%s, %s, %s, %s, %s, %s, %s) ''',
            (roomnum, semester, examname, testtype, timings, examdate, 'Free'))
            mysql.connection.commit()
            cursor.close()
            return render_template("newroom.html", msg="Room Alloted Success")

@app.route('/newfaculty')
def newfaculty():
    return render_template("newuser.html")

@app.route('/newexam')
def newexam():
    date_object = datetime.date.today()
    print(date_object)
    return render_template("newexam.html", mindate=date_object)


@app.route('/contact')
def contactPage():
    return render_template("contact.html")


@app.route('/adminallotexam')
def adminallotexam():
    status = 'Free'
    cursor = mysql.connection.cursor()
    query = "Select * from newroom where status like 'Free'"
    print(query)
    cursor.execute(query)
    #cursor.execute('''Select * from NewExam''')
    examrows = cursor.fetchall()

    query = "Select * from FacultyAllotTime where status like 'Free'"
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    facultyrows = cursor.fetchall()

    return render_template("adminallotexam.html", examrows=examrows, facultyrows=facultyrows)


@app.route('/addFacultyFreeTime', methods=['POST'])
def addFacultyFreeTime():
    print("Add Faculty Function")
    if request.method == 'POST':
        facultyid = request.form['facultyid']
        facultyname = request.form['facultyname']
        freedate = request.form['freedate']
        freetime = request.form['freetime']
        allotid = request.form['timeid']
        examid = request.form['examid']

        cursor = mysql.connection.cursor()
        cursor.execute(
            ''' INSERT INTO FacultyAllotTime(FacultyId, FacultyName, FreeDate, FreeTime, Status) VALUES(%s, %s, %s, %s, %s) ''',
            (facultyid, facultyname, freedate, freetime, 'Free'))
        mysql.connection.commit()

        cursor.execute(''' Update NewExam set Status = 'Occupied' where examid = %s ''', (examid))
        mysql.connection.commit()

        cursor.execute(''' Update FacultyAllotTime set Status = 'Occupied' where allotid = %s ''', (allotid))
        mysql.connection.commit()

        cursor.close()
    return render_template("facultyalottime.html", msg="Time Alloted Success")


@app.route('/addFaculty', methods=['POST'])
def addFaculty():
    print("Add Faculty Function")
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        uname = request.form['uname']
        pwd = request.form['pwd']
        email = request.form['emailid']
        phnum = request.form['phnum']

        cursor = mysql.connection.cursor()
        cursor.execute(
            ''' INSERT INTO NewFaculty(FirstName, LastName, UserName, Password, EmailId, PhoneNumber) VALUES(%s, %s, %s, %s, %s, %s) ''',
            (fname, lname, uname, pwd, email, phnum))
        mysql.connection.commit()
        cursor.close()
    return render_template("newuser.html", msg="Faculty Added Success")


@app.route('/addExam', methods=['POST'])
def addExam():
    print("Add Exam Function")
    if request.method == 'POST':
        examname = request.form['examname']
        semester = request.form['semester']
        examdate = request.form['examdate']
        examtime = request.form['examtime']

        cursor = mysql.connection.cursor()
        cursor.execute(
            ''' INSERT INTO NewExam(ExamName, Semester, ExamDate, ExamTime, Status) VALUES(%s, %s, %s, %s, %s) ''',
            (examname, semester, examdate, examtime, 'Free'))
        mysql.connection.commit()
        cursor.close()
    return render_template("newexam.html", msg="Exam Added Success")


if __name__ == "__main__":
    app.run(debug=True)
