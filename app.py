from flask import Flask, render_template

app = Flask(__name__)

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница тренировки
@app.route('/study')
def study():
    return "Здесь будет тренировка! (пока пусто)"

if __name__ == '__main__':
    app.run(debug=True)