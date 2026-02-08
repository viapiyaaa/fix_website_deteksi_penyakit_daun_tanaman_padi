from flask import Blueprint, render_template

articles = Blueprint('articles', __name__)

@articles.route('/article1')
def article1():
    return render_template('article/article1.html')

@articles.route('/article2')
def article2():
    return render_template('article/article2.html')

@articles.route('/article3')
def article3():
    return render_template('article/article3.html')

@articles.route('/article4')
def article4():
    return render_template('article/article4.html')

@articles.route('/article5')
def article5():
    return render_template('article/article5.html')