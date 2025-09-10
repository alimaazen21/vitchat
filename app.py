import os
import time
import traceback
import re
from flask import Flask, request, jsonify, render_template, redirect, url_for
import google.generativeai as genai
import sys

genai.configure(api_key="AIzaSyB0v2dpVkf4E_1-UsoT1NaQU0qIU8oG96k")
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

grade_history_file = "data/new_grade_history.txt"
attendance_records_file = "data/new_attendance_records.txt"
calendar_data_file = "data/calendar_data.txt"
personal_data_file = "data/personal_data.txt"
detailed_attendance_records_file = "data/detailed_attendance_records.txt"

with open(grade_history_file, 'r') as f:
    grade_history = f.read()
with open(attendance_records_file, 'r') as f:
    attendance_data = f.read()
with open(calendar_data_file, 'r') as f:
    calendar_data = f.read()
with open(personal_data_file, 'r') as f:
    personal_data = f.read()
with open(detailed_attendance_records_file, 'r') as f:
    detailed_attendance_data = f.read()


@app.route('/')
def vitchat():
    time.sleep(1)
    return render_template('vitchat.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        prompt = request.json.get('prompt', '').strip().lower()

        if re.search(r"what gpa should", prompt, re.IGNORECASE):
            final_prompt = f"(always answer in second person and do not mention where you got the data from, if required gpa is above 10 mention it is impossible this sem, maybe try next sem) Based on the following data, answer the question in these steps, : 1. Calculate the total credits after this semester: Total credits = Credits earned so far + Current semester credits 2. Calculate the target CGPA points: Target points = Desired CGPA * Total credits 3. Calculate the points earned so far: Points earned so far = Current CGPA * Credits earned so far 4. Calculate the points needed in this semester: Points needed = Target points - Points earned so far 5. Calculate the required GPA for this semester: Required GPA = Points needed / Current semester credits Therefore, you need to aim for a GPA of approximately 'required GPA' this semester to reach a cumulative GPA of 'desired gpa' points. {grade_history} {attendance_data} {calendar_data} {personal_data} {detailed_attendance_data} query: {prompt}"
            response = model.generate_content(final_prompt)
            return jsonify({'response': response.text})

        final_prompt = f"(always answer in second person and do not mention where you got the data from) Based on the following data answer the question: {grade_history} {attendance_data} {calendar_data} {personal_data} {detailed_attendance_data} question: {prompt}"
        response = model.generate_content(final_prompt)

        return jsonify({'response': response.text})

    except Exception as e:
        traceback.print_exc()
        print(e)
        return jsonify({'error': 'Sorry, something went wrong. Please try again later.'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
