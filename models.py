from sqlalchemy import Column, Integer, String, Date, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    students = relationship('Student', backref='group')

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    group_id = Column(Integer, ForeignKey('groups.id'))
    grades = relationship('Student', backref='student')

class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    subject =relationship('Subject', backref='teacher')

class Subject(Base):
    __tablename__ ='subjects'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    grades = relationship('Grade', backref='subject')

class Grade(Base):
    __tablename__ = 'grades'
    id = Column(Integer, primary_key=True)
    value = Column(Integer)
    student_id = Column(Integer, ForeignKey('students.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    date = Column(Date)

def create_db(engine_url='postgresql://postgres:postgres@localhost:5432/mydatabase'):
    engine = create_engine(engine_url)
    Base.metadata.create_all(engine)
    return engine
