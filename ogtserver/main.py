
import os

from flask import Flask, render_template, jsonify

from ogt import ags4

err = ags4.initialise()
if err:
    PANIC

HERE_PATH =  os.path.abspath( os.path.dirname( __file__ ))
PROJECT_ROOT = os.path.abspath( os.path.join(HERE_PATH, "..") )

app = Flask(__name__, static_url_path="", static_folder=os.path.join(PROJECT_ROOT, "static"))

nav = [
    {"url": "/", "label": "Home"},
    {"url": "/about", "label": "About"},
    {"url": "/ags4/widget", "label": "AGS4 Data Dict"},
    {"url": "/viewer", "label":"Viewer"}
]

def make_page_context(url, page_title):
    """Simple way to bang all vaiables into c"""
    c = {"site_name": "OGT Server",
        "nav": nav,
        "url": url,
        "page_title": page_title
    }
    return c

@app.route('/')
def index():
    c = make_page_context("/", "OGT Server")
    return render_template('index.html', c=c)

@app.route('/ags4/data-dict.json')
def ags4_dd_json():
    return jsonify(ags4.all())

@app.route('/ags4/data-dict.yaml')
def ags4_dd_yaml():
    return render_template('ags4_sss.html', c=c)


@app.route('/ags4/widget')
def ags4_widget():
    c = make_page_context("/ags4/widget", "AGS4 Widget")
    return render_template('ags4_widget.html', c=c)
