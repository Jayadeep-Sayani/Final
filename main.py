import csv
import random
import pandas as pd

#hi !
#hello!
class CoursesRequest:
    def __init__(self):
        self.main_courses = []
        self.alternative_courses = []
        self.courses = []
        self.id = 0

    def add_course(self, course):
        if course.alternate == 'Y':
            self.alternative_courses.append(course)
        else:
            self.main_courses.append(course)
        
        self.courses.append(course)


    def get_course_requests(self):
        return self.main_courses
    
    def change_id(self, new_id):
        self.id = new_id

    def display_schedule(self):
        if not self.courses:
            print("No courses scheduled.")
        else:
            print("Scheduled courses:")
            for course in self.courses:
                print(f"{course.name}: {course.start_time} - {course.end_time}")

class Course:
    def __init__(self, name, course_id_, alt):
        self.name = name
        self.course_id = course_id_
        self.alternate = alt

# Define the Timetable class to manage schedules
class Timetable:
    def __init__(self):
        self.semester_1 = []
        self.semester_2 = []

    def add_course(self, course, semester):
        if semester == 1:
            if len(self.semester_1) < 4:
                self.semester_1.append(course)
            else:
                print("Cant add semester 1")
        elif semester == 2:
            if len(self.semester_2) < 4:
                self.semester_2.append(course)
            else:
                print("cant add sem 2")
        else:
            if len(self.semester_1) < 4:
                self.semester_1.append(course)
            elif len(self.semester_2) < 4:
                self.semester_2.append(course)



# Define the function to extract schedules
def extract_schedules():
    schedules = []
    schedule = CoursesRequest()
    with open('Cleaned Student Requests.csv', mode ='r') as file:
        csvFile = csv.reader(file)
        for lines in csvFile:
            if (len(lines) > 2):
                if lines[3] == '':       
                    schedules.append(schedule)
                    schedule = CoursesRequest()
                else:
                    course_to_add = Course(lines[3], lines[0], lines[11])
                    schedule.add_course(course_to_add)
            else:
                schedule.change_id(lines[1])

    return schedules


#----------------------------------------------------------------

def create_timetables(schedule_requests, sequencing):
    timetables = []
    fulfilled_requests = 0
    
    for schedule_request in schedule_requests:
        courses = schedule_request.get_course_requests()
        can_schedule = True
        timetable = Timetable()  # Create a new timetable for each schedule request
        
        # Check if courses form a pair in sequencing
        for seq_pair in sequencing:
            course_id_1, course_id_2 = seq_pair
            pair_found = False
            prereq = None
            subseq = None
            for course in courses:
                if (course.course_id == course_id_1):
                    prereq = course
                if (course.course_id == course_id_2):
                    subseq = course
            # e
            if prereq is not None and subseq is not None and prereq not in timetable.semester_1 and subseq not in timetable.semester_2:
                timetable.add_course(prereq, 1)
                timetable.add_course(subseq, 2)

        for course in courses:
            if course not in timetable.semester_1 and course not in timetable.semester_2:
                if len(timetable.semester_1) < 4:
                    timetable.add_course(course, 1)
                elif len(timetable.semester_2) < 4:
                    timetable.add_course(course, 2) 

        timetables.append(timetable)  # Add the completed timetable to the list

    return timetables, fulfilled_requests



def export_timetables_to_excel(timetables):
    data = {'S1A': [], 'S1B': [], 'S1C': [], 'S1D': [], 'S2A': [], 'S2B': [], 'S2C': [], 'S2D': []}

    for timetable in timetables:
        s1_courses = timetable.semester_1
        s2_courses = timetable.semester_2

        data['S1A'].append(s1_courses[0].name if len(s1_courses) > 0 else '')
        data['S1B'].append(s1_courses[1].name if len(s1_courses) > 1 else '')
        data['S1C'].append(s1_courses[2].name if len(s1_courses) > 2 else '')
        data['S1D'].append(s1_courses[3].name if len(s1_courses) > 3 else '')
        data['S2A'].append(s2_courses[0].name if len(s2_courses) > 0 else '')
        data['S2B'].append(s2_courses[1].name if len(s2_courses) > 1 else '')
        data['S2C'].append(s2_courses[2].name if len(s2_courses) > 2 else '')
        data['S2D'].append(s2_courses[3].name if len(s2_courses) > 3 else '')

    df = pd.DataFrame(data)
    df.to_excel('timetables.xlsx', index=False)


def extract_sequencing(file_path='Course Sequencing Rules.csv'):
    sequences = []

    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for line in csv_reader:
            if line[2].startswith("Sequence"):
                parts = line[2].split(" before ")
                parts[0] = parts[0].split(" ")[1]

                for part in parts:
                    prereq = parts[0]
                    for subseq in parts[1].split(", "):
                        sequences.append((prereq, subseq))
    return sequences

def extract_blockings(file_path='blockings.csv'):
    blockings = []

    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for line in csv_reader:
            blocking_rule = line[2].split(" in a ")[0][9:].split(", ")
            blockings.append(blocking_rule)
    
    return blockings


# Extract schedule requests from the data
all_schedule_requests = extract_schedules()
sequencing = extract_sequencing()
# blockings = extract_blockings()



# Create timetables and get stats
timetables, fulfilled_requests = create_timetables(all_schedule_requests, sequencing)

export_timetables_to_excel(timetables)

print(f"Total schedule requests: {len(all_schedule_requests)}")
print(f"Fulfilled schedule requests: {fulfilled_requests}")