from sqlalchemy import create_engine, func, desc
from sqlalchemy.orm import sessionmaker

from models import Student, Group, Subject, Teacher, Grade
from db_config import DATABASE_URL

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def select_1():
    """Find 5 students with the highest average grade across all subjects."""
    result = (
        session.query(Student.name, func.avg(Grade.grade).label("avg_grade"))
        .join(Grade)
        .group_by(Student.id, Student.name)
        .order_by(desc("avg_grade"))
        .limit(5)
        .all()
    )
    return result

def select_2(subject_name):
    """Find the student with the highest average grade in a specific subject.
    
    Args:
        subject_name: Name of the subject
        
    Returns:
        Tuple with student name and average grade
    """
    result = (
        session.query(Student.name, func.avg(Grade.grade).label("avg_grade"))
        .join(Grade)
        .join(Subject)
        .filter(Subject.name == subject_name)
        .group_by(Student.id, Student.name)
        .order_by(desc("avg_grade"))
        .first()
    )
    return result

def select_3(subject_name):
    """Find the average grade in groups for a specific subject.
    
    Args:
        subject_name: Name of the subject
        
    Returns:
        List of tuples with group name and average grade
    """
    result = (
        session.query(Group.name, func.avg(Grade.grade).label("avg_grade"))
        .join(Student)
        .join(Grade)
        .join(Subject)
        .filter(Subject.name == subject_name)
        .group_by(Group.id, Group.name)
        .all()
    )
    return result

def select_4():
    """Find the average grade across all grades in the database."""
    result = session.query(func.avg(Grade.grade).label("avg_grade")).scalar()
    return result

def select_5(teacher_name):
    """Find the subjects taught by a specific teacher.
    
    Args:
        teacher_name: Full name of the teacher
        
    Returns:
        List of subject names
    """
    result = (
        session.query(Subject.name)
        .join(Teacher)
        .filter(Teacher.name == teacher_name)
        .all()
    )
    return [row[0] for row in result]

def select_6(group_name):
    """Find the list of students in a specific group.
    
    Args:
        group_name: Name of the student group
        
    Returns:
        List of student names
    """
    result = (
        session.query(Student.name)
        .join(Group)
        .filter(Group.name == group_name)
        .all()
    )
    return [row[0] for row in result]

def select_7(group_name, subject_name):
    """Find the grades of students in a specific group for a specific subject.
    
    Args:
        group_name: Name of the student group
        subject_name: Name of the subject
        
    Returns:
        List of tuples with student name and grade
    """
    result = (
        session.query(Student.name, Grade.grade)
        .join(Grade)
        .join(Subject)
        .join(Group)
        .filter(Group.name == group_name, Subject.name == subject_name)
        .all()
    )
    return result

def select_8(teacher_name):
    """Find the average grade given by a specific teacher for their subjects.
    
    Args:
        teacher_name: Full name of the teacher
        
    Returns:
        Average grade as float
    """
    result = (
        session.query(func.avg(Grade.grade).label("avg_grade"))
        .join(Subject)
        .join(Teacher)
        .filter(Teacher.name == teacher_name)
        .scalar()
    )
    return result

def select_9(student_name):
    """Find the list of subjects attended by a specific student.
    
    Args:
        student_name: Full name of the student
        
    Returns:
        List of subject names
    """
    result = (
        session.query(Subject.name)
        .join(Grade)
        .join(Student)
        .filter(Student.name == student_name)
        .distinct()
        .all()
    )
    return [row[0] for row in result]

def select_10(student_name, teacher_name):
    """Find the list of subjects that a specific teacher teaches to a specific student.
    
    Args:
        student_name: Full name of the student
        teacher_name: Full name of the teacher
        
    Returns:
        List of subject names
    """
    result = (
        session.query(Subject.name)
        .join(Grade)
        .join(Student)
        .join(Teacher)
        .filter(Student.name == student_name, Teacher.name == teacher_name)
        .distinct()
        .all()
    )
    return [row[0] for row in result]

def select_11(teacher_name, student_name):
    """Find the average grade that a specific teacher gives to a specific student.
    
    Args:
        teacher_name: Full name of the teacher
        student_name: Full name of the student
        
    Returns:
        Average grade as float
    """
    result = (
        session.query(func.avg(Grade.grade).label("avg_grade"))
        .join(Subject)
        .join(Teacher)
        .join(Student)
        .filter(Teacher.name == teacher_name, Student.name == student_name)
        .scalar()
    )
    return result

def select_12(group_name, subject_name):
    """Find the grades of students in a specific group for a specific subject on the last lesson.
    
    Args:
        group_name: Name of the student group
        subject_name: Name of the subject
        
    Returns:
        List of tuples with student name and grade from the most recent lesson
    """
    latest_date = (
        session.query(func.max(Grade.date_received))
        .join(Student)
        .join(Group)
        .join(Subject)
        .filter(Group.name == group_name, Subject.name == subject_name)
        .scalar()
    )

    result = (
        session.query(Student.name, Grade.grade)
        .join(Grade)
        .join(Subject)
        .join(Group)
        .filter(
            Group.name == group_name,
            Subject.name == subject_name,
            Grade.date_received == latest_date
        )
        .all()
    )
    return result


def print_query_results():
    """Print results for all queries with example parameters"""
    teacher = session.query(Teacher).first()
    if teacher:
        teacher_name = teacher.name
    else:
        teacher_name = "John Doe"
        
    student = session.query(Student).first()
    if student:
        student_name = student.name
    else:
        student_name = "Jane Doe"
        
    subject = session.query(Subject).first()
    if subject:
        subject_name = subject.name
    else:
        subject_name = "Math Studies"
        
    group = session.query(Group).first()
    if group:
        group_name = group.name
    else:
        group_name = "Group-1"
    
    print("\n===== QUERY RESULTS =====\n")
    print("Query 1: Top 5 students by average grade")
    print(select_1())
    
    print(f"\nQuery 2: Best student in {subject_name}")
    print(select_2(subject_name))
    
    print(f"\nQuery 3: Average grades by group in {subject_name}")
    print(select_3(subject_name))
    
    print("\nQuery 4: Overall average grade")
    print(select_4())
    
    print(f"\nQuery 5: Subjects taught by {teacher_name}")
    print(select_5(teacher_name))
    
    print(f"\nQuery 6: Students in {group_name}")
    print(select_6(group_name))
    
    print(f"\nQuery 7: Grades in {group_name} for {subject_name}")
    print(select_7(group_name, subject_name))
    
    print(f"\nQuery 8: Average grade given by {teacher_name}")
    print(select_8(teacher_name))
    
    print(f"\nQuery 9: Subjects taken by {student_name}")
    print(select_9(student_name))
    
    print(f"\nQuery 10: Subjects that {teacher_name} teaches to {student_name}")
    print(select_10(student_name, teacher_name))
    
    print(f"\nQuery 11: Average grade that {teacher_name} gives to {student_name}")
    print(select_11(teacher_name, student_name))
    
    print(f"\nQuery 12: Latest grades in {group_name} for {subject_name}")
    print(select_12(group_name, subject_name))


if __name__ == "__main__":
    print_query_results()
