# -*- coding: utf-8 -*-

import os
from fabric.api import env, local, run, cd, lcd, sudo, warn_only, prompt, shell_env

os.environ["__GEN_DOCS__"] = "1"

import ogt
import ogt.ags4

HERE_PATH =  os.path.abspath( os.path.dirname( __file__ ))
TEMP_LOCAL = os.path.join(HERE_PATH, "temp_workspace")
DOCS_BUILD_DIR = os.path.join(TEMP_LOCAL, "docs_build")


HOST_ADDRESS = 'ogtserver.daffodil.uk.com'
HOST_USER = "ogt"

env.hosts = [ HOST_ADDRESS ]
env.user = HOST_USER
env.use_ssh_config = True # using key, not password
env.password = "--using-ssh-key--"
#env.shell = "/bin/sh -c"
env.shell = "/bin/bash -l -c"


def docs_server(port=8080):
    """Run simple local HTTP server with docs"""
    with lcd(TEMP_LOCAL + "/docs_build"):
        local("python -m SimpleHTTPServer %s" % port)

def docs_clean():
    """Clean current docs build """
    local("rm ./docs/_static/favicon.*")
    local("rm -f -r temp/*")

def docs_build(clear=None):
    """Build the documentation to temp dir"""
    #build_dir = "%s/docs_build" % TEMP_LOCAL
    build_dir = "/home/opengeo/open-geotechnical.github.io/ogt-ags-py"
    # copy some stuff
    local("cp ./static/images/favicon.* ./docs/_static/")
    local("cp ./static/images/logo.* ./docs/_static/")
    local("cp ./static/images/logo-small.* ./docs/_static/")

    ## run build
    clear_cache_flag = "-E" if clear else ""
    local("/usr/bin/python2 /usr/local/bin/sphinx-build %s -a  -b html ./docs/ %s" % (clear_cache_flag, build_dir))

    #local('echo "User-agent: *\nDisallow: /" > %/robots.txt' % build_dir)




def svg2icons():
    """Converts the svg icons to png"""
    src_d = os.path.join(HERE_PATH, "static", "svg")
    target_d = os.path.join(HERE_PATH, "static", "icons")

    output = local('ls %s' % os.path.join(src_d, "*.svg"), capture=True )
    files = output.split()
    print files

    for fp in files:
        f = os.path.basename(fp)
        s_file = os.path.join(src_d, f)
        t_file = os.path.join(target_d, f + ".png" )
        #local("convert -resize 32x32 %s %s " % (s_file, t_file))
        local("inkscape -z -e %s -w 32 -h 32 %s" % (t_file, s_file))


def pyclean():
    """Delete all `.pyc` python compiled files"""
    local(' find . | grep -E "(__pycache__|\.pyc$)" | xargs rm -rf ')

def server(port=13777):
    """Locally runs the ogtserver"""
    print os.environ.get("PYTHONPATH")
    main = os.path.join(HERE_PATH, "ogtserver", "main.py")
    with shell_env(FLASK_DEBUG="1", FLASK_APP=main):
        local("/usr/bin/python2.7 -m flask run --host=0.0.0.0 --port=%s" % (port))


def sshtest():
    run("ls -al")
    run("whoami")
