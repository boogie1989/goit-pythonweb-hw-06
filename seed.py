import random
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_config import DATABASE_URL
from models import Group, Student, Teacher, Subject, Grade


def create_db_session():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()


def seed_groups(session, num_groups=3):
    groups = [Group(name=f"Group-{i+1}") for i in range(num_groups)]
    session.add_all(groups)
    session.commit()
    return groups


def seed_teachers(session, num_teachers=5):
    fake = Faker()
    teachers = [Teacher(name=fake.name()) for _ in range(num_teachers)]
    session.add_all(teachers)
    session.commit()
    return teachers


def seed_subjects(session, teachers, min_subjects=5, max_subjects=8):
    fake = Faker()
    subjects = []
    for i in range(random.randint(min_subjects, max_subjects)):
        subject = Subject(
            name=fake.word().capitalize() + " Studies",
            teacher_id=random.choice(teachers).id,
        )
        subjects.append(subject)
    session.add_all(subjects)
    session.commit()
    return subjects


def seed_students(session, groups, min_students=30, max_students=50):
    fake = Faker()
    students = []
    for _ in range(random.randint(min_students, max_students)):
        student = Student(
            name=fake.name(),
            group_id=random.choice(groups).id,
        )
        students.append(student)
    session.add_all(students)
    session.commit()
    return students


def seed_grades(session, students, subjects, min_grades=10, max_grades=20):
    fake = Faker()
    for student in students:
        grades = []
        for _ in range(random.randint(min_grades, max_grades)):
            grade = Grade(
                student_id=student.id,
                subject_id=random.choice(subjects).id,
                grade=round(random.uniform(2.0, 5.0), 1),
                date_received=fake.date_time_between(
                    start_date=datetime(2024, 9, 1),
                    end_date=datetime(2025, 5, 3)
                ),
            )
            grades.append(grade)
        session.add_all(grades)
    session.commit()


def main():
    session = create_db_session()
    
    try:
        groups = seed_groups(session)
        teachers = seed_teachers(session)
        subjects = seed_subjects(session, teachers)
        students = seed_students(session, groups)
        seed_grades(session, students, subjects)
        
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main()