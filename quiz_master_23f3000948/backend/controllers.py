from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from backend.models import db, User, Subject, Chapter, Quiz, Question, Score
from flask import jsonify
import json

#Authentication Controllers(24-27)

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid Credentials')
    return render_template('login.html')

def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        qualification = request.form['qualification']
        dob_str = request.form['dob']
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid Date of Birth')
            return render_template('signup.html')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.')
            return render_template('signup.html')
        
        user = User(username=username, fullname=fullname, qualification=qualification, dob=dob)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('user_dashboard'))
    return render_template('signup.html')

@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#Admin Controllers(30-54)
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    stats = {
        'total_subjects': Subject.query.count(),
        'total_chapters': Chapter.query.count(),
        'total_quizzes': Quiz.query.count(),
        'total_users': User.query.count()
    }
    
    subjects = Subject.query.all()
    users = User.query.all()
    quizzes = Quiz.query.all()
    
    return render_template('admin_dashboard.html', stats=stats, subjects=subjects, users=users, quizzes=quizzes)

#addding a subject
@login_required
def add_subject():
    if not current_user.is_admin:
        return jsonify({'error': 'You are not authorized to perform this action'}), 403
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name:
            flash('Name is required')
            return redirect(url_for('admin_dashboard'))
        
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()

        flash('Subject added successfully')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_subject.html')

#editing a subject
@login_required
def edit_subject(subject_id):
    if not current_user.is_admin:
        return jsonify({'error': 'You are not authorized to perform this action'}), 403
    
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name:
            flash('Name is required')
            return redirect(url_for('admin_dashboard'))
        
        subject.name = name
        subject.description = description
        db.session.commit()

        flash('Subject updated successfully')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_subject.html', subject=subject)

#deleting a subject
@login_required
def delete_subject(subject_id):
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    subject = Subject.query.get_or_404(subject_id)
    
    try:
        # Delete associated chapters and quizzes
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        for chapter in chapters:
            quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()
            for quiz in quizzes:
                Question.query.filter_by(quiz_id=quiz.id).delete()
                Score.query.filter_by(quiz_id=quiz.id).delete()
                db.session.delete(quiz)
            db.session.delete(chapter)
        
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting subject. Please try again.', 'danger')
        
    return redirect(url_for('admin_dashboard'))

