"""Seed the database with fake data using the Faker library."""

from faker import Faker
from models import Student, Group, Teacher, Subject, Grade

from connect import session

faker = Faker()


def main():
    try:
        groups = [Group(name=f"Group {i}") for i in range(1, 4)]
        session.add_all(groups)
        session.commit()

        teachers = [Teacher(name=faker.name()) for _ in range(5)]
        session.add_all(teachers)
        session.commit()

        subjects = [
            Subject(
                name=f"Subject {faker.word()}",
                teacher_id=(faker.random.choice(teachers).id if i >= len(teachers) else i),
            )
            for i in range(1, 9)
        ]
        session.add_all(subjects)
        session.commit()

        students = [
            Student(
                name=faker.name(),
                group_id=faker.random.choice(groups).id,
            )
            for _ in range(50)
        ]
        session.add_all(students)
        session.commit()

        grades = [
            Grade(
                student_id=faker.random.choice(students).id,
                subject_id=faker.random.choice(subjects).id,
                grade=faker.random.randint(1, 5),
                date=faker.date_this_year(),
            )
            for _ in range(20 * len(students))
        ]
        session.add_all(grades)
        session.commit()
    except Exception as e:
        session.rollback()
        print("An error occurred while seeding the database:", e)


if __name__ == "__main__":
    main()
