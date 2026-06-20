#Main script for generate testcases
import os
import sys

from dotenv import load_dotenv
from google import genai   
from google.genai import types 
import openpyxl

#Read the requirement file (BRD, User stories or plain text) from requiremtns folder

def generate_testcases(requirements_file):
    load_dotenv()
    with open(requirements_file,"r") as f:
        output_requirement = f.read()

    #create a gemini Client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    #Create the prompt
    testcase_generation_prompt = f"""
        You are a senior QA engineer.
        Below is a requirements document. 
        Generate detailed test cases from it.

        REQUIREMENTS:
        {output_requirement}

        Generate EXACTLY these categories:
        - Positive test cases (cover all happy paths)
        - Negative test cases (cover all error scenarios)
        - Boundary test cases (cover all boundary values)
        - Edge test cases (cover security and unusual scenarios)

        IMPORTANT RULES:
        - Cover EVERY requirement mentioned in the document
        - Do not skip any acceptance criteria
        - Each test case must be unique
        - Output a single markdown table with all test cases combined
        - NO section headers like "Positive Test Cases"
        - NO bold text like **Positive Test Cases**
        - NO introductory text before the table
        - NO summary text after the table
        - First line must be the table header row
        - Every test case on its own row immediately after
        - Test case number should be continuous across all categories (TC1, TC2, TC3, etc.)
        - If Test Data is not applicable, always write N/A in that cell, never leave it empty
        - Every row must have exactly 8 columns
        - Never skip any column even if the value is N/A or empty

        Format each test case as a markdown table row with these exact columns:
        TC No., Title, Description, Test Data, Expected Result, Priority, Actual Result, Execution Status
        Last two fields can be empty.
    """

    #call the gemini API
    api_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=testcase_generation_prompt,
        config=types.GenerateContentConfig(
            temperature=0.1
    ))

    #testcase generation
    test_cases = api_response.text
    print("Testcases Generated")
    return test_cases

#output the test cases to a csv file in the output folder
def save_testcases_to_excel(test_cases, output_file):
    #create new workbook
    workbook = openpyxl.Workbook()
    current_sheet = workbook.active
    current_sheet.title = "Test Cases"

    #header row
    headers = ["TC No.", "Title", "Description", "Test Data", "Expected Result", "Priority", "Actual Result", "Execution Status"]
    current_sheet.append(headers)

    for line in test_cases.split("\n"):
        #if line.startswith("|"):
        if "|" in line:
            cells = line.split("|")
            cells = [c.strip() for c in cells if c]
            if cells and cells[0] not in ["TC No.", "Title", "Description", "Test Data", "Expected Result", "Priority", "Actual Result", "Execution Status","---"]:
                current_sheet.append(cells)
        
    workbook.save(output_file)
    print(f"Testcases saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2: 
        print("Usage: python generate_testcases.py requirements/requirements_login.txt")
        sys.exit(1)
    requirements_file = sys.argv[1]
    test_cases = generate_testcases(requirements_file)
    output_file = os.path.join("outputs","test_cases.xlsx")
    save_testcases_to_excel(test_cases, output_file)
