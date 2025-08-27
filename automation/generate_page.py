import json

# These constants are used for text replacement within the format HTML files.
LOOKUP_OPENER = "(!!! "
LOOKUP_CLOSER = " !!!)"
LOOKUP_ACTIVE = " ACTIVE"
LOOKUP_COLLEGE_BANNER = LOOKUP_OPENER + "COLLEGE BANNER" + LOOKUP_CLOSER
LOOKUP_COURSE_BANNER = LOOKUP_OPENER + "COURSE BANNER" + LOOKUP_CLOSER
LOOKUP_PDF_NAME = LOOKUP_OPENER + "FILE NAME" + LOOKUP_CLOSER
LOOKUP_COURSE_TITLE = LOOKUP_OPENER + "COURSE TITLE" + LOOKUP_CLOSER

LOOKUP_ENTRY_ADDITION = "<!-- NEW ENTRIES MAY BE ADDED HERE -->"
LOOKUP_DESCRIPTION = LOOKUP_OPENER + "DESCRIPTION" + LOOKUP_CLOSER
LOOKUP_TITLE = LOOKUP_OPENER + "TITLE" + LOOKUP_CLOSER
LOOKUP_NUMBER = LOOKUP_OPENER + "COURSE NUMBER" + LOOKUP_CLOSER
LOOKUP_ENTRY_START = "<!-- ENTRIES BEGIN HERE -->"
LOOKUP_ENTRY_END = "<!-- ENTRIES END HERE -->"

F_DIR_FORMATS = "page_formats/"
F_BANNER_DIR = F_DIR_FORMATS + "banner_formats/"
F_BANNER = "_banner.html"
F_COLLEGES_BANNER = F_BANNER_DIR + "colleges" + F_BANNER
F_COURSE_PAGE = F_DIR_FORMATS + "course_page.html"
F_COLLEGES_PATH = "../colleges/"
F_COURSE_PAGES_PATH = "/course_pages/"
F_COURSE_ENTRY = F_DIR_FORMATS + "course_description_entry.html"
F_CATALOG = "course_catalog.json"

COLLEGE_LST = ["cad","cet","chst","cola","cos","gccis","kgcoe","ntid","other","scb","sois"]

BANNER_ACTIVE_ID = "class=\"active\""
PDF_DIR = "../pdfs/"
PDF_FILETYPE = ".pdf"
TITLE_OPENER = "RIT Syllabus Registry: "
ENTRY_BLOCK = f"{LOOKUP_ENTRY_START}\n{LOOKUP_ENTRY_ADDITION}\n{LOOKUP_ENTRY_END}"

JSON_TITLE = "TITLE"
JSON_CODE = "ID"
JSON_DESCRIPTION = "DESC"


def build_banner(college):
    return f"{F_BANNER_DIR}{college}{F_BANNER}"

def build_active(entry):
    return f"{LOOKUP_OPENER}{entry}{LOOKUP_ACTIVE}{LOOKUP_CLOSER}".upper()

def build_pdf_src(number):
    return f"{PDF_DIR}{number}{PDF_FILETYPE}"

def build_title(code,number):
    return f"{TITLE_OPENER}{code}-{number}"

# Find what college the course ID belongs to.
#   INPUT: course_code - four letter code defining what department the course falls into
#   OUTPUT: banner list entry, defined as follows:
#               Index 0: College course banner HTML file path
#               Index 1: College abbreviation.
def find_course_college(course_code):
    # Build the lookup and replacement string for whatever course we're looking for.
    id_str = f"{LOOKUP_OPENER}{course_code}{LOOKUP_ACTIVE}{LOOKUP_CLOSER}"
    
    for banner_entry in COLLEGE_LST:
        f = open(f"{build_banner(banner_entry)}", "r")
        f_str = f.read()
        f.close()

        # Debug print. Can remove this once this code is done.
        if id_str.upper() in f_str.upper():
            return banner_entry


    return ""

