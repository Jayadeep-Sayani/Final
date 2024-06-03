

import csv
import random
import pandas as pd


outside_timetables = [
        'XC---09--L', 'MDNC-09C-L', 'MDNC-09M-L', 'XBA--09J-L', 'XLDCB09S-L', 'YCPA-0AX-L',
        'MDNCM10--L', 'YED--0BX-L', 'MMUCC10--L', 'YCPA-0AXE-', 'MMUOR10S-L', 'MDNC-10--L',
        'MIDS-0C---', 'MMUJB10--L', 'MDNC-11--L', 'YCPA-1AX-L', 'MDNCM11--L', 'YCPA-1AXE-',
        'MGRPR11--L', 'MGMT-12L--', 'YED--1EX-L', 'MWEX-2A--L', 'MCMCC11--L', 'MWEX-2B--L',
        'MIMJB11--L', 'MMUOR11S-L', 'MDNC-12--L', 'YCPA-2AX-L', 'MDNCM12--L', 'YCPA-2AXE-',
        'MGRPR12--L', 'MGMT-12L--', 'YED--2DX-L', 'YED--2FX-L', 'MCMCC12--L', 'MWEX-2A--L',
        'MIMJB12--L', 'MWEX-2B--L', 'MMUOR12S-', ''
    ]

# CourseRequest class
class CoursesRequest:

    # Constructor
    def __init__(self):
        self.main_courses = []
        self.alternative_courses = []
        self.courses = []
        self.outsides = []
        self.id = 0

    # Adds course to the Timetable Request
    def add_course(self, course):
        if course.outside:
            self.outsides.append(course)
        else:
            if course.alternate == 'Y':
                self.alternative_courses.append(course)
            else:
                self.main_courses.append(course)
        
        self.courses.append(course)

    # Returns the course requests in a scheudle request
    def get_course_requests(self):
        return self.main_courses
    
    # Sets the UID
    def change_id(self, new_id):
        self.id = new_id

    # Displays the schedule in the terminal
    def display_schedule(self):
        if not self.courses:
            print("No courses scheduled.")
        else:
            print("Scheduled courses:")
            for course in self.courses:
                print(f"{course.name}: {course.start_time} - {course.end_time}")

# Course class
class Course:

    # Constructor
    def __init__(self, name, course_id_, alt, outside):
        self.name = name
        self.outside = outside
        self.course_id = course_id_
        self.alternate = alt


# Timetable class - Timetable created based on a person's request
class Timetable:

    # Constructor
    def __init__(self):
        self.semester_1 = []
        self.semester_2 = []
        self.outsides = []

    # Adds course to a specified semester
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
        elif semester == 5:
            self.outsides.append(course)
        else:
            if len(self.semester_1) < 4:
                self.semester_1.append(course)
            elif len(self.semester_2) < 4:
                self.semester_2.append(course)



# Extract schedules from csv file
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
                    course_to_add = Course(lines[3], lines[0], lines[11], lines[0] in outside_timetables)
                    schedule.add_course(course_to_add)
            else:
                schedule.change_id(lines[1])

    return schedules


#---------------------------------------------------------------

def create_timetables(schedule_requests):
    for schedule in schedule_requests:
        main_courses = schedule.main_courses
        random.shuffle(main_courses)
        schedule.finalized_schedule = [course.name for course in main_courses]


def create_real_master_timetable(timetables, max_enrolement):
    data = [{}, {}, {}, {}, {}, {}, {}, {}]

    for i in range(len(data)):
        for timetable in timetables:
            courses = timetable

            if i < len(courses):
                if courses[i] in data[i] and courses[i] in max_enrolement:
                    if data[i][courses[i]][-1] == max_enrolement[courses[i]]:
                        data[i][courses[i]].append(1)
                    else:
                        data[i][courses[i]][-1] += 1
                else:
                    data[i][courses[i]] = []
                    data[i][courses[i]].append(1)
    data2 = {'S1A': [], 'S1B': [], 'S1C': [], 'S1D': [], 'S2A': [], 'S2B': [], 'S2C': [], 'S2D': []}

    for original, copy in zip(data, data2):
        for key in original:
            for int in original[key]:
                data2[copy].append(key + ": " + str(int))
    
    df = pd.DataFrame.from_dict(data2, orient='index')
    df = df.transpose()
    df.to_excel('mastertimetable.xlsx', index=False)

# Exports the master timetable to an excel file
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


# Gets sequencing rules from csv file
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

# Gets blocking rules from csv file
def extract_blockings(file_path='Course Blocking Rules.csv'):
    blockings = []

    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for line in csv_reader:
            blocking_rule = line[2].split(" in a ")[0][9:].split(", ")
            if len(blocking_rule) != 1 and blocking_rule[0] != '':
                blockings.append(blocking_rule)
    #print(blockings)
    return blockings

def extract_maxEnrollment(file_path='Course Information.csv'):
    maxEnrollment = {}

    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        
        for line in csv_reader:
            if line[18] == "Y" or line[18] == "N":
                maxEnrollment[line[2]] = (int)(line[9])

    return maxEnrollment

# Main 
#----------------------------

# Extracts data
all_schedule_requests = extract_schedules()
sequencing = extract_sequencing()
blockings = extract_blockings()
maxEnrollment = extract_maxEnrollment()
print(maxEnrollment)
for schedule in all_schedule_requests:
        while len(schedule.main_courses) < 8:
            schedule.main_courses.append(Course("", "", False, False))


create_timetables(all_schedule_requests)

"""# Print the percentage of people who got all 8 requested main courses
print(f"Percentage of people who got all 8 requested main courses: {eight:.1f}%")
print(f"Percentage of people who got 7-8 requested main courses: {seven_or_eight:.1f}%")
print(f"Percentage of main courses given: {mainper:.1f}%")
"""
timetables = []
for schedule in all_schedule_requests:
    timetables.append(schedule.finalized_schedule)
create_real_master_timetable(timetables, maxEnrollment)