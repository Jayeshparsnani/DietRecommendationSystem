from Diet_Recommender import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100))
    profile = db.relationship('Profile', backref='profile')
    information = db.relationship('Information', backref='information')
    diet = db.relationship('Diet_model', backref='diet')
    exercise = db.relationship('Exercise_model', backref='exercise')

    def __repr__(self):
        return '<User %r>' % self.username


class Profile(db.Model):
    __tablename__ = "Profile"
    id = db.Column(db.Integer, primary_key=True)
    Phone = db.Column(db.Integer)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    img_filename = db.Column(db.String())
    # img_data = db.Column(db.LargeBinary)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)


class Information(db.Model):
    __tablename__ = "Information"
    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Float)
    weight = db.Column(db.Integer)
    activity = db.Column(db.String(50))
    Diabetic = db.Column(db.String(50))
    date_table = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)


class Diet_model(db.Model):
    __tablename__ = "Diet_model"
    id = db.Column(db.Integer, primary_key=True)
    breakfast = db.Column(db.String())
    lunch = db.Column(db.String())
    dinner = db.Column(db.String())
    cal = db.Column(db.Float)
    date_table = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)


class Exercise_model(db.Model):
    __tablename__ = "Exercise_model"
    id = db.Column(db.Integer, primary_key=True)
    exercises = db.Column(db.String())
    date_table = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
