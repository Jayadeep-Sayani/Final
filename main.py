import csv
import pandas as pd

def extract_max_enrollment():

    # Initialize an empty list to store the course ID and max enrollment pairs
    course_enrollment = []

    # Read the CSV file
    with open('data/Course Information.csv', mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row[0] != '' and row[9] != '':
                course_id = row[0]
                max_enrollment = row[9]
                course_enrollment.append((course_id, max_enrollment))
    return course_enrollment

max_enrollments = []

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

    # Returns the course requests in a schedule request
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
    def __init__(self, name, course_id_, alt, outside, linear):
        self.name = name
        self.outside = outside
        self.course_id = course_id_
        self.alternate = alt
        self.linear = linear  # New attribute to indicate if the course is linear

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
                print("Can't add to semester 1")
        elif semester == 2:
            if len(self.semester_2) < 4:
                self.semester_2.append(course)
            else:
                print("Can't add to semester 2")
        elif semester == 5:
            self.outsides.append(course)
        elif course.linear:
            if len(self.semester_1) < 4 and len(self.semester_2) < 4:
                self.semester_1.append(course)
                self.semester_2.append(course)
            else:
                print("Can't add linear course to both semesters")
        else:
            if len(self.semester_1) < 4:
                self.semester_1.append(course)
            elif len(self.semester_2) < 4:
                self.semester_2.append(course)

# Extract schedules from csv file
def extract_schedules(file_path='data/Cleaned Student Requests.csv'):
    schedules = []
    schedule = CoursesRequest()
    with open(file_path, mode='r') as file:
        csvFile = csv.reader(file)
        for lines in csvFile:
            if (len(lines) > 2):
                if lines[3] == '':       
                    schedules.append(schedule)
                    schedule = CoursesRequest()
                else:
                    linear = "linear" in lines[3].lower()
                    course_to_add = Course(lines[3], lines[0], lines[11], lines[0] in outside_timetables, linear)
                    schedule.add_course(course_to_add)
            else:
                schedule.change_id(lines[1])

    return schedules

def create_timetables_recursive(schedule_requests, sequencing, index=0, timetables=None):
    if timetables is None:
        timetables = []
    
    # Base case: If all schedule requests are processed
    if index >= len(schedule_requests):
        return timetables

    schedule_request = schedule_requests[index]
    courses = schedule_request.get_course_requests()
    timetable = Timetable()  # Create a new timetable for each schedule request
    
    for out in schedule_request.outsides:
        timetable.add_course(out, 5)
    
    def add_course_to_timetable(course, semester):
        if course not in timetable.semester_1 and course not in timetable.semester_2:
            timetable.add_course(course, semester)

    # Recursive case: Process each course in the schedule request
    def process_courses(courses, sequencing):
        if not courses:
            return
        course = courses[0]
        remaining_courses = courses[1:]
        
        for seq_pair in sequencing:
            course_id_1, course_id_2 = seq_pair
            prereq = None
            subseq = None

            # Finds the prereq and subseq
            for c in courses:
                if c.course_id == course_id_1:
                    prereq = c
                if c.course_id == course_id_2:
                    subseq = c
            
            # Adds the prerequisite to semester 1 and subsequent to semester 2
            if prereq is not None and subseq is not None and prereq not in timetable.semester_1 and subseq not in timetable.semester_2:
                timetable.add_course(prereq, 1)
                timetable.add_course(subseq, 2)

        if course.linear and course not in timetable.semester_1 and course not in timetable.semester_2 and len(timetable.semester_1) < 4 and len(timetable.semester_2) < 4:
            timetable.add_course(course, 1)
            timetable.add_course(course, 2)
        else:
            if course not in timetable.semester_1 and len(timetable.semester_1) < 4:
                add_course_to_timetable(course, 1)
            elif course not in timetable.semester_2 and len(timetable.semester_2) < 4:
                add_course_to_timetable(course, 2)

        process_courses(remaining_courses, sequencing)
    
    process_courses(courses, sequencing)
    timetables.append(timetable)

    return create_timetables_recursive(schedule_requests, sequencing, index + 1, timetables)


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
def extract_sequencing(file_path='data/Course Sequencing Rules.csv'):
    sequences = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file_path)
        for line in csv_reader:
            if len(line) >= 3:
                if line[2].startswith("Sequence"):
                    parts = line[2].split(" before ")
                    parts[0] = parts[0].split(" ")[1]
                    for part in parts:
                        prereq = parts[0]
                        for subseq in parts[1].split(", "):
                            sequences.append((prereq, subseq))       
    return sequences


def extract_blockings(file_path='data/Course Blocking Rules.csv'):
    with open(file_path, mode='r', encoding='utf-8'):
        simulataneous_blocking = []
        nonsimulataneous_blocking = []
        term_blocking = [] 

        csv_reader = csv.reader(file_path)
        for line in csv_reader:
            print(line)

        return 1, 2, 3

# Main 
#----------------------------

# Extracts data
all_schedule_requests = extract_schedules()
sequencing = extract_sequencing()
simulataneous_blockings, nonsimulataneous_blocking, term_blocking = extract_blockings()

# Create timetables and get stats
timetables = create_timetables_recursive(all_schedule_requests, sequencing)

export_timetables_to_excel(timetables)

# Prints the stats
print(f"Total schedule requests: {len(all_schedule_requests)}")
print(f"Fulfilled schedule requests: {fulfilled_requests}")

# testraph