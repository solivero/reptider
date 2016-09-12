from . import db

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Unicode(100))
    _class = db.Column(db.Unicode(3))
    first_name = db.Column(db.Unicode(50))
    last_name = db.Column(db.Unicode(50))
    lessons = db.relationship('Lesson', backref='student', lazy='dynamic')

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer)
    start_min = db.Column(db.Integer)
    end_min = db.Column(db.Integer)
    subject = db.Column(db.Unicode(255))
    info = db.Column(db.Unicode(255))
    teachers = db.Column(db.Unicode(255))
    _class = db.Column(db.Unicode(255))
    rooms = db.Column(db.Unicode(511))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
