import csv
import pandas as pd
import random
from itertools import combinations
import math
from multiprocessing import Pool

course_ids = {}
memoized_scores = {}
visited_states = {}

outside_timetables = [
    'XC---09--L', 'MDNC-09C-L', 'MDNC-09M-L', 'XBA--09J-L', 'XLDCB09S-L', 'YCPA-0AX-L',
    'MDNCM10--L', 'YED--0BX-L', 'MMUCC10--L', 'YCPA-0AXE-', 'MMUOR10S-L', 'MDNC-10--L',
    'MIDS-0C---', 'MMUJB10--L', 'MDNC-11--L', 'YCPA-1AX-L', 'MDNCM11--L', 'YCPA-1AXE-',
    'MGRPR11--L', 'MGMT-12L--', 'YED--1EX-L', 'MWEX-2A--L', 'MCMCC11--L', 'MWEX-2B--L',
    'MIMJB11--L', 'MMUOR11S-L', 'MDNC-12--L', 'YCPA-2AX-L', 'MDNCM12--L', 'YCPA-2AXE-',
    'MGRPR12--L', 'MGMT-12L--', 'YED--2DX-L', 'YED--2FX-L', 'MCMCC12--L', 'MWEX-2A--L',
    'MIMJB12--L', 'MWEX-2B--L', 'MMUOR12S-', ''
]

unknown_courses = ['YESFL1AX--', 'MEFWR10---', 'XLEAD09---', 'MGE--11', 'MGE--12', 'MKOR-10---', 'MKOR-11---', 'MKOR-12---', 'MIT--12---', 'MSPLG11---', 'MJA--10---', 'MJA--11---', 'MJA--12---', 'MLTST10---', 'MLTST10--L']



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

    def add_course(self, course):
        if course.outside:
            self.requested_outsides.append(course)
        else:
            if course.alternate == 'Y':
                self.requested_alternative_courses.append(course)
            else:
                self.requested_main_courses.append(course)
        self.requested_courses.append(course)

    def get_course_requests(self):
        return self.requested_courses

    def change_id(self, new_id):
        self.id = new_id

    def add_to_finalized_schedule(self, course):
        self.finalized_schedule.append(course)

def extract_schedules(file_path='data/Cleaned Student Requests.csv'):
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
                        schedule.add_course(course_to_add)
                else:
                    schedule.change_id(lines[1])
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return schedules

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
    numcurr = 1000
    for schedule in schedule_requests:
        numcurr = numcurr + 1
        main_courses = schedule.requested_main_courses
        random.shuffle(main_courses)

        for course in schedule.requested_main_courses:
            if course.course_id not in course_ids.keys() and course.course_id != '':
                schedule.requested_main_courses.remove(course)

        schedule.finalized_schedule = [course.name for course in main_courses]

def generate_possible_master_timetables(master_timetable):
    possible_master_timetables = []

    for person_index, person_timetable in enumerate(master_timetable):
        for swap_combination in combinations(range(len(person_timetable)), 2):
            new_master_timetable = [row.copy() for row in master_timetable]
            new_master_timetable[person_index][swap_combination[0]], new_master_timetable[person_index][swap_combination[1]] = \
                new_master_timetable[person_index][swap_combination[1]], new_master_timetable[person_index][swap_combination[0]]

            key = tuple(tuple(row) for row in new_master_timetable)
            if key not in visited_states:
                possible_master_timetables.append(new_master_timetable)

    return possible_master_timetables

def score_master_timetable(master_timetable, sequencing_rules):
    key = tuple(tuple(row) for row in master_timetable)
    if key in memoized_scores:
        return memoized_scores[key]

    score = 0
    for person_schedule in master_timetable:
        first_half = person_schedule[:4]
        second_half = person_schedule[4:]

        for prereq, subseq in sequencing_rules:
            if prereq in course_ids.keys() and subseq in course_ids.keys():
                if course_ids[prereq] in first_half and course_ids[subseq] in second_half:
                    score += 10
                elif course_ids[prereq] in second_half and course_ids[subseq] in first_half:
                    score -= 10

    memoized_scores[key] = score
    return score

def update_visited_states(master_timetable, score):
    key = tuple(tuple(row) for row in master_timetable)
    visited_states[key] = score

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

def simulated_annealing(initial_timetable, sequencing_rules, initial_temp, cooling_rate):
    current_timetable = initial_timetable
    current_score = score_master_timetable(current_timetable, sequencing_rules)
    best_timetable = current_timetable
    best_score = current_score
    temperature = initial_temp

    while temperature > 1:
        new_timetable = generate_possible_master_timetables(current_timetable)[0]  # Get one new possible timetable
        new_score = score_master_timetable(new_timetable, sequencing_rules)

        if new_score > current_score or math.exp((new_score - current_score) / temperature) > random.random():
            current_timetable = new_timetable
            current_score = new_score

            if new_score > best_score:
                best_timetable = new_timetable
                best_score = new_score

        temperature *= cooling_rate

    return best_timetable, best_score

if __name__ == "__main__":
    with open("data/Course Information.csv", mode='r') as file:
        csv_reader = csv.reader(file)
        for line in csv_reader:
            if line[18] == 'Y' or line[18] == 'N':
                course_ids[line[0]] = line[2]

    schedule_requests = extract_schedules()
    sequencing = extract_sequencing()

    for schedule in schedule_requests:
        while len(schedule.requested_main_courses) < 8:
            schedule.requested_main_courses.append(Course("", "", False, False, False))

    create_timetables(schedule_requests)

    master_timetable = [schedule.finalized_schedule for schedule in schedule_requests]

    initial_temp = 10000
    cooling_rate = 0.99

    best_timetable, best_score = simulated_annealing(master_timetable, sequencing, initial_temp, cooling_rate)
    
    print(f"Best score: {best_score}")
    export_timetables_to_excel(best_timetable, 'timetables.xlsx')
