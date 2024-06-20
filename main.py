import csv
import pandas as pd
import pyomo.environ as pyo
from pyomo.opt import SolverFactory

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

def create_timetables_mixed(schedule_requests, sequencing, index=0, timetables=None):
    model = pyo.ConcreteModel()
    
    # Sets
    model.C = pyo.Set(initialize=range(len(schedule_requests)))  # Set of students
    model.S = pyo.Set(initialize=[1, 2])  # Set of semesters
    model.K = pyo.Set(initialize=range(4))  # Set of course slots per semester

    # Parameters
    model.requests = pyo.Param(model.C, initialize={i: len(req.main_courses) for i, req in enumerate(schedule_requests)}, within=pyo.NonNegativeIntegers)
    
    # Variables
    model.x = pyo.Var(model.C, model.S, model.K, domain=pyo.Binary)  # Binary variables to decide if a course is in a particular slot
    
    # Constraints
    def request_satisfaction_rule(model, c):
        return sum(model.x[c, s, k] for s in model.S for k in model.K) <= model.requests[c]
    model.request_satisfaction = pyo.Constraint(model.C, rule=request_satisfaction_rule)

    def unique_slot_rule(model, c, s, k):
        return sum(model.x[c, s, k] for s in model.S for k in model.K) <= 1
    model.unique_slot = pyo.Constraint(model.C, model.S, model.K, rule=unique_slot_rule)

    # Objective
    def objective_rule(model):
        return sum(model.x[c, s, k] for c in model.C for s in model.S for k in model.K)
    model.objective = pyo.Objective(rule=objective_rule, sense=pyo.maximize)

    # Solve
    solver = pyo.SolverFactory('glpk')
    results = solver.solve(model, tee=True)

    # Extract timetables
    if timetables is None:
        timetables = [Timetable() for _ in schedule_requests]
    
    for c in model.C:
        for s in model.S:
            for k in model.K:
                if pyo.value(model.x[c, s, k]) > 0.5:
                    course = schedule_requests[c].main_courses[k]
                    timetables[c].add_course(course, s)
    
    return timetables

def num_fulfilled_requests(all_schedule_requests, timetable):
    num_fulfilled = 0
    print(len(all_schedule_requests) * 8)
    for i in range(len(all_schedule_requests)):
        for course in all_schedule_requests[i].main_courses:
            if course in timetable[i].semester_1 or timetable[i].semester_2:
                num_fulfilled += 1
            else:
                print (i + " not given " + course)

    return num_fulfilled


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
    with open(file_path, mode='r', encoding='utf-8') as file:
        simulataneous_blocking = []
        nonsimulataneous_blocking = []
        term_blocking = [] 

        csv_reader = csv.reader(file)
        for line in csv_reader:
            print(line)

        return 1, 2, 3

class course_scheduler:
    def __init__(self, blocks, classes):
        self.blocks = blocks
        self.classes = classes
        self.model = None
        self.schedule = None

def create_model(self):
    model = pyo.ConcreteModel()

    #data sets
    model.sBlocks = pyo.Set(initialize = self.Blocks, ordered = True)
    model.sClasses = pyo.Set(initialize = self.classes)



# Main 
#----------------------------

# Extracts data
all_schedule_requests = extract_schedules()
sequencing = extract_sequencing()
simulataneous_blockings, nonsimulataneous_blocking, term_blocking = extract_blockings()

# Create timetables and get stats
timetables = create_timetables_mixed(all_schedule_requests, sequencing)
fulfilled_requests = num_fulfilled_requests(all_schedule_requests, timetables)



export_timetables_to_excel(timetables)

# Prints the stats
print(f"Total schedule requests: {len(all_schedule_requests)}")
print(f"Fulfilled schedule requests: {fulfilled_requests}")
