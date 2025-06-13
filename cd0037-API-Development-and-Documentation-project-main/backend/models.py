from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

database_name = "trivia"
# This path construction is for clarity. Use your own credentials if they differ.
database_path = "postgresql://{}:{}@{}/{}".format('postgres', 'postgres', 'localhost:5432', database_name)

db = SQLAlchemy()

def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    # No need to create_all() here; it's better handled elsewhere

class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    difficulty = Column(Integer, nullable=False)

    # MUST be 'category' to match the database schema from trivia.psql
    category = Column(Integer, ForeignKey('categories.id'), nullable=False)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'difficulty': self.difficulty,
            'category': self.category
        }

class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)

    # backref must NOT be 'category' to avoid a name conflict with the column above.
    questions = relationship('Question', backref='category_ref', lazy=True, cascade="all, delete")

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }