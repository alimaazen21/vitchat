from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/acquire_data.py', methods = ["GET", "POST"])
def get_credentials():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
    return render_template("/login.html")

if __name__=='__main__':
    app.run(debug=True)