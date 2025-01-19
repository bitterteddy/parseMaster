from flask import Flask, render_template
from parse_methods.soup_parser import SoupParser
from parse_methods.regex_parser import RegexParser
import json

app = Flask(__name__, static_folder="dir", template_folder="dir/templates")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)