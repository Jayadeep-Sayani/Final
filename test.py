import csv
from joblib import Parallel, delayed
import numpy as np
import pandas as pd
import random
import copy


course_ids = {}

def export_timetables_to_excel(timetables, file_path):
    data = {'S1A': [], 'S1B': [], 'S1C': [], 'S1D': [], 'S2A': [], 'S2B': [], 'S2C': [], 'S2D': []}

    for timetable in timetables:
        data['S1A'].append(timetable.finalized_schedule[0] if len(timetable.finalized_schedule) > 0 else '')
        data['S1B'].append(timetable.finalized_schedule[1] if len(timetable.finalized_schedule) > 1 else '')
        data['S1C'].append(timetable.finalized_schedule[2] if len(timetable.finalized_schedule) > 2 else '')
        data['S1D'].append(timetable.finalized_schedule[3] if len(timetable.finalized_schedule) > 3 else '')
        data['S2A'].append(timetable.finalized_schedule[4] if len(timetable.finalized_schedule) > 4 else '')
        data['S2B'].append(timetable.finalized_schedule[5] if len(timetable.finalized_schedule) > 5 else '')
        data['S2C'].append(timetable.finalized_schedule[6] if len(timetable.finalized_schedule) > 6 else '')
        data['S2D'].append(timetable.finalized_schedule[7] if len(timetable.finalized_schedule) > 7 else '')

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
            elif course.alternate == 'N':
                self.requested_main_courses.append(course)
        self.requested_courses.append(course)

    def get_course_requests(self):
        return self.requested_courses

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

def extract_sections(file_path='data/Course Information.csv'):
    sections = {}
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for line in csv_reader:
            if len(line[13]) == 1:
                sections[line[2]] = (int)(line[13])
    return sections

def create_timetables(schedule_requests):
    for schedule in schedule_requests:
        main_courses = schedule.requested_main_courses
        random.shuffle(main_courses)
        schedule.finalized_schedule = [course.name for course in main_courses]

def extract_maxEnrollment(file_path='data/Course Information.csv'):
    maxEnrollment = {}
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for line in csv_reader:
            if len(line[13]) == 1:
                if int(line[13]) != 0:
                    maxEnrollment[line[2]] = int(line[9]) / int(line[13])
                                                              
    return maxEnrollment

max_enrollments = extract_maxEnrollment()


def score_master_timetable(master_timetable, sequencing_rules):
    score = 0
    
    # Define time blocks
    time_blocks = ['S1A', 'S1B', 'S1C', 'S1D', 'S2A', 'S2B', 'S2C', 'S2D']
    
    # Initialize a dictionary to count enrollments in each time block
    timeblock_enrollment = {block: {} for block in time_blocks}


    for person_schedule in master_timetable:
        first_half = person_schedule[:4]
        second_half = person_schedule[4:]
        
        # Check sequencing rules
        for prereq, subseq in sequencing_rules:
            if prereq in course_ids.keys() and subseq in course_ids.keys():
                if course_ids[prereq] in first_half and course_ids[subseq] in second_half:
                    score += 10
                elif course_ids[prereq] in second_half and course_ids[subseq] in first_half:
                    score -= 10
        
        # Check linear courses
        for course in person_schedule:
            if "linear" in course.lower():
                if (course in first_half and course not in second_half) or (course in second_half and course not in first_half):
                    score -= 20
                elif course in first_half and course in second_half:
                    score += 20
        
        # Count enrollments in each time block
        for i, course in enumerate(person_schedule):
            if i < len(time_blocks):  # Ensure index does not exceed the length of time_blocks
                if course:
                    block = time_blocks[i]
                    if course not in timeblock_enrollment[block]:
                        timeblock_enrollment[block][course] = 0
                    timeblock_enrollment[block][course] += 1
        
    
    # Penalize schedules where time block enrollments do not meet the 50% threshold
    for block, courses in timeblock_enrollment.items():
        for course, count in courses.items():
            if course in max_enrollments:
                if count < 0.5 * max_enrollments[course] or count > max_enrollments[course]:
                    score -= 100
    
    return score

def count_strings_in_columns(array):
    string_count = {}
    max_cols = max(len(row) for row in array)
    for col in range(max_cols):
        unique_strings_in_column = set()
        for row in array:
            if col < len(row):
                unique_strings_in_column.add(row[col])
        for string in unique_strings_in_column:
            if string not in string_count:
                string_count[string] = 1
            else:
                string_count[string] += 1
    return string_count

def select_parents(population, scores, k=3):
    selected = []
    for _ in range(k):
        selected.append(random.choice(population))
    selected.sort(key=lambda x: scores[population.index(x)], reverse=True)
    return selected[0]

def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1)-1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

def mutate(schedule_requests, mutation_rate=0.1):
    for person in schedule_requests:
        # Perform mutation on main courses
        for i in range(len(person.finalized_schedule)):
            if random.random() < mutation_rate:
                if random.random() < 0.5:
                    swap_idx = random.randint(0, len(person.finalized_schedule)-1)
                    person.finalized_schedule[i], person.finalized_schedule[swap_idx] = person.finalized_schedule[swap_idx], person.finalized_schedule[i]
                else:
                    if len(person.requested_alternative_courses) > 0:
                        alt_swap_idx = random.randint(0, len(person.requested_alternative_courses)-1)
                        person.finalized_schedule[i], person.requested_alternative_courses[alt_swap_idx].name = person.requested_alternative_courses[alt_swap_idx].name, person.finalized_schedule[i]
                    else:
                        swap_idx = random.randint(0, len(person.finalized_schedule)-1)
                        person.finalized_schedule[i], person.finalized_schedule[swap_idx] = person.finalized_schedule[swap_idx], person.finalized_schedule[i]
    return schedule_requests


def genetic_algorithm(schedule_requests, sequencing_rules, population_size=120, generations=20, mutation_rate=0.3, elitism_size=5):
    population = generate_initial_population(schedule_requests, population_size)
    best_score = float('-inf')
    best_individual = None

    for generation in range(generations):
        print(f"Generation {generation}")
        scores = Parallel(n_jobs=-1)(delayed(score_master_timetable)([person.finalized_schedule for person in individual], sequencing_rules) for individual in population)
        best_generation_score = max(scores)
        best_generation_individual = population[scores.index(best_generation_score)]

        if best_generation_score > best_score:
            best_score = best_generation_score
            best_individual = best_generation_individual

        new_population = [best_generation_individual]

        while len(new_population) < population_size:
            parent1 = select_parents(population, scores)
            parent2 = select_parents(population, scores)
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)
            new_population.extend([child1, child2])

        population = new_population[:population_size]
    print(best_individual)
    return best_individual, best_score



def generate_initial_population(schedule_requests, population_size):
    population = []
    for _ in range(population_size):
        schedule_copy = copy.deepcopy(schedule_requests)
        create_timetables(schedule_copy)
        population.append(schedule_copy)
    return population

def create_real_master_timetable(timetables, max_enrolement):
    data = [{}, {}, {}, {}, {}, {}, {}, {}]

    for i in range(len(data)):
        for timetable in timetables:
            courses = timetable.finalized_schedule

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
                if key != '':
                    data2[copy].append(key + ": " + str(int))
                else:
                    data2[copy].append(key)
    
    df = pd.DataFrame.from_dict(data2, orient='index')
    df = df.transpose()
    df.to_excel('mastertimetable.xlsx', index=False)


def get_timetable_by_id(id, best_timetable):
    print(best_timetable[id - 1000])


if __name__ == "__main__":
    with open("data/Course Information.csv", mode='r') as file:
        csv_reader = csv.reader(file)
        for line in csv_reader:
            if len(line[13]) == 1:
                course_ids[line[0]] = line[2]

    schedule_requests = extract_schedules()

    sequencing = extract_sequencing()
    sections = extract_sections()

    for schedule in schedule_requests:
        while len(schedule.requested_main_courses) < 8:
            schedule.requested_main_courses.append(Course("", "", 'N', False, False))

    initial_population_size = 200
    generations = 70
    mutation_rate = 0.5
    elitism_size = 5

    best_timetable, best_score = genetic_algorithm(schedule_requests, sequencing, initial_population_size, generations, mutation_rate, elitism_size)
        
    total_main_requests = 0
    total_main_fulfill = 0

    total_eight_mains_people = 0
    total_eight_main_schedules = 0
    total_seven_eight_main_schedules = 0
    total_eight_main_or_alt_schedules = 0

    for schedule in best_timetable:
        for course in schedule.requested_main_courses:
            if course.name != '':
                total_main_requests += 1

        for course in schedule.finalized_schedule:
            if course in [course.name for course in schedule.requested_main_courses]:
                total_main_fulfill += 1

    for schedule in best_timetable:
        if len(schedule.requested_main_courses) == 8:
            total_eight_mains_people += 1

            requested_course_names = [course.name for course in schedule.requested_main_courses]
            print(requested_course_names)
            fulfilled_courses = sum(1 for course in schedule.finalized_schedule if course in requested_course_names)

            if fulfilled_courses == 8:
                total_eight_main_schedules += 1
            if 7 <= fulfilled_courses <= 8:
                total_seven_eight_main_schedules += 1

            # Check for main or alternate courses fulfillment
            requested_main_or_alt_names = requested_course_names + [course.name for course in schedule.requested_alternative_courses]
            print(requested_main_or_alt_names)
            fulfilled_main_or_alt_courses = sum(1 for course in schedule.finalized_schedule if course in requested_main_or_alt_names)

            if fulfilled_main_or_alt_courses == 8:
                total_eight_main_or_alt_schedules += 1

    print("Best Score:", best_score)
    print("Total Main Requests Placed: ", total_main_fulfill * 100 / total_main_requests)
    print("Total 8/8 Main Requests Placed: ", total_eight_main_schedules * 100 / total_eight_mains_people)
    print("Total 7-8/8 Main Requests Placed: ", total_seven_eight_main_schedules * 100 / total_eight_mains_people)
    print("Total 8/8 Main or Alternate Requests Placed: ", total_eight_main_or_alt_schedules * 100 / total_eight_mains_people)


    export_timetables_to_excel(best_timetable, 'timetables.xlsx')
    create_real_master_timetable(best_timetable, max_enrollments)


    get_timetable_by_id(1000, best_timetable)
