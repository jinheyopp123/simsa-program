from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # 비밀번호 보호를 위한 비밀키
PASSWORD = None
dancers = []  # 댄서 목록을 저장할 리스트

class Dancer:
    def __init__(self, name):
        self.name = name

@app.route('/login', methods=['GET', 'POST'])
def login():
    global PASSWORD
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
                flash(f'댄서 {name}이(가) 추가되었습니다.')
        elif 'export' in request.form:
            return export_to_csv()
    return render_template('manage.html', dancers=dancers)

def export_to_csv():
    if not dancers:
        flash('댄서가 없습니다.')
        return redirect(url_for('manage'))
    
    data = {'댄서': [dancer.name for dancer in dancers], '점수': [''] * len(dancers), '객관문장': [''] * len(dancers)}
    df = pd.DataFrame(data)
    
    csv_file = 'dancers.csv'
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    
    return send_file(csv_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