#viewing a subject
@login_required
def view_subject(subject_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    
    return render_template('view_subject.html', subject=subject, chapters=chapters)


#adding a chapter
@login_required
def add_chapter(subject_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Chapter name is required', 'danger')
            return redirect(url_for('view_subject', subject_id=subject_id))
        
        new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        
        flash('Chapter added successfully', 'success')
        return redirect(url_for('view_subject', subject_id=subject_id))
    
    return render_template('add_chapter.html', subject=subject)

#editing a chapter
@login_required
def edit_chapter(chapter_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Chapter name is required', 'danger')
            return redirect(url_for('view_subject', subject_id=chapter.subject_id))
        
        chapter.name = name
        chapter.description = description
        db.session.commit()
        
        flash('Chapter updated successfully', 'success')
        return redirect(url_for('view_subject', subject_id=chapter.subject_id))
    
    return render_template('edit_chapter.html', chapter=chapter)

#deleting a chapter
def delete_chapter(chapter_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id
    
    db.session.delete(chapter)
    db.session.commit()
    
    flash('Chapter deleted successfully', 'success')
    return redirect(url_for('view_subject', subject_id=subject_id))

#viewing a chapter
@login_required
def view_chapter(chapter_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    
    return render_template('view_chapter.html', chapter=chapter, quizzes=quizzes)

#adding a quiz
@login_required
def add_quiz(chapter_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        date_str = request.form.get('date_of_quiz')
        time_duration = request.form.get('time_duration')
        remarks = request.form.get('remarks')

        try:
            date_of_quiz = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid Date', 'danger')
            return redirect(url_for('view_chapter', chapter_id=chapter_id))
        
        new_quiz = Quiz(
            chapter_id = chapter_id,
            date_of_quiz = date_of_quiz,
            time_duration = time_duration,
            remarks = remarks
        )

        db.session.add(new_quiz)
        db.session.commit()

        flash('Quiz added successfully', 'success')
        return redirect(url_for('view_chapter', chapter_id=chapter_id))
    
    return render_template('add_quiz.html', chapter=chapter)

#editing a quiz
@login_required
def edit_quiz(quiz_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        date_str = request.form.get('date_of_quiz')
        quiz.time_duration = request.form.get('time_duration')
        quiz.remarks = request.form.get('remarks')
        
        try:
            quiz.date_of_quiz = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'danger')
            return redirect(url_for('view_quiz', quiz_id=quiz_id))
        
        db.session.commit()
        
        flash('Quiz updated successfully', 'success')
        return redirect(url_for('view_quiz', quiz_id=quiz_id))
    
    return render_template('edit_quiz.html', quiz=quiz)

#deleting a quiz
@login_required
def delete_quiz(quiz_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    quiz=Quiz.query.get_or_404(quiz_id)
    chapter_id = quiz.chapter_id

    db.session.delete(quiz)
    db.session.commit()

    flash('Quiz deleted successfully', 'success')
    return redirect(url_for('view_chapter', chapter_id=chapter_id))

#viewing a quiz (for admin)
@login_required
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if current_user.is_admin:
        return render_template('view_quiz_admin.html', quiz=quiz, questions=questions)
    else:
        # here it checks for the user who is not an admin
        existing_score = Score.query.filter_by(quiz_id=quiz_id, user_id=current_user.id).first()
        if existing_score:
            flash('You have already attempted this quiz', 'info')
            return redirect(url_for('view_score', score_id=existing_score.id))
        return render_template('view_quiz.html', quiz=quiz, questions=questions)
    
#adding a question
@login_required
def add_question(quiz_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        question_statement = request.form.get('question_statement')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = request.form.get('correct_option')

        if not all([question_statement, option1, option2, option3, option4, correct_option]):
            flash('All fields are required', 'danger')
            return redirect(url_for('view_quiz', quiz_id=quiz_id))
        
        new_question = Question(
            quiz_id=quiz_id,
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option
        )

        db.session.add(new_question)
        db.session.commit()

        flash('Question added successfully', 'success')
        return redirect(url_for('view_quiz', quiz_id=quiz_id))
    
    return render_template('add_question.html', quiz=quiz)

#editing a question
@login_required
def edit_question(question_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        question.question_statement = request.form.get('question_statement')
        question.option1 = request.form.get('option1')
        question.option2 = request.form.get('option2')
        question.option3 = request.form.get('option3')
        question.option4 = request.form.get('option4')
        question.correct_option = request.form.get('correct_option')

        db.session.commit()

        flash('Question updated successfully', 'success')
        return redirect(url_for('view_quiz', quiz_id=question.quiz_id))
    
    return render_template('edit_question.html', question=question)

#deleting a question
@login_required
def delete_question(question_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id

    db.session.delete(question)
    db.session.commit()

    flash('Question deleted successfully', 'success')
    return redirect(url_for('view_quiz', quiz_id=quiz_id))

# Quiz Participation view
def admin_quiz_participation(quiz_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    quiz = Quiz.query.get_or_404(quiz_id)
    scores = Score.query.filter_by(quiz_id=quiz_id).all()

    return render_template('admin_quiz_participation.html', quiz=quiz, scores=scores)

#(admin_summary - line 55)
@login_required
def admin_summary():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    stats = {
        'total_subjects': Subject.query.count(),
        'total_chapters': Chapter.query.count(),
        'total_quizzes': Quiz.query.count(),
        'total_users': User.query.count()
    }
    
    quizzes = Quiz.query.all()
    
    # Prepare data for charts
    quiz_participation_data = []
    performance_data = []
    for quiz in quizzes:
        scores = Score.query.filter_by(quiz_id=quiz.id).all()
        total_students = len(scores)
        average_score = sum(score.total_scored for score in scores) / total_students if total_students > 0 else 0
        quiz_participation_data.append({
            'quiz': quiz.remarks or f'Quiz #{quiz.id}',
            'total_students': total_students
        })
        performance_data.append({
            'quiz': quiz.remarks or f'Quiz #{quiz.id}',
            'average_score': round(average_score, 2)
        })

    return render_template(
        'admin_summary.html', 
        stats=stats,
        quizzes=quizzes,
        quiz_participation_data=json.dumps(quiz_participation_data),
        performance_data=json.dumps(performance_data)
    )

#Summary Stuffs
@login_required
def top_scores_data():
    if not current_user.is_admin:
        return jsonify({'error': 'You are not authorized to perform this action'}), 403
    
    try:
        quiz_scores = []
        quizzes = Quiz.query.all()
        
        for quiz in quizzes:
            # Find the highest score for this quiz
            highest_score = Score.query.filter_by(quiz_id=quiz.id).order_by(Score.total_scored.desc()).first()
            
            if highest_score:
                student = User.query.get(highest_score.user_id)
                if student:
                    quiz_scores.append({
                        'quiz_name': quiz.remarks or f'Quiz #{quiz.id}',
                        'student_name': student.fullname,
                        'score': highest_score.total_scored,
                        'total_questions': highest_score.total_questions,
                        'percentage': round((highest_score.total_scored / highest_score.total_questions) * 100, 2) if highest_score.total_questions > 0 else 0
                    })
        
        return jsonify(quiz_scores)
    
    except Exception as e:
        print(f"Error in top_scores_data: {str(e)}") 
        return jsonify({'error': 'Internal server error'}), 500

@login_required
def user_attempts_data():
    if not current_user.is_admin:
        return jsonify({'error': 'You are not authorized to perform this action'}), 403
    
    subjects = Subject.query.all()
    data = {
        'subjects': [subject.name for subject in subjects],
        'attempt_counts': []
    }
    
    for subject in subjects:
        attempt_count = 0
        for chapter in subject.chapters:
            for quiz in chapter.quizzes:
                attempt_count += Score.query.filter_by(quiz_id=quiz.id).count()
        data['attempt_counts'].append(attempt_count)
    
    return jsonify(data)


#Search Controllers(admin)
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    # server-side search
    subject_search = request.args.get('subject_search', '')
    user_search = request.args.get('user_search', '')
    quiz_search = request.args.get('quiz_search', '')
    
    #subject search
    if subject_search:
        subjects = Subject.query.filter(
            (Subject.name.ilike(f'%{subject_search}%')) | 
            (Subject.description.ilike(f'%{subject_search}%'))
        ).all()
    else:
        subjects = Subject.query.all()
    
    #user search
    if user_search:
        users = User.query.filter(
            (User.username.ilike(f'%{user_search}%')) | 
            (User.fullname.ilike(f'%{user_search}%')) |
            (User.qualification.ilike(f'%{user_search}%'))
        ).all()
    else:
        users = User.query.all()
    
    #quizzes search
    if quiz_search:
        quizzes = Quiz.query.filter(
            (Quiz.remarks.ilike(f'%{quiz_search}%'))
        ).all()
    else:
        quizzes = Quiz.query.all()
    
    stats = {
        'total_subjects': Subject.query.count(),
        'total_chapters': Chapter.query.count(),
        'total_quizzes': Quiz.query.count(),
        'total_users': User.query.count()
    }
    
    return render_template('admin_dashboard.html', stats=stats, subjects=subjects, users=users, quizzes=quizzes)

#User Management Controllers(57-60)

@login_required
def manage_users():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    users = User.query.all()
    return render_template('manage_users.html', users=users)


#User Controllers(62-72)
@login_required
def user_dashboard():
    recent_scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.date.desc()).limit(5).all()
    return render_template('user_dashboard.html', recent_scores=recent_scores)

#(browse_subjects)
@login_required
def browse_subjects():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    subjects = Subject.query.all()
    return render_template('browse_subjects.html', subjects=subjects)

#(browse_chapter)
@login_required
def browse_chapters(subject_id):
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    
    return render_template('browse_chapters.html', subject=subject, chapters=chapters)

#(browse_quiz)
def browse_quizzes(chapter_id):
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    
    # Add info about whether user has taken each quiz
    quiz_info = []
    for quiz in quizzes:
        score = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz.id).first()
        quiz_info.append({
            'quiz': quiz,
            'taken': score is not None,
            'score': score
        })
    
    return render_template('browse_quizzes.html', chapter=chapter, quiz_info=quiz_info)

#(take_quiz)
@login_required
def take_quiz(quiz_id):
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    # Check if user has already attempted the quiz
    existing_score = Score.query.filter_by(quiz_id=quiz_id, user_id=current_user.id).first()
    if existing_score:
        flash('You have already attempted this quiz', 'info')
        return redirect(url_for('view_score', score_id=existing_score.id))
    
    if request.method == 'POST':
        total_questions = len(questions)
        total_scored = 0

        for question in questions:
            selected_option = request.form.get(f'question_{question.id}')
            if selected_option == str(question.correct_option):
                total_scored += 1

        score = Score(
            user_id=current_user.id,
            quiz_id=quiz_id,
            total_scored=total_scored,
            total_questions=total_questions  # Ensure total_questions is set
        )

        db.session.add(score)
        db.session.commit()

        flash('Quiz submitted successfully', 'success')
        return redirect(url_for('view_score', score_id=score.id))

    return render_template('take_quiz.html', quiz=quiz, questions=questions)

#(view_score)
@login_required
def view_score(score_id):
    score = Score.query.get_or_404(score_id)
    
    # Only allow the user who took the quiz or admin to view
    if score.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('user_dashboard'))
    
    quiz = Quiz.query.get(score.quiz_id)
    chapter = Chapter.query.get(quiz.chapter_id)
    subject = Subject.query.get(chapter.subject_id)
    
    percentage = (score.total_scored / score.total_questions) * 100
    
    return render_template(
        'view_score.html',
        score=score,
        quiz=quiz,
        chapter=chapter,
        subject=subject,
        percentage=percentage
    )

#(user_scores)
@login_required
def user_scores():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    scores = Score.query.filter_by(user_id=current_user.id).all()
    
    score_details = []
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        percentage = (score.total_scored / score.total_questions) * 100
        
        score_details.append({
            'score': score,
            'quiz': quiz,
            'chapter': chapter,
            'subject': subject,
            'percentage': percentage
        })
    
    return render_template('user_scores.html', scores=scores, score_details=score_details)

#User Summary Controllers
@login_required
def user_summary():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    # Get all scores for the current user
    user_scores = Score.query.filter_by(user_id=current_user.id).all()
    
    # Basic stats
    total_quizzes_taken = len(user_scores)
    if total_quizzes_taken > 0:
        average_score = sum(score.total_scored for score in user_scores) / total_quizzes_taken
        average_percentage = sum((score.total_scored / score.total_questions) * 100 for score in user_scores) / total_quizzes_taken
    else:
        average_score = 0
        average_percentage = 0
    
    # data for performance chart
    performance_data = []
    subject_performance = {}
    
    for score in user_scores:
        quiz = Quiz.query.get(score.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        
        percentage = (score.total_scored / score.total_questions) * 100
        
        # Data for quiz performance over time
        performance_data.append({
            'quiz_name': quiz.remarks or f'Quiz #{quiz.id}',
            'percentage': round(percentage, 2),
            'date': score.date.strftime('%Y-%m-%d')
        })
        
        # Calculate average performance by subject
        if subject.name not in subject_performance:
            subject_performance[subject.name] = {
                'total_percentage': percentage,
                'count': 1
            }
        else:
            subject_performance[subject.name]['total_percentage'] += percentage
            subject_performance[subject.name]['count'] += 1
    
    # average calc
    subject_averages = {
        subject: {
            'average': round(data['total_percentage'] / data['count'], 2)
        }
        for subject, data in subject_performance.items()
    }
    
    stats = {
        'total_quizzes_taken': total_quizzes_taken,
        'average_score': round(average_score, 2),
        'average_percentage': round(average_percentage, 2),
        'highest_score': max((score.total_scored for score in user_scores), default=0),
        'recent_activity': len([score for score in user_scores if (datetime.now() - score.date).days <= 30])
    }
    
    return render_template(
        'user_summary.html',
        stats=stats,
        performance_data=json.dumps(performance_data),
        subject_averages=json.dumps(subject_averages)
    )


# API for searching subjects
def search_subjects():
    query = request.args.get('query', '')
    
    if query:
        subjects = Subject.query.filter(
            (Subject.name.ilike(f'%{query}%')) | 
            (Subject.description.ilike(f'%{query}%'))
        ).all()
    else:
        subjects = Subject.query.all()
    
    result = []
    for subject in subjects:
        result.append({
            'id': subject.id,
            'name': subject.name,
            'description': subject.description
        })
    
    return jsonify(result)

#API Controllers

# User quiz status
@login_required
def user_quiz_status(chapter_id):
    if current_user.is_admin:
        return jsonify({'error': 'Admin users should use admin endpoints'}), 403
    
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    
    result = []
    for quiz in quizzes:
        score = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz.id).first()
        
        status = {
            'quiz_id': quiz.id,
            'taken': score is not None
        }
        
        if score:
            status['score'] = {
                'id': score.id,
                'total_scored': score.total_scored,
                'total_questions': score.total_questions
            }
        
        result.append(status)
    
    return jsonify(result)


#(edit_user)
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.fullname = request.form.get('fullname')
        user.qualification = request.form.get('qualification')
        dob_str = request.form['dob']
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid Date of Birth, please use YYYY-MM-DD format', 'danger')
            return render_template('edit_user.html', user=user)
        
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('manage_users'))
    
    return render_template('edit_user.html', user=user)

#(delete_user)
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('manage_users'))

