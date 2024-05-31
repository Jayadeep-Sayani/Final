import csv

# CourseRequest class
class CoursesRequest:

    # Constructor
    def __init__(self):
        self.main_courses = []

    # Adds course to the Timetable Request
    def add_course(self, course):
        if course.alternate == 'N':  # Only consider main courses
            self.main_courses.append(course)
        
    # Returns the main course requests
    def get_course_requests(self):
        return self.main_courses

# Course class
class Course:

    # Constructor
    def __init__(self, name, course_id_, alt):
        self.name = name
        self.course_id = course_id_
        self.alternate = alt

# Timetable class - Timetable created based on a person's request
class Timetable:

    # Constructor
    def __init__(self):
        self.semester_1 = []
        self.semester_2 = []

    # Adds course to a specified semester
    def add_course(self, course, semester):
        if semester == 1:
            if len(self.semester_1) < 4:
                self.semester_1.append(course)
        elif semester == 2:
            if len(self.semester_2) < 4:
                self.semester_2.append(course)

# Extract schedules from csv file
def extract_schedules():
    schedules = []
    schedule = CoursesRequest()
    with open('Cleaned Student Requests.csv', mode='r') as file:
        csvFile = csv.reader(file)
        for lines in csvFile:
            if len(lines) > 2:
                if lines[3] == '':
                    schedules.append(schedule)
                    schedule = CoursesRequest()
                else:
                    course_to_add = Course(lines[3], lines[0], lines[11])
                    schedule.add_course(course_to_add)
    return schedules

# Creates the timetables based on requests
def create_timetables(schedule_requests):
    fully_scheduled_count = 0
    seven_or_eight_scheuled_count = 0
    
    for schedule_request in schedule_requests:
        courses = schedule_request.get_course_requests()
        timetable = Timetable()  # Create a new timetable for each schedule request
        
        # Adds courses to the timetable
        for course in courses:
            if len(timetable.semester_1) < 4:
                timetable.add_course(course, 1)
            elif len(timetable.semester_2) < 4:
                timetable.add_course(course, 2)

        # Check if all 8 requested courses were scheduled
        if len(timetable.semester_1) == 4 and len(timetable.semester_2) == 4 and len(schedule_request.get_course_requests()) == 8:
            fully_scheduled_count += 1

        if (len(timetable.semester_1) + len(timetable.semester_2)) > 6 and len(schedule_request.get_course_requests()) > 6:
            seven_or_eight_scheuled_count += 1

    total_eight_main_course_requests = 0
    total_main_requests = 0
    total_seven_or_eight_course_requests = 0
    for schedule_request in schedule_requests:


        if len(schedule_request.get_course_requests()) > 6:
            total_seven_or_eight_course_requests += 1
        
        if len(schedule_request.get_course_requests()) == 8:
            total_eight_main_course_requests += 1

    fulfilled_eight_percentage = (total_eight_main_course_requests / fully_scheduled_count) * 100
    fulfilled_seven_or_eight_percentage = (total_seven_or_eight_course_requests / seven_or_eight_scheuled_count) * 100

    return fulfilled_eight_percentage, fulfilled_seven_or_eight_percentage

# Main 
#----------------------------

# Extracts data
all_schedule_requests = extract_schedules()

# Create timetables and get stats
eight, seven_or_eight = create_timetables(all_schedule_requests)

# Print the percentage of people who got all 8 requested main courses
print(f"Percentage of people who got all 8 requested main courses: {eight:.2f}%")
print(f"Percentage of people who got 7-8 requested main courses: {seven_or_eight:.2f}%")
