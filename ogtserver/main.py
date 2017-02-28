
import os

from flask import Flask, render_template

HERE_PATH =  os.path.abspath( os.path.dirname( __file__ ))
PROJECT_ROOT = os.path.abspath( os.path.join(HERE_PATH, "..") )

app = Flask(__name__, static_url_path="", static_folder=os.path.join(PROJECT_ROOT, "static"))

nav = [
    {"url": "/", "label": "Home"},
    {"url": "/about", "label": "About"},
    {"url": "/ags4/widget", "label": "AGS4 Data Dict"},
    {"url": "/viewer", "label":"Viewer"}
]

def make_context(url, page_title):
    c = {"site_name": "OGT Server",
        "nav": nav, "url": url, "page_title": page_title
    }
    """
    c['page_title']= ""
    for n in nav:
        if n['url'] = page:
            c['page_title']
    """
    return c

@app.route('/')
def index():
    c = make_context("/", "OGT Server")
    return render_template('index.html', c=c)



@app.route('/ags4/widget')
def ags4_widget():
    c = make_context("/ags4/widget", "AGS4 Widget")
    return render_template('ags4_widget.html', c=c)