# Build the page for the course itself
def build_course_page(course_code, course_number):

    # STEP 1: Identify what college we're looking at.
    course_college = find_course_college(course_code)

    # STEP 2: Read in the course page HTML file
    f_course_page = open(F_COURSE_PAGE, "r")
    course_page_html = f_course_page.read()
    f_course_page.close()

    # STEP 3: Read in the college banner HTML file
    f_college_banner = open(F_COLLEGES_BANNER, "r")
    college_banner_html = f_college_banner.read()
    f_college_banner.close()

    # STEP 4: Read in the course code banner HTML file
    f_course_banner = open(build_banner(course_college), "r")
    course_banner_html = f_course_banner.read()
    f_course_banner.close()

    # STEP 5: Build an updated college banner based on the current active college
    for college in COLLEGE_LST:
        active = build_active(college)
        if college == course_college:
            college_banner_html = college_banner_html.replace(active, BANNER_ACTIVE_ID)
        else:
            college_banner_html = college_banner_html.replace(active, "")

    course_banner_html = course_banner_html.replace(build_active(course_code), BANNER_ACTIVE_ID)
    course_banner_html_lines = course_banner_html.split("\n")
    course_banner_html = ""
    for course_banner_html_line in course_banner_html_lines:
        # check for header / irrelevant lines. We paste these in normally.
        if LOOKUP_OPENER not in course_banner_html_line or LOOKUP_CLOSER not in course_banner_html_line:
            course_banner_html += f"{course_banner_html_line}\n"
            continue

        # We have to replace an "active" line! Remove anything between the lookup opener and closer
        course_banner_html += f"{course_banner_html_line.split(LOOKUP_OPENER)[0]}{course_banner_html_line.split(LOOKUP_CLOSER)[1]}\n"

    # STEP 6: Apply the updated banners
    course_page_html = course_page_html.replace(LOOKUP_COLLEGE_BANNER, college_banner_html)
    course_page_html = course_page_html.replace(LOOKUP_COURSE_BANNER, course_banner_html)
    course_page_html = course_page_html.replace(LOOKUP_COURSE_TITLE, build_title(course_code, course_number))
    course_page_html = course_page_html.replace(LOOKUP_PDF_NAME, build_pdf_src(course_number))

    # STEP 7: Create the new course listing.
    course_page_path = f"{F_COLLEGES_PATH}{course_college}/{course_code}{F_COURSE_PAGES_PATH}{course_number}.html"
    f_output = open(course_page_path, "w")
    f_output.write(course_page_html)
    f_output.close()

def reset_course_list(course_code):
    # STEP 1: Identify what college we're looking at.
    course_page_path = f"{F_COLLEGES_PATH}{find_course_college(course_code)}/{course_code}/{course_code}.html"

    # STEP 2: Read in the existing course list.
    f_courses = open(course_page_path, "r")
    courses_html = f_courses.read()
    f_courses.close()

    # STEP 3: Ensure there is somewhere to reset entries.
    if LOOKUP_ENTRY_START not in courses_html or LOOKUP_ENTRY_END not in courses_html:
        return
    
    courses_html = f"{courses_html.split(LOOKUP_ENTRY_START)[0]}{ENTRY_BLOCK}{courses_html.split(LOOKUP_ENTRY_END)[1]}"
    
    f_output = open(course_page_path, "w")
    f_output.write(courses_html)
    f_output.close()

# Insert the page into the the overarching course page
def update_course_list(course_code, course_number, course_title, course_description):
    # STEP 1: Identify what college we're looking at.
    course_page_path = f"{F_COLLEGES_PATH}{find_course_college(course_code)}/{course_code}/{course_code}.html"

    # STEP 2: Read in the existing course list.
    f_courses = open(course_page_path, "r")
    courses_html = f_courses.read()
    f_courses.close()

    # STEP 2: Read in the existing course list.
    f_entry = open(F_COURSE_ENTRY, "r")
    entry_html = f_entry.read()
    f_entry.close()

    # STEP 3: Replace description, title, and number in the entry.
    entry_html = entry_html.replace(LOOKUP_DESCRIPTION, course_description)
    entry_html = entry_html.replace(LOOKUP_TITLE, f"{course_code}-{course_number}: {course_title}")
    entry_html = entry_html.replace(LOOKUP_NUMBER, course_number)

    # STEP 4: Add the entry.
    courses_html = courses_html.replace(LOOKUP_ENTRY_ADDITION, f"{entry_html}\n{LOOKUP_ENTRY_ADDITION}")

    # STEP 2: Read in the existing course list.
    f_output = open(course_page_path, "w")
    f_output.write(courses_html)
    f_output.close()

# MAIN FUNCTION:
#   1. Determine the course being generated (should be of format ABCD-123)
#   2. Determine the college the course is generated for.
#   3. Build the course page.
#   4. Insert the course page into the 
if __name__ == "__main__":
    # List of courses. TODO: Read this in from a JSON or set of JSONS
    f_courses = open(F_CATALOG, "r")
    courses_json = json.load(f_courses)
    f_courses.close()
    
    # Reset all courses to remove entries.
    done_codes = []
    for course in courses_json:
        code = course[JSON_CODE].split("-")[0]
        if code not in done_codes:
            done_codes.append(code)
            reset_course_list(code)
    for course in courses_json:
        input_course = course[JSON_CODE].split("-")
        build_course_page(input_course[0], input_course[1])
        update_course_list(input_course[0], input_course[1], course[JSON_TITLE], course[JSON_DESCRIPTION])