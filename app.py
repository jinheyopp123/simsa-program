from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
import pickle
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# 데이터 저장 및 로딩을 위한 파일 경로
DANCERS_FILE = 'dancers.pkl'
QUESTIONS_FILE = 'questions.pkl'
CSV_FILENAME = 'dancers_results.csv'

# 초기 비밀번호
PASSWORD = 'admin'

# 데이터 모델
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

# 전역 변수
dancers = []
questions = []

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == PASSWORD:
            return redirect(url_for('manage'))
        else:
            flash('비밀번호가 맞지 않습니다.')
    return render_template('login.html')

@app.route('/set_password', methods=['GET', 'POST'])
def set_password():
    global PASSWORD
    if request.method == 'POST':
        PASSWORD = request.form.get('password')
        flash('비밀번호가 설정되었습니다.')
        return redirect(url_for('login'))
    return render_template('set_password.html')

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if request.method == 'POST':
        if 'add_dancer' in request.form:
            name = request.form.get('dancer_name')
            if name:
                dancers.append(Dancer(name))
                update_comboboxes()
                flash(f'댄서 {name}이(가) 추가되었습니다.')
        elif 'add_question' in request.form:
            content = request.form.get('question_content')
            if content:
                questions.append(Question(content))
                update_comboboxes()
                flash(f'질문 "{content}"이(가) 추가되었습니다.')
        elif 'add_score' in request.form:
            dancer_name = request.form.get('dancer_name')
            question_content = request.form.get('question_content')
            score = request.form.get('score')
            try:
                score = int(score)
                if not (0 <= score <= 10):
                    raise ValueError
            except ValueError:
                flash('점수는 0에서 10 사이의 정수여야 합니다.')
                return redirect(url_for('manage'))

            dancer = next((d for d in dancers if d.name == dancer_name), None)
            question_index = next((i for i, q in enumerate(questions) if q.content == question_content), None)

            if dancer and question_index is not None:
                dancer.add_score(score, question_index)
                flash(f'{dancer.name}의 "{question_content}"에 대한 점수 {score}이(가) 추가되었습니다.')
            else:
                flash('댄서와 질문을 선택하세요.')
        elif 'add_subjective_evaluation' in request.form:
            dancer_name = request.form.get('dancer_name')
            evaluation = request.form.get('subjective_evaluation')
            if evaluation:
                dancer = next((d for d in dancers if d.name == dancer_name), None)
                if dancer:
                    dancer.add_subjective_evaluation(evaluation)
                    flash(f'{dancer.name}에 대한 주관적 평가가 추가되었습니다.')
                else:
                    flash('댄서를 선택하세요.')
            else:
                flash('주관적 평가 내용을 입력하세요.')
        elif 'export' in request.form:
            return export_to_csv()
        elif 'save' in request.form:
            save_data()
            flash('데이터가 저장되었습니다.')
        elif 'reset' in request.form:
            reset_scores()
            flash('모든 댄서의 점수와 주관적 평가가 초기화되었습니다.')

    return render_template('manage.html', dancers=dancers, questions=questions)

def update_comboboxes():
    # 댄서와 질문 목록을 업데이트합니다.
    pass

def save_data():
    with open(DANCERS_FILE, 'wb') as f:
        pickle.dump(dancers, f)
    with open(QUESTIONS_FILE, 'wb') as f:
        pickle.dump(questions, f)

def load_data():
    global dancers, questions
    try:
        with open(DANCERS_FILE, 'rb') as f:
            dancers = pickle.load(f)
        with open(QUESTIONS_FILE, 'rb') as f:
            questions = pickle.load(f)
    except (FileNotFoundError, EOFError):
        pass

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def export_to_csv():
    if not dancers:
        flash('댄서가 없습니다.')
        return redirect(url_for('manage'))

    # 데이터 준비
    data = {'댄서 이름': [dancer.name for dancer in dancers]}
    for question in questions:
        data[question.content] = [dancer.scores[questions.index(question)] if len(dancer.scores) > questions.index(question) else 0 for dancer in dancers]
    data['총 점수'] = [dancer.total_score() for dancer in dancers]
    data['주관적 평가'] = ['; '.join(dancer.subjective_evaluations) for dancer in dancers]

    # DataFrame 생성 및 CSV로 저장
    df = pd.DataFrame(data)
    df.to_csv(CSV_FILENAME, index=False, encoding='utf-8-sig')

    # 저장된 CSV 파일을 클라이언트에 전송
    return send_file(CSV_FILENAME, as_attachment=True, download_name=CSV_FILENAME)

if __name__ == '__main__':
    load_data()
    app.run(debug=True, port=5000)



