from sqlalchemy import func, desc
from models import Student, Group, Subject, Grade
from connect import session
from argparse import ArgumentParser
from functools import wraps


def session_scope(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        finally:
            session.close()
        return result

    return wrapper


@session_scope
def select_1(limit=5):
    result = (
        session.query(Student.name, func.avg(Grade.grade).label("average"))
        .select_from(Student)
        .join(Grade)
        .group_by(Student.id)
        .order_by(desc("average"))
        .limit(limit)
        .all()
    )
    return result


@session_scope
def select_2(subject_id):
    result = (
        session.query(Student.name, func.avg(Grade.grade).label("average"))
        .select_from(Student)
        .join(Grade)
        .filter(Grade.subject_id == subject_id)
        .group_by(Student.id)
        .order_by(desc("average"))
        .first()
    )
    return result


@session_scope
def select_3(subject_id):
    result = (
        session.query(Group.name, func.avg(Grade.grade).label("average"))
        .join(Student, Student.group_id == Group.id)
        .join(Grade, Grade.student_id == Student.id)
        .filter(Grade.subject_id == subject_id)
        .group_by(Group.id)
        .all()
    )
    return result


@session_scope
def select_4():
    result = session.query(func.avg(Grade.grade)).scalar()
    return result


@session_scope
def select_5(teacher_id):
    result = session.query(Subject.name).filter(Subject.teacher_id == teacher_id).all()
    return result


@session_scope
def select_6(group_id):
    result = (
        session.query(Group.name, Student.name)
        .join(Group)
        .filter(Student.group_id == group_id)
        .all()
    )
    return result


@session_scope
def select_7(group_id, subject_id):
    result = (
        session.query(Student.name, Grade.grade, Group.name)
        .join(Grade)
        .join(Group)
        .filter(Student.group_id == group_id, Grade.subject_id == subject_id)
        .all()
    )
    return result


@session_scope
def select_8(teacher_id):
    result = (
        session.query(func.avg(Grade.grade).label("average"))
        .join(Subject)
        .filter(Subject.teacher_id == teacher_id)
        .scalar()
    )
    return result


@session_scope
def select_9(student_id):
    result = (
        session.query(Subject.name)
        .join(Grade)
        .filter(Grade.student_id == student_id)
        .distinct()
        .all()
    )
    return result


@session_scope
def select_10(student_id, teacher_id):
    result = (
        session.query(Subject.name)
        .join(Grade)
        .filter(Grade.student_id == student_id, Subject.teacher_id == teacher_id)
        .distinct()
        .all()
    )
    return result


def main():
    parser = ArgumentParser(description="Select from database")
    parser.add_argument("--student_id", type=str, required=False)
    parser.add_argument("--group_id", type=str, required=False)
    parser.add_argument("--teacher_id", type=str, required=False)
    parser.add_argument("--subject_id", type=str, required=False)

    args = parser.parse_args()
    student_id, group_id, teacher_id, subject_id = (
        args.student_id or 1,
        args.group_id or 1,
        args.teacher_id or 1,
        args.subject_id or 1,
    )

    print("Наступні дані будуть використані при вибирці з бази даних")
    print(
        f"\nStudent ID {student_id}, Group ID {group_id}, Teacher ID {teacher_id}, Subject ID {subject_id}"
    )

    print("\n1) Знайти 5 студентів із найбільшим середнім балом з усіх предметів:")
    best_students = select_1()
    for student, avg_grade in best_students:
        print(f"{student}: {avg_grade:.2f}")

    print("\n2) Знайти студента із найвищим середнім балом з певного предмета:")
    best_student = select_2(subject_id)
    if best_student:
        print(f"{best_student[0]}: {best_student[1]:.2f}")

    print("\n3) Знайти середній бал у групах з певного предмета:")
    group_grades = select_3(subject_id)
    for group, avg_grade in group_grades:
        print(f"{group}: {avg_grade:.2f}")

    print("\n4) Знайти середній бал на потоці (по всій таблиці оцінок):")
    avg_grade = select_4()
    if avg_grade:
        print(f"{avg_grade:.2f}")
    else:
        print("Не знайдено")

    print("\n5) Знайти які курси читає певний викладач:")
    courses = select_5(teacher_id)
    for course in courses:
        print(course[0])

    print("\n6) Знайти список студентів у певній групі:")
    students = select_6(group_id)
    for student in students:
        print(f"{student[0]} - {student[1]}")

    print("\n7) Знайти оцінки студентів у окремій групі з певного предмета:")
    grades = select_7(group_id, subject_id)
    for student, grade, group in grades:
        print(f"{group}, {student}: {grade}")

    print("\n8) Знайти середній бал, який ставить певний викладач зі своїх предметів:")
    teacher_avg = select_8(teacher_id)
    if teacher_avg:
        print(f"{teacher_avg:.2f}")
    else:
        print("Не знайдено")

    print("\n9) Знайти список курсів, які відвідує певний студент:")
    student_courses = select_9(student_id)
    for course in student_courses:
        print(course[0])

    print("\n10) Список курсів, які певному студенту читає певний викладач:")
    teacher_courses = select_10(student_id, teacher_id)
    for course in teacher_courses:
        print(course[0])


if __name__ == "__main__":
    main()
