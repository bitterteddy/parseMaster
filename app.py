from flask import Flask, render_template
from models.database import initialize
from parse_methods.soup_parser import SoupParser
from parse_methods.regex_parser import RegexParser
import json

app = Flask(__name__, static_folder="dir", template_folder="dir/templates")

app = initialize(app, "parse_Master")
# app = initialize(app)

@app.route("/")
def index():
    # print("Rendering index.html")
    # return "Hello, World!"
    # return render_template("index.html")
    try:
        print("Rendering index.html")
        return render_template("index.html")
    except Exception as e:
        print(f"Error rendering template: {str(e)}")
        return str(e)

    

@app.route("/test")
def test():
    print("Test route is working!")
    return "Test Page"


if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(host='localhost', port=5001,debug=True)