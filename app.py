from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import pickle
import csv
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 필요한 경우 비밀키 설정

class Dancer:
    def __init__(self, name):
        self.name = name
        self.scores = []
        self.subjective_evaluations = []

    def add_score(self, score, question_index):
        while len(self.scores) <= question_index:
            self.scores.append(0)
        self.scores[question_index] += score

    def add_subjective_evaluation(self, evaluation):
        self.subjective_evaluations.append(evaluation)

    def total_score(self):
        return sum(self.scores)

class Question:
    def __init__(self, content):
        self.content = content

# Global variables to hold data
dancers = []
questions = []

# Hardcoded password (could be changed or loaded from a secure location)
PASSWORD = 'password123'

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    password = request.form.get('password')
    if password == PASSWORD:
        return redirect(url_for('manage'))
    else:
        flash('비밀번호가 틀렸습니다. 다시 시도해주세요.')
        return redirect(url_for('index'))

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
