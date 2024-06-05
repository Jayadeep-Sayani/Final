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
            if line[18] == "Y" or line[18] == "N":
                sections[line[0]] = (int)(line[14])
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
            if line[18] == "Y" or line[18] == "N":
                maxEnrollment[line[1]] = (int)(line[14])
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


max_enrollments = extract_maxEnrollment()

def score_master_timetable(master_timetable, sequencing_rules):
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
        for course in person_schedule:
            if "linear" in course.lower():
                if (course in first_half and course not in second_half) or (course in second_half and course not in first_half):
                    score -= 20
                elif course in first_half and course in second_half:
                    score += 20
        course_counts = count_strings_in_columns(master_timetable)

        for course in max_enrollments:
            if course_counts[course] > max_enrollments[course]:
                score -= 20
            else:
                score += 20
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

def mutate(timetable, mutation_rate=0.1):
    for i in range(len(timetable)):
        if random.random() < mutation_rate:
            swap_idx = random.randint(0, len(timetable)-1)
            timetable[i], timetable[swap_idx] = timetable[swap_idx], timetable[i]
    return timetable

def genetic_algorithm(schedule_requests, sequencing_rules, population_size=100, generations=30, mutation_rate=0.5, elitism_size=5):
    population = generate_initial_population(schedule_requests, population_size)
    scores = [score_master_timetable(individual, sequencing_rules) for individual in population]
    print(generations)
    for generation in range(generations):
        print(generation)
        new_population = []
        scores = [score_master_timetable(individual, sequencing_rules) for individual in population]
        population = [x for _, x in sorted(zip(scores, population), reverse=True)]
        for _ in range(elitism_size):
            new_population.append(population[_])
        while len(new_population) < population_size:
            parent1 = select_parents(population, scores)
            parent2 = select_parents(population, scores)
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)
            new_population.extend([child1, child2])
        population = new_population
    best_individual = max(population, key=lambda x: score_master_timetable(x, sequencing_rules))
    best_score = score_master_timetable(best_individual, sequencing_rules)
    return best_individual, best_score



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

if __name__ == "__main__":
    with open("data/Course Information.csv", mode='r') as file:
        csv_reader = csv.reader(file)
        for line in csv_reader:
            if line[18] == 'Y' or line[18] == 'N':
                course_ids[line[0]] = line[2]

    schedule_requests = extract_schedules()
    maxEnrollment = extract_maxEnrollment()
    sequencing = extract_sequencing()
    sections = extract_sections()

    for schedule in schedule_requests:
        while len(schedule.requested_main_courses) < 8:
            schedule.requested_main_courses.append(Course("", "", False, False, False))

    initial_population_size = 100
    generations = 30
    mutation_rate = 0.1
    elitism_size = 5

    best_timetable, best_score = genetic_algorithm(schedule_requests, sequencing, initial_population_size, generations, mutation_rate, elitism_size)



    print("Best Score:", best_score)
    export_timetables_to_excel(best_timetable, 'timetables.xlsx')
    create_real_master_timetable(best_timetable, maxEnrollment)

        