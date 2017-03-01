
# NOTE from pedro
# This is a qucik hack as POC
# ideally we want renderers and some dynamics

import os

import yaml

from flask import Flask, render_template, jsonify
#from flask.ext.api import renderers

from ogt import ags4

err = ags4.initialise()
if err:
    PANIC

HERE_PATH =  os.path.abspath( os.path.dirname( __file__ ))
PROJECT_ROOT = os.path.abspath( os.path.join(HERE_PATH, "..") )

app = Flask(__name__, static_url_path="", static_folder=os.path.join(PROJECT_ROOT, "static"))

#print "################RENDERS=", app.config['DEFAULT_RENDERERS']

"""
class YAMLRenderer(renderers.BaseRenderer):
    media_type = 'application/yaml'

    def render(self, data, media_type, **options):
        return yaml.dump(data, encoding=self.charset)
"""

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

def xrender(ext, data):
    """Our custom function to knock out the stuff"""
    pass

@app.route('/')
def index():
    c = make_page_context("/", "OGT Server")
    return render_template('index.html', c=c)


#@app.route('/ags4/data-dict')
@app.route('/ags4/data-dict.<ext>')
def ags4_dd_json(ext="json"):
    if ext == "json":
        return jsonify(ags4.all())

    if ext in ["yml", "yaml"]:
        return yaml.dump(ags4.all())

    return "NOT Handled : `%s`" % ext

@app.route('/ags4/groups')
@app.route('/ags4/groups.<ext>')
def ags4_groups(ext="html"):
    if ext == "json":
        return jsonify({"groups": ags4.groups(), "success": True})

    if ext in ["yml", "yaml"]:
        return yaml.dump(ags4.all())

    c = make_page_context("/ags4/groups", "AGS4 Groups")

    # TODO Make its nested based on class
    c['ags4_classified_groups'] = ags4.classified_groups()
    #print c['ags4_classified_groups']
    return render_template("ags4_groups.html", c=c)


@app.route('/ags4/groups_list.<ext>')
def ags4_groups_list(ext="json"):
    if ext == "json":
        return jsonify({"groups_list": ags4.groups().values(), "success": True})


@app.route('/ags4/group/<group_code>')
@app.route('/ags4/group/<group_code>.<ext>')
def ags4_group(group_code, ext="html"):
    if ext == "json":
        return jsonify({"group": ags4.group(group_code), "success": True})

    if ext in ["yml", "yaml"]:
        return yaml.dump(ags4.all())

    c = make_page_context("/ags4/group", "AGS4 Group")

    # TODO Make its nested based on class
    c['ags4_group'] = ags4.group(group_code)
    print c['ags4_group']
    return render_template("ags4_group.html", c=c)


@app.route('/ags4/widget')
def ags4_widget():
    c = make_page_context("/ags4/widget", "AGS4 Widget")
    return render_template('ags4_widget.html', c=c)
