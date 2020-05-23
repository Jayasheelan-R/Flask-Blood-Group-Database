from flask import Flask,render_template,request,flash
from flask_mysqldb import MySQL
import yaml
import os

list = ['a+','o+','b+','ab+','a-','o-','b-','ab-','A+','O+','B+','AB+','A-','A-','B-','AB-','O-','Ab+','aB+','Ab-','aB-']


app=Flask(__name__)

db=yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
app.config['SECRET_KEY'] = os.urandom(10)


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')


@app.route('/form', methods=['GET','POST'])
def form():
    if request.method == "POST":
        try:
            form=request.form
            name=form['name'].upper()
            if form['blood_group'] in list:
                blood_group=form['blood_group'].upper()
            cur = mysql.connection.cursor()
            cur.execute("insert into blood values(%s, %s)",(name, blood_group))
            mysql.connection.commit()
            flash('Process Successfully completed')
        except:
            flash('Error Occured!!.... Try Again')
    return render_template('form.html')


@app.route('/info')
def info():
    cur=mysql.connection.cursor()
    result=cur.execute("select * from blood")
    if result > 0:
        info=cur.fetchall()
        x=len(info)
        return render_template('info.html', info=info, x=x)
    else:
        return render_template("empty.html")


@app.route('/delete', methods=['GET','POST'])
def delete():
    if request.method == "POST":
        try:
            form=request.form
            wow=form['wow']
            cur = mysql.connection.cursor()
            cur.execute(f"delete from blood where name='{wow}'")
            mysql.connection.commit()
            flash('Process Successfully completed')
        except:
            flash('Error Occured!!.... Try Again')
    return render_template('delete.html')


@app.route('/select', methods=['GET','POST'])
def select():
    if request.method == "POST":
        try:
            form=request.form
            if form['hii'] in list:
                hii=form['hii'].upper()
            cur = mysql.connection.cursor()
            result  = cur.execute(f"select * from blood where blood_group='{hii}'")
            if result > 0:
                info=cur.fetchall()
                x=len(info)
                return render_template('info.html', info=info, x=x)
            else:
                return render_template("empty.html")
            mysql.connection.commit()
            flash('Process Successfully completed')
        except:
            flash('Error Occured!!.... Try Again')
    return render_template('select.html')



if __name__=="__main__":
    app.run(debug=True)
