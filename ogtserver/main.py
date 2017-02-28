

from flask import Flask, render_template


app = Flask(__name__)

nav = [
    {"url": "/", "label": "Home"},
    {"url": "/about", "label": "About"},
    {"url": "/widget", "label": "AGS4 Data Dict"},
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



@app.route('/spec/ags4')
def ags4_spec():
    c = make_context("/about", "About")
    return render_template('<b>SPECCC {{name}}</b>!', c=c)
