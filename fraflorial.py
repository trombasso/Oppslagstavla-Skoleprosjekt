import pymysql
from flask import Flask, render_template, request, url_for, flash, redirect

app = Flask(__name__)

app.config['SECRET_KEY'] = "I AM A COOL KEY"

# connect with pymysql
conn = pymysql.connect(host='localhost', user= 'root', password= 'password', db='uit_feedback', cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    with conn.cursor() as cur:
        cur = conn.cursor()
        res = cur.execute("SELECT * FROM feedback")
        feedbacks = cur.fetchall()
        if res > 0:
            return render_template('index.html', feedbacks = feedbacks)
        else:
            flash('No entries in your database!', 'success')
            return render_template('index.html')



@app.route('/submit', methods=['POST'])
def submit():
    with conn.cursor() as cur:
        if request.method == 'POST':
            student = request.form.get('student')
            instructor = request.form.get('instructor')
            email = request.form.get('email')
            rating = request.form.get('rating')
            comments = request.form.get('comments')
            if student == '' or instructor == '' or email == '':
                flash('please enter required fields', 'danger')
                return render_template('index.html')
            
            cur.execute('INSERT INTO feedback (student, instructor, email, rating, comments) VALUES (%s, %s, %s, %s, %s)', [student, instructor, email, rating, comments])
            conn.commit()
            flash('Successfully submitted feedback. Thank you!!', 'success')
            return redirect(url_for('index'))
    

@app.route('/delete/<int:id>')
def delete(id):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM feedback WHERE id = %s", [id])
        conn.commit()
        flash("Feedback deleted successfully", 'success')
        return redirect(url_for('index'))
        
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)