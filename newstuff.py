
import csv

courses = []
people = []


class Course:

    prereqs = []
    simult_blocks = []
    nonsimulat_blocks = []
    
    def __init__(self, n, id, nt, em) -> None:
        self.course_name = n
        self.course_id = id
        self.num_terms = nt
        self.enrollment_max = em

class Student:
    
    main_courses = []
    alternate_courses = []

    def __init__(self, id) -> None:
        self.id = int(id)

def generate_data():
    generate_course_data(filepath="data/Course Information.csv")
    generate_student_requests(filepath="data/Cleaned Student Requests.csv")
    # generate_rules(pathone="data/Course Sequencing Rules", pathtwo="data/Course Blocking Rules")

def generate_course_data(filepath):
    course_data  = []

    with open(filepath, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for line in csv_reader:
            course_data.append(line)

        for course in course_data:
            course_name = course[1]
            course_id = course[0]
            course_num_terms = course[8]
            course_enrollment_max = course[7]

            course_class = Course(course_name, course_id, course_num_terms, course_enrollment_max)
            courses.append(course_class)


def generate_student_requests(filepath):
    student_data  = []

    with open(filepath, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for line in csv_reader:
            student_data.append(line)

        student_obj = None
        course = None
        for student in student_data:
            if student[0] == "ID":
                if student_obj is not None:
                    people.append(student_obj)
                student_obj = Student(student[1])
            else:
                course = get_course_data(student[0])
                if course is not None:
                    if student[3] == 'Y':
                        student_obj.alternate_courses.append(course)
                    elif student[3] == 'N':
                        student_obj.main_courses.append(course)

def generate_sequences()

def get_course_data(code):
    return next((c for c in courses if c.course_id == code), None)

generate_data()