import csv
import numpy as np
import pandas as pd
import random
import copy


course_ids = {}

def export_timetables_to_excel(timetables, file_path):
    data = {'S1A': [], 'S1B': [], 'S1C': [], 'S1D': [], 'S2A': [], 'S2B': [], 'S2C': [], 'S2D': []}

    for timetable in timetables:
        data['S1A'].append(timetable[0] if len(timetable) > 0 else '')
        data['S1B'].append(timetable[1] if len(timetable) > 1 else '')
        data['S1C'].append(timetable[2] if len(timetable) > 2 else '')
        data['S1D'].append(timetable[3] if len(timetable) > 3 else '')
        data['S2A'].append(timetable[4] if len(timetable) > 4 else '')
        data['S2B'].append(timetable[5] if len(timetable) > 5 else '')
        data['S2C'].append(timetable[6] if len(timetable) > 6 else '')
        data['S2D'].append(timetable[7] if len(timetable) > 7 else '')

    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)


outside_timetables = [
    'XC---09--L', 'MDNC-09C-L', 'MDNC-09M-L', 'XBA--09J-L', 'XLDCB09S-L', 'YCPA-0AX-L',
    'MDNCM10--L', 'YED--0BX-L', 'MMUCC10--L', 'YCPA-0AXE-', 'MMUOR10S-L', 'MDNC-10--L',
    'MIDS-0C---', 'MMUJB10--L', 'MDNC-11--L', 'YCPA-1AX-L', 'MDNCM11--L', 'YCPA-1AXE-',
    'MGRPR11--L', 'MGMT-12L--', 'YED--1EX-L', 'MWEX-2A--L', 'MCMCC11--L', 'MWEX-2B--L',
    'MIMJB11--L', 'MMUOR11S-L', 'MDNC-12--L', 'YCPA-2AX-L', 'MDNCM12--L', 'YCPA-2AXE-',
    'MGRPR12--L', 'MGMT-12L--', 'YED--2DX-L', 'YED--2FX-L', 'MCMCC12--L', 'MWEX-2A--L',
    'MIMJB12--L', 'MWEX-2B--L', 'MMUOR12S-', ''
]

unknown_courses = ['ADST -  DRAFTING 10', 'ADST -  FOOD STUDIES 10', 'ADST - ENTREPRENEURSHIP AND MARKETING 10', 'ADST - MEDIA DESIGN 10', 'ADST -  WOODWORK 10', 'ADST -  POWER TECHNOLOGY 10']


class Course:
    def __init__(self, name, course_id_, alt, outside, linear):
        self.name = name
        self.course_id = course_id_
        self.alternate = alt
        self.outside = outside
        self.linear = linear

class Person:
    def __init__(self):
        self.requested_main_courses = []
        self.requested_alternative_courses = []
        self.requested_courses = []
        self.requested_outsides = []
        self.finalized_schedule = ["", "", "", "", "", "", "", ""]

    def add_course(self, course, nonalternate_courses_requested, alternate_courses_requested):
        if course.outside:
            self.requested_outsides.append(course)
        else:
            if course.alternate == 'Y':
                self.requested_alternative_courses.append(course)
                nonalternate_courses_requested += 1
            else:
                self.requested_main_courses.append(course)
                alternate_courses_requested += 1
        self.requested_courses.append(course)
        return nonalternate_courses_requested, alternate_courses_requested

    def get_course_requests(self):
        return self.requested_courses

def extract_schedules(file_path='data/Cleaned Student Requests.csv'):
    nonalternate_courses_requested = 0
    alternate_courses_requested = 0
    schedules = []
    schedule = Person()
    try:
        with open(file_path, mode='r') as file:
            csvFile = csv.reader(file)
            for lines in csvFile:
                if len(lines) > 2:
                    if lines[3] == '':
                        schedules.append(schedule)
                        schedule = Person()
                    else:
                        linear = "linear" in lines[3].lower()
                        course_to_add = Course(lines[3], lines[0], lines[11], lines[0] in outside_timetables, linear)
                        nonalternate_courses_requested, alternate_courses_requested = schedule.add_course(course_to_add, nonalternate_courses_requested, alternate_courses_requested)
                
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return schedules, nonalternate_courses_requested, alternate_courses_requested

def extract_sequencing(file_path='data/Course Sequencing Rules.csv'):
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

def create_timetables(schedule_requests):
    for schedule in schedule_requests:
        main_courses = schedule.requested_main_courses
        random.shuffle(main_courses)
        for main_course in main_courses:
            schedule.finalized_schedule.append(main_course.name)
 
           


def extract_max_sections(file_path='data/Course Information.csv'):
    sections = {}

    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        
        for line in csv_reader:
            if len(line[13]) == 1:
                sections[line[2]] = (int)(line[13])

    return sections

def extract_maxEnrollment(file_path='data/Course Information.csv'):
    maxEnrollment = {}

    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)

        for line in csv_reader:
            if len(line[13]) == 1:
                maxEnrollment[line[2]] = (int)(line[9])

    return maxEnrollment
def generate_initial_population(schedule_requests, population_size):
    population = []
    for _ in range(population_size):
        create_timetables(schedule_requests)
        master_timetable = [schedule.finalized_schedule for schedule in schedule_requests]
        master_timetable.pop(0)
        population.append(copy.deepcopy(master_timetable))
    return population

def extract_blockings(file_path='data/Course Blocking Rules.csv'):
    blockings = {}

    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)

        for line in csv_reader:
            column = line[2]
            arr = column[9:].split(", ")
            #print(column[9:])
            if column.startswith("Schedule"):
                for i in range(len(arr)):
                    list = []
                    for j in range(len(arr)):
                        if i != j:
                            list.append(arr[j][:10])
                    list.append(column.split("in a ")[1])
                    blockings[arr[i][:10]] = list
    return blockings


max_enrollments = extract_max_sections()

def is_valid_timetable(schedule, sequencing_rules, max_enrollments, blockings):
    for i in range(schedule):
        if schedule[i].size > max_enrollments[i]:
            return False

        



