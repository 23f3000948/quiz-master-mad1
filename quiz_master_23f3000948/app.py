from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from backend.models import db, User, Quiz, Question, Score, Subject, Chapter
import backend.controllers as controllers
from backend.models import init_db
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'quizmaster-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database Initialization
init_db(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Authentication Routes
app.route('/login', methods=['GET', 'POST'])(controllers.login)
app.route('/signup', methods=['GET', 'POST'])(controllers.signup)
app.route('/logout')(controllers.logout)

# Admin routes
app.route('/admin/dashboard')(controllers.admin_dashboard)
app.route('/admin/subjects/add', methods=['GET', 'POST'])(controllers.add_subject)
app.route('/admin/subjects/<int:subject_id>/edit', methods=['GET', 'POST'])(controllers.edit_subject)
app.route('/admin/subjects/<int:subject_id>/delete', methods=['POST'])(controllers.delete_subject) 
app.route('/admin/subjects/<int:subject_id>')(controllers.view_subject)

app.route('/admin/chapter/<int:subject_id>/add', methods=['GET', 'POST'])(controllers.add_chapter)
app.route('/admin/chapter/<int:chapter_id>/edit', methods=['GET', 'POST'])(controllers.edit_chapter)
app.route('/admin/chapter/<int:chapter_id>/delete')(controllers.delete_chapter)
app.route('/admin/chapter/<int:chapter_id>')(controllers.view_chapter)

app.route('/admin/quiz/<int:chapter_id>/add', methods=['GET', 'POST'])(controllers.add_quiz)
app.route('/admin/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])(controllers.edit_quiz)
app.route('/admin/quiz/<int:quiz_id>/delete')(controllers.delete_quiz)
app.route('/admin/quiz/<int:quiz_id>')(controllers.view_quiz)
app.route('/admin/quiz/<int:quiz_id>/participation')(controllers.admin_quiz_participation)

app.route('/admin/question/<int:quiz_id>/add', methods=['GET', 'POST'])(controllers.add_question)
app.route('/admin/question/<int:question_id>/edit', methods=['GET', 'POST'])(controllers.edit_question)
app.route('/admin/question/<int:question_id>/delete')(controllers.delete_question)

app.route('/admin/api/top-scores-data', methods=['GET'])(controllers.top_scores_data)
app.route('/admin/api/user-attempts-data', methods=['GET'])(controllers.user_attempts_data)

app.route('/admin/summary')(controllers.admin_summary)

# User Management Routes
app.route('/admin/users')(controllers.manage_users)
app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])(controllers.edit_user)
app.route('/admin/users/<int:user_id>/delete')(controllers.delete_user)

# User routes
app.route('/dashboard')(controllers.user_dashboard)
app.route('/subjects')(controllers.browse_subjects)
app.route('/chapter/<int:subject_id>')(controllers.browse_chapters)
app.route('/browse_quizzes/<int:chapter_id>')(controllers.browse_quizzes)
app.route('/quiz/<int:quiz_id>')(controllers.view_quiz)
app.route('/quiz/<int:quiz_id>/submit', methods=['POST'])(controllers.take_quiz)
app.route('/score/<int:score_id>')(controllers.view_score)
app.route('/scores')(controllers.user_scores)
app.route('/summary')(controllers.user_summary)
app.route('/api/search/subjects')(controllers.search_subjects)


# Base Index Route
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)