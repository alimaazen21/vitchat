import google.generativeai as genai
import sys

# Configure API key and model
genai.configure(api_key="AIzaSyB0v2dpVkf4E_1-UsoT1NaQU0qIU8oG96k")
model = genai.GenerativeModel('gemini-1.5-flash')

# Get user input

with open("data/personal_data.txt", "r") as file1:
    personal_details = file1.read()

user_prompt = f"{personal_details} what is my name?"


# Generate response
response = model.generate_content(user_prompt)

# Print the response
print(response.text)