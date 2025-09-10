import subprocess

def run_script(script_name):
    subprocess.run(['python', script_name])

def main():
    run_script('acquire_data.py')
    run_script('chatbot.py')

if __name__ == '__main__':
    main()