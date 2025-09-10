from PIL import Image
from IPython.display import display

import google.generativeai as genai
genai.configure(api_key="AIzaSyB0v2dpVkf4E_1-UsoT1NaQU0qIU8oG96k")
model = genai.GenerativeModel('gemini-1.5-flash')



captcha = Image.open('captcha.jpg')

prompt = """read the text carefully in the image"""
response = model.generate_content([prompt, captcha])
print(response.text)