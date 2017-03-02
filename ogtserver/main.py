
# NOTE from pedro
# This is a qucik hack as POC
# ideally we want renderers and some dynamics

import os
import sys
import yaml

HERE_PATH =  os.path.abspath( os.path.dirname( __file__ ))
PROJECT_ROOT = os.path.abspath( os.path.join(HERE_PATH, "..") )
if sys.path.count(PROJECT_ROOT) == 0:
	sys.path.insert(0, PROJECT_ROOT)


from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request, flash, redirect
#from flask.ext.api import renderers


from ogt import ags4, ogt_doc

err = ags4.initialise()
if err:
    PANIC



app = Flask(__name__, static_url_path="", static_folder=os.path.join(PROJECT_ROOT, "static"))

#print "################RENDERS=", app.config['DEFAULT_RENDERERS']

"""
class YAMLRenderer(renderers.BaseRenderer):
    media_type = 'application/yaml'

    def render(self, data, media_type, **options):
        return yaml.dump(data, encoding=self.charset)
"""

ALLOWED_UPLOADS = ['ags', 'ags4']


nav = [
    {"url": "/", "label": "Home"},
    {"url": "/about", "label": "About"},
    {"url": "/ags4/widget", "label": "AGS4 Data Dict"},
    {"url": "/viewer", "label":"Viewer"},
    {"url": "/convert", "label":"Convert"}
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

@app.route('/about')
def about():
    c = make_page_context("/about", "About")
    return render_template('about.html', c=c)

@app.route('/viewer')
def viewer():
    c = make_page_context("/viewer", "Viewer")
    return render_template('viewer.html', c=c)

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


@app.route('/ags4/abbrs_list.<ext>')
def ags4_abbrs_list(ext="html"):
    if ext == "json":
        return jsonify({"abbrs_list": ags4.abbrs(), "success": True})

    if ext in ["yml", "yaml"]:
        return yaml.dump(ags4.all())

    c = make_page_context("/ags4/groups", "AGS4 Groups")

    # TODO Make its nested based on class
    c['ags4_classified_groups'] = ags4.classified_groups()
    #print c['ags4_classified_groups']
    return render_template("ags4_groups.html", c=c)


@app.route('/ags4')
def ags4_index():
    c = make_page_context("/ags4", "AGS4 Data Dict")
    return render_template('ags4.html', c=c)

@app.route('/ags4/widget')
def ags4_widget():
    c = make_page_context("/ags4/widget", "AGS4 Widget")
    return render_template('ags4_widget.html', c=c)



@app.route('/ags4/examples')
@app.route('/ags4/examples.<ext>')
def ags4_examples(ext="html"):

    if ext == "json":
        return jsonify({"examples": ags4.examples(), "success": True})

    c = make_page_context("/ags4/examples", "AGS4 Widget")
    return render_template('ags4_examples.html', c=c)

@app.route('/ags4/examples_list.<ext>')
def ags4_examples_list(ext="json"):

    if ext == "json":
        return jsonify({"examples_list": ags4.examples_list(), "success": True})


@app.route('/ags4/example')
@app.route('/ags4/example.<ext>')
def ags4_example(ext="html"):

    file_name = request.args.get('file_name')
    if not file_name:
        panic
    ex = ags4.example(file_name)
    if ex:
        #print "EX=", ex
        doc = ogt_doc.OGTDocument()
        doc.source_file_path = ex['file_name']
        err = doc.load_ags4_string(ex['contents'])
        doc.edit_mode=True
        doc.include_stats=True
        doc.include_source=True
        #if request.args.get('format') == "json":
        #        return jsonify(doc.to_dict())
        if ext == "json":
            return jsonify({"document": doc.to_dict(), "success": True})

    c = make_page_context("/ags4/examples", "AGS4 Widget")
    return render_template('ags4_example.html', c=c)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_UPLOADS

@app.route('/convert', methods=["GET", "POST"])
def c_convert():

    c = make_page_context("/convert", "AGS4 Convert")
    c['err_mess'] = None
    if request.method == "POST":
        if 'ags_file' not in request.files:
            c['err_mess'] = "Need a file"

        else:
            file = request.files['ags_file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                c['err_mess'] = "Need a file"

            else:
                if file and allowed_file(file.filename):


                    doc = ogt_doc.OGTDocument()
                    doc.source_file_path = secure_filename(file.filename)
                    err = doc.load_ags4_string(file.read())

                    return jsonify(doc.to_dict())

    ## convert example
    """
    if request.method == "GET":
        ex_name = request.args.get('example')
        if ex_name:

            ex = ags4.example(ex_name)
            #print "EX=", ex
            doc = ogt_doc.OGTDocument()
            doc.source_file_path = ex_name
            err = doc.load_ags4_string(ex['contents'])

            if request.args.get('format') == "json":
                return jsonify(doc.to_dict())
    """

    return render_template('convert.html', c=c)

"""
@app.route('/convert.json', methods=["GET", "POST"])
def ajax_convert():

    ex_name = request.args.get('example')
    if ex_name:
        ex = ags4.example(ex_name)
        #print "EX=", ex
        doc = ogt_doc.OGTDocument()
        doc.source_file_path = ex_name
        err = doc.load_ags4_string(ex['contents'])

        return jsonify(doc.to_dict())
"""
