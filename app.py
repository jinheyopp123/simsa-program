from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
import pickle
import csv
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 비밀키 설정

# Global variables to hold data
dancers = []
questions = []

# Load or initialize password
def get_password():
    return session.get('password')

def set_password(password):
    session['password'] = password

@app.route('/')
def index():
    if get_password() is None:
        return redirect(url_for('set_password_page'))
    return redirect(url_for('login'))

@app.route('/set_password', methods=['GET', 'POST'])
def set_password_page():
    if request.method == 'POST':
        password = request.form.get('password')
        if password:
            set_password(password)
            flash('비밀번호가 설정되었습니다. 로그인 페이지로 이동합니다.')
            return redirect(url_for('login'))
        else:
            flash('비밀번호를 입력하세요.')
    return render_template('set_password.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == get_password():
            return redirect(url_for('manage'))
        else:
            flash('비밀번호가 틀렸습니다. 다시 시도해주세요.')
    return render_template('login.html')

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if request.method == 'POST':
        if 'add_dancer' in request.form:
            name = request.form.get('dancer_name').strip()
            if name:
                dancers.append(Dancer(name))
        elif 'add_question' in request.form:
            content = request.form.get('question_content').strip()
            if content:
                questions.append(Question(content))
        elif 'add_score' in request.form:
            dancer_name = request.form.get('dancer')
            question_content = request.form.get('question')
            score = int(request.form.get('score').strip())
            if 0 <= score <= 10:
                dancer = next((d for d in dancers if d.name == dancer_name), None)
                question_index = next((i for i, q in enumerate(questions) if q.content == question_content), None)
                if dancer and question_index is not None:
                    dancer.add_score(score, question_index)
        elif 'add_subjective' in request.form:
            dancer_name = request.form.get('dancer')
            evaluation = request.form.get('subjective_evaluation').strip()
            if evaluation:
                dancer = next((d for d in dancers if d.name == dancer_name), None)
                if dancer:
                    dancer.add_subjective_evaluation(evaluation)
        elif 'export_csv' in request.form:
            return export_to_csv()

    return render_template('manage.html', dancers=dancers, questions=questions)

def export_to_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    header = ['댄서 이름'] + [q.content for q in questions] + ['총 점수', '주관적 평가']
    writer.writerow(header)
    
    # Write data
    for dancer in dancers:
        row = [dancer.name] + dancer.scores + [dancer.total_score()] + ['; '.join(dancer.subjective_evaluations)]
        writer.writerow(row)
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        attachment_filename="dancers_results.csv",
        as_attachment=True,
        mimetype="text/csv"
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

