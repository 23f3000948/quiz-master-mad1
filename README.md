# quiz-master-mad1
Project under Modern Application Development 1 from Indian Institute of Technology -Madras 
# Quiz Master 🎓📝

## Overview
Quiz Master is a comprehensive web-based quiz management application that allows users to take quizzes across various subjects and chapters. The application supports both student and admin functionalities, providing a robust platform for educational assessment.

## Features

### User Features
- User Registration and Authentication
- Browse Subjects and Chapters
- Take Quizzes
- View Quiz Scores
- Personal Dashboard
- User Performance Summary

### Admin Features
- Manage Subjects, Chapters, and Quizzes
- Add, Edit, and Delete Questions
- User Management
- Detailed Quiz and User Statistics
- Performance Analytics

## Technology Stack
- Backend: Flask (Python)
- Database: SQLAlchemy with SQLite
- Authentication: Flask-Login
- Password Hashing: Bcrypt
- Frontend: HTML, potentially with JavaScript for dynamic interactions

## Prerequisites
- Python 3.8+
- pip (Python Package Manager)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/quiz-master.git
cd quiz-master
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install flask flask-sqlalchemy flask-login flask-bcrypt
```

### 4. Initialize the Database
The application will automatically create the database and an admin user on first run.

### 5. Run the Application
```bash
python app.py
```

## Default Admin Credentials
- Username: `admin@quizmaster.com`
- Password: `admin123`

## Project Structure
```
quiz-master/
│
├── app.py                 # Main Flask application
├── backend/
│   ├── controllers.py     # Route handlers and business logic
│   └── models.py          # Database models
├── templates/             # HTML templates

```

## Security Features
- Secure password hashing
- Role-based access control
- Protected admin routes
- User authentication required for most actions

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## Contact
Vashisht Brahmbhatt : 23f3000948@ds.study.iitm.ac.in
```
