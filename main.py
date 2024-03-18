from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import declarative_base
from faker import Faker
import random
from datetime import datetime

# Підключення до бази даних PostgreSQL
engine = create_engine('postgresql://postgres:postgres@localhost:5432/mydatabase')

# Створення сесії
Session = sessionmaker(bind=engine)
session = Session()

# Оголошення базового класу моделей
Base = declarative_base()

# Оголошення моделей
class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String)

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    group_id = Column(Integer, ForeignKey('groups.id'))
    group = relationship('Group', backref='students')

class Teacher(Base):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True)
    name = Column(String)

class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    teacher = relationship('Teacher', backref='subjects')

class Grade(Base):
    __tablename__ = 'grades'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    grade = Column(Integer)
    date = Column(Date)

# Створення таблиць у базі даних
Base.metadata.create_all(engine)

# Заповнення бази даних даними
fake = Faker()

# Заповнення таблиці груп
groups = [Group(name=f'Group {i}') for i in range(1, 4)]
session.add_all(groups)
session.commit()

# Заповнення таблиці викладачів
teachers = [Teacher(name=fake.name()) for _ in range(3)]
session.add_all(teachers)
session.commit()

# Заповнення таблиці студентів та предметів
for _ in range(30):  # Кількість студентів
    student = Student(name=fake.name(), group_id=random.randint(1, 3))
    session.add(student)
    session.commit()

    for _ in range(random.randint(5, 8)):  # Кількість предметів
        subject = Subject(name=fake.word(), teacher_id=random.randint(1, 3))
        session.add(subject)
        session.commit()

        for student_id in range(1, 31):  # Кількість студентів
            grade = Grade(student_id=student_id, subject_id=subject.id, grade=random.randint(1, 10), date=datetime.now())
            session.add(grade)

session.commit()

# Виконання SQL-запитів
# query_1.sql: Знайти 5 студентів із найбільшим середнім балом з усіх предметів.
top_students = session.query(Student.name, func.avg(Grade.grade).label('average_grade')) \
                     .join(Grade) \
                     .group_by(Student.id) \
                     .order_by(func.avg(Grade.grade).desc()) \
                     .limit(5) \
                     .all()

# query_2.sql: Знайти середній бал у групах з певного предмета.
average_grade_by_group = session.query(Group.name, func.avg(Grade.grade).label('average_grade')) \
                                .join(Student) \
                                .join(Grade) \
                                .join(Subject) \
                                .filter(Subject.name == 'Your Subject') \
                                .group_by(Group.id) \
                                .all()

# Вивід результатів
print("Top 5 students with highest average grades:")
for student in top_students:
    print(student.name, student.average_grade)

print("\nAverage grades by group for a specific subject:")
for group in average_grade_by_group:
    print(group.name, group.average_grade)

# Закриття сесії з базою даних
session.close()
