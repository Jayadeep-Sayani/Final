import csv
import numpy as np
import pandas as pd
import random
from itertools import combinations

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
        self.finalized_schedule = ["", "", "", "", "", "", "", ""]  # New attribute

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


# Gets sequencing rules from csv file
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

def extract_sections(file_path='data/Course Information.csv'):
    sections = {}

    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        
        for line in csv_reader:
            if line[18] == "Y" or line[18] == "N":
                sections[line[1]] = (int)(line[14])

    #print(sections)

    return sections

def extract_maxEnrollment(file_path='data/Course Information.csv'):
    maxEnrollment = {}

    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        
        for line in csv_reader:
            if line[18] == "Y" or line[18] == "N":
                maxEnrollment[line[1]] = (int)(line[9])

    #print(maxEnrollment)

    return maxEnrollment

def extract_blockings(file_path='data/Course Information.csv'):
    blockings = {}

    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        
        for line in csv_reader:
            if line[2].startswith("Schedule"):
                blockings[line[2].split(",")[0].str[9:]] = line[2].split(", ")[1].str[:10]

    print(blockings)

    return blockings

def create_timetables(schedule_requests, sequencing):
    numcurr = 1000
    for schedule in schedule_requests:
        
        numcurr = numcurr + 1
        # Get the requested main courses for this person
        main_courses = schedule.requested_main_courses
        # Shuffle the main courses randomly
        random.shuffle(main_courses)

        for course in schedule.requested_main_courses:
            if course.course_id not in course_ids.keys() and course.course_id != '':
                schedule.requested_main_courses.remove(course)

        # Check if the schedule request has both a prerequisite and a subsequent
        for seq_pair in sequencing:
            course_id_1, course_id_2 = seq_pair
            prereq = None
            subseq = None

            # Finds the prereq and subseq
            for course in schedule.requested_main_courses:
                if course.course_id == course_id_1:
                    prereq = course
                if course.course_id == course_id_2:
                    subseq = course
            
            # Adds the prerequisite to semester 1 and subsequent to semester 2
            if prereq is not None and subseq is not None and prereq not in schedule.finalized_schedule[:4] and subseq not in schedule.finalized_schedule[4:]:
                for course in schedule.finalized_schedule[:4]:
                    if course is "":
                        course = prereq
                for course in schedule.finalized_schedule[4:]:
                    if course is "":
                        course = subseq

        # Check for linear course and add to both semesters
        for course in schedule.requested_main_courses:
            if course.linear and course not in schedule.finalized_schedule:
                for sem1course in schedule.finalized_schedule[:4]:
                    if sem1course is "":
                        sem1course = course
                for sem2course in schedule.finalized_schedule[4:]:
                    if sem2course is "":
                        sem2course = course
        
        # Add remaining courses
        for course in schedule.requested_main_courses:
            if course not in schedule.finalized_schedule:
                for course_space in schedule.finalized_schedule:
                    if course_space is "":
                        course_space = course

# Define a global variable to store visited states
visited_states = {}

def generate_possible_master_timetables(master_timetable):
    possible_master_timetables = []

    for person_index, person_timetable in enumerate(master_timetable):
        # Generate all possible swaps for this person's timetable
        for swap_combination in combinations(range(len(person_timetable)), 2):
            new_master_timetable = [row.copy() for row in master_timetable]
            new_master_timetable[person_index][swap_combination[0]], new_master_timetable[person_index][swap_combination[1]] = \
                new_master_timetable[person_index][swap_combination[1]], new_master_timetable[person_index][swap_combination[0]]

            key = tuple(tuple(row) for row in new_master_timetable)
            if key not in visited_states:
                possible_master_timetables.append(new_master_timetable)

    
    return possible_master_timetables


def score_master_timetable(master_timetable, sequencing_rules):
    score = 0

    # Check sequencing for each pair of courses in the master timetable
    for person_schedule in master_timetable:
        # Extract the first 4 and last 4 courses from the person's schedule
        first_half = person_schedule[:4]
        second_half = person_schedule[4:]

        # Check each sequencing rule
        for prereq, subseq in sequencing_rules:
            if prereq in course_ids.keys() and subseq in course_ids.keys():
                if course_ids[prereq] in first_half and course_ids[subseq] in second_half:
                    # Reward if the prerequisite is scheduled before the subsequent course
                    score += 10
                elif course_ids[prereq] in second_half and course_ids[subseq] in first_half:
                    score -= 10
        
        for course in person_schedule:
            if "linear" in course.lower():
                if (course in first_half and course not in second_half) or (course in second_half and course not in first_half):
                    score -= 20
                elif course in first_half and course in second_half:
                    score += 20
        

        # Initialize an empty dictionary to store the counts
        course_counts = count_strings_in_columns(master_timetable)

        

        print(course_counts)
    return score


def count_strings_in_columns(array):
    # Initialize an empty dictionary to store counts
    string_count = {}
    
    # Get the number of columns
    num_columns = len(array[0])
    
    # Iterate through each column
    for col_idx in range(num_columns):
        # Use a set to store unique strings in the current column
        unique_strings = set(row[col_idx] for row in array)
        
        # Update the dictionary with counts
        for string in unique_strings:
            if string in string_count:
                string_count[string] += 1
            else:
                string_count[string] = 1
    
    return string_count



def update_visited_states(master_timetable, score):
    key = tuple(tuple(row) for row in master_timetable)
    visited_states[key] = score

if __name__ == "__main__":
    
    with open("data/Course Information.csv", mode='r') as file:
        csv_reader = csv.reader(file)
        for line in csv_reader:
            if line[18] == 'Y' or line[18] == 'N':
                course_ids[line[0]] = line[2]    

    schedule_requests = extract_schedules()
    sequencing = extract_sequencing()
    sections = extract_sections()
    maxEnrollment = extract_maxEnrollment()

    for schedule in schedule_requests:
        while len(schedule.requested_main_courses) < 8:
            schedule.requested_main_courses.append(Course("", "", False, False, False))


    # Create timetables for each person
    create_timetables(schedule_requests)

    # Create master timetable
    master_timetable = []

    # Iterate over each person's schedule and append to master timetable
    for schedule in schedule_requests:
        master_timetable.append(schedule.finalized_schedule)
     

    currscore = score_master_timetable(master_timetable, sequencing)
    update_visited_states(master_timetable, currscore)

    print(currscore)

    newbest_score = currscore
    newbest_master_timetable = master_timetable

    while True:
        possible_master_timetables = generate_possible_master_timetables(newbest_master_timetable)
        same_score_master_timetables = []
        found_new_best = False
        for master_timetable in possible_master_timetables:
            score = score_master_timetable(master_timetable, sequencing)     
            if score > currscore:
                newbest_score = score
                newbest_master_timetable = master_timetable
                found_new_best = True
                break
            elif score == currscore:
                same_score_master_timetables.append(master_timetable)
                
        if found_new_best == False:
            newbest_master_timetable = random.choice(same_score_master_timetables)
            newbest_score = score_master_timetable(newbest_master_timetable, sequencing)

        print(newbest_score)

        # Update visited states with the new best timetable
        
        update_visited_states(newbest_master_timetable, newbest_score)

        export_timetables_to_excel(newbest_master_timetable, 'timetables.xlsx')



