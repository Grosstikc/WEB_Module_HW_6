from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Group, Student, Teacher, Subject, Grade
from faker import Faker
import random

def populate_db(session):
    faker = Faker()

    # Створення груп
    for _ in range(3):
        group = Group(name=f"Group {faker.word()}")
        session.add(group)

    # Створення викладачів
    teachers = [Teacher(name=faker.name()) for _ in range(3)]
    session.add_all(teachers)

    session.commit()  # Зберегти викладачів

    # Створення предметів
    subjects = [Subject(name=faker.word(), teacher=random.choice(teachers)) for _ in range(8)]
    session.add_all(subjects)

    # Створення студентів
    for _ in range(50):
        student = Student(name=faker.name(), group=random.choice(group))
        session.add(student)

    session.commit()  # Зберегти студентів і предмети

    # Додавання оцінок
    students = session.query(Student).all()
    for student in students:
        for _ in range(random.randint(5, 20)):  # кількість оцінок для кожного студента
            grade = Grade(value=random.randint(1, 5), student=student, subject=random.choice(subjects), date=faker.date_this_year())
            session.add(grade)

    session.commit()

if __name__ == '__main__':
    engine_url = 'postgresql://postgres:postgres@localhost:5432/mydatabase'
    engine = create_engine(engine_url)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    populate_db(session)
    session.close()
