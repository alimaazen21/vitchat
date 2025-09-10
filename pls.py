import os
import re
import torch
from transformers import pipeline
from fuzzywuzzy import fuzz
from collections import deque

# Initialize Hugging Face Q&A pipeline
qa_pipeline = pipeline("question-answering")

# Parse the course data into a structured dictionary (from .txt file)
def parse_course_data(content):
    course_data = {}
    lines = content.splitlines()
    
    for line in lines:
        # Skip lines that don't contain useful course data
        if line.startswith("S.NO") or len(line.strip()) == 0:
            continue
        
        parts = re.split(r'\s{2,}', line.strip())  # Split by multiple spaces
        if len(parts) >= 6:
            course_code, course_name, course_type, grade, credit = parts[1], parts[2], parts[3], parts[4], parts[5]
            course_data[course_name.lower()] = {'course_code': course_code, 'grade': grade, 'credit': credit}
    
    return course_data

# Load course data from the file
def load_course_data(directory):
    files_content = {}
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), "r") as file:
                files_content[filename] = parse_course_data(file.read())
    return files_content

# Generate an answer based on a question and course data context
def generate_response(query, files_content, memory):
    # If the query is about a course grade, extract it directly
    if "grade" in query.lower() or "marks" in query.lower():
        return search_grade(query, files_content)
    
    # Provide context (i.e., previously answered queries)
    memory_context = memory.recall_memory()

    # Use Hugging Face's generative model to generate an answer
    context_text = f"Here is the course data: {str(files_content)}"
    full_query = memory_context + "\n\nQuestion: " + query + "\nContext: " + context_text
    
    # Using Hugging Face's QA pipeline to generate an answer
    answer = qa_pipeline({
        'context': context_text,
        'question': query
    })

    response_with_memory = f"Memory:\n{memory_context}\n\n{answer['answer']}"
    
    # Store the query-response pair in memory
    memory.add_to_memory(query, answer['answer'])
    
    return response_with_memory

# Search for a specific course grade based on user query
def search_grade(query, files_content):
    query = query.lower()
    
    for filename, courses in files_content.items():
        # Search through each course
        for course_name, course_info in courses.items():
            if fuzz.partial_ratio(query, course_name) > 70:  # Fuzzy matching threshold
                return f"Your grade in {course_name.title()} is {course_info['grade']}."
    
    return "Sorry, I couldn't find a grade for that course."

# Memory: Save the last few conversations to give context
class Memory:
    def __init__(self, max_size=5):
        self.history = deque(maxlen=max_size)

    def add_to_memory(self, query, response):
        self.history.append((query, response))

    def recall_memory(self):
        return "\n".join([f"You: {query}\nBot: {response}" for query, response in self.history])

# Main chatbot loop
def chat():
    directory = 'data'  # Assuming your text files are in a folder named 'data'
    files_content = load_course_data(directory)
    memory = Memory()
    print("Hello! I'm your chatbot. Ask me anything.")
    
    while True:
        query = input("You: ")
        
        if query.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye!")
            break

        response = generate_response(query, files_content, memory)
        print("Bot:", response)

if __name__ == "__main__":
    chat()
