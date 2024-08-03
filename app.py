from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import csv
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 데이터 저장을 위한 클래스 정의
class Dancer:
    def __init__(self, name):
        self.name = name
        self.scores = {}

    def add_score(self, question, score):
        self.scores[question] = score

class Question:
    def __init__(self, content):
        self.content = content

# 초기화
dancers = []
questions = []

# 기본 비밀번호 설정
app.config['PASSWORD'] = None

# 비밀번호 설정 페이지
@app.route('/set_password', methods=['GET', 'POST'])
def set_password_page():
    if request.method == 'POST':
        password = request.form['password']
        app.config['PASSWORD'] = password
        flash('비밀번호가 설정되었습니다.')
        return redirect(url_for('login'))
    return render_template('set_password.html')

# 로그인 페이지
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == app.config['PASSWORD']:
            return redirect(url_for('manage'))
        else:
            flash('비밀번호가 틀렸습니다.')
    return render_template('login.html')

# 관리 페이지
@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if request.method == 'POST':
        if 'add_dancer' in request.form:
            name = request.form['dancer_name']
            dancers.append(Dancer(name))
            flash(f'댄서 {name}가 추가되었습니다.')
        elif 'add_question' in request.form:
            content = request.form['question_content']
            questions.append(Question(content))
            flash(f'질문 "{content}"가 추가되었습니다.')
        elif 'add_score' in request.form:
            dancer_name = request.form['dancer_name']
            question_content = request.form['question_content']
            score = int(request.form['score'])
            dancer = next((d for d in dancers if d.name == dancer_name), None)
            if dancer:
                dancer.add_score(question_content, score)
                flash(f'댄서 {dancer_name}에 대한 점수가 추가되었습니다.')
        elif 'export' in request.form:
            return export_to_csv()
    return render_template('manage.html', dancers=dancers, questions=questions)

def export_to_csv():
    file_path = os.path.join(os.getcwd(), 'dancer_scores.csv')
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['메인댄서', '점수', '객관문장']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for dancer in dancers:
            for question, score in dancer.scores.items():
                writer.writerow({'메인댄서': dancer.name, '점수': score, '객관문장': question})

    return send_file(file_path, as_attachment=True, download_name='dancer_scores.csv')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
