from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, func
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from faker import Faker
import random
from datetime import datetime
import argparse

# Оголошення базового класу моделей
Base = declarative_base()

class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    students = relationship('Student', backref='group')

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    group_id = Column(Integer, ForeignKey('groups.id'))
    grades = relationship('Grade', backref='student')

class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    subjects = relationship('Subject', backref='teacher')

class Subject(Base):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    grades = relationship('Grade', backref='subject')

class Grade(Base):
    __tablename__ = 'grades'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    value = Column(Integer)
    date = Column(Date)

def setup_database():
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/mydatabase')
    Base.metadata.create_all(engine)
    return engine

def fill_database(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    faker = Faker()

    # Create groups
    groups = [Group(name=f'Group {i}') for i in range(1, 4)]
    session.add_all(groups)

    # Create teachers
    teachers = [Teacher(name=faker.name()) for _ in range(3)]
    session.add_all(teachers)

    # Create students and subjects
    for _ in range(30):
        group = random.choice(groups)
        student = Student(name=faker.name(), group=group)
        session.add(student)

        for _ in range(random.randint(2, 5)):  # Each student takes 2-5 subjects
            teacher = random.choice(teachers)
            subject = Subject(name=faker.word(), teacher=teacher)
            session.add(subject)

            # Assign grades to the subject
            grade = Grade(student=student, subject=subject, value=random.randint(1, 10), date=faker.date_this_year())
            session.add(grade)

    session.commit()
    session.close()

def main():
    engine = setup_database()
    fill_database(engine)

    parser = argparse.ArgumentParser(description="Database Management CLI")
    parser.add_argument('-a', '--action', required=True, choices=['create', 'list', 'update', 'remove'], help='CRUD action')
    parser.add_argument('-m', '--model', required=True, choices=['Group', 'Student', 'Teacher', 'Subject', 'Grade'], help='Model to interact with')
    parser.add_argument('--name', help='Name for creating or updating')
    parser.add_argument('--id', type=int, help='ID for updating or removing')
    args = parser.parse_args()

    Session = sessionmaker(bind=engine)
    session = Session()

    if args.model and hasattr(eval(args.model), '__tablename__'):
        model = eval(args.model)
        if args.action == 'create' and args.name:
            obj = model(name=args.name)
            session.add(obj)
            session.commit()
            print(f"{args.model} '{args.name}' created.")
        elif args.action == 'list':
            items = session.query(model).all()
            for item in items:
                print(f"ID: {item.id}, Name: {item.name}")
        elif args.action == 'update' and args.id and args.name:
            item = session.query(model).filter_by(id=args.id).first()
            if item:
                item.name = args.name
                session.commit()
                print(f"{args.model} ID {args.id} updated to {args.name}.")
            else:
                print(f"{args.model} ID {args.id} not found.")
        elif args.action == 'remove' and args.id:
            item = session.query(model).filter_by(id=args.id).first()
            if item:
                session.delete(item)
                session.commit()
                print(f"{args.model} ID {args.id} removed.")
            else:
                print(f"{args.model} ID {args.id} not found.")
        else:
            print("Invalid command or arguments.")

    session.close()

if __name__ == '__main__':
    main()
