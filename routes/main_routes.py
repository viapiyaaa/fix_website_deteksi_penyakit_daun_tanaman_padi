from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/upload')
def upload():
    return render_template('deteksi.html')

@main.route('/chatbot')
def chat():
    return render_template('chatbot.html') 