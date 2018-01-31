import os
import tempfile

####################################################
# Note this file is for variables only, no imports
# except standard libs where necessary
# as its imported for docs gen etc
####################################################

PROJECT_VERSION = "0.0.1"

PROJECT_SHORT = "ogt-ags-py"
PROJECT_LONG = "Open GeoTechnical AGS Tools"

PROJECT_DESCRIPTION = "Lib and tools for playing geotechnical stuff"
PROJECT_CONTACT = "ogt@daffodil.uk.com"

PROJECT_DOMAIN = "ogt.daffodil.uk.com"
PROJECT_WWW = "http://open-geotechnical.github.io/"
PROJECT_HOME = "https://github.com/open-geotechnical/ogt-ags-py"
PROJECT_ISSUES = "https://github.com/open-geotechnical/ogt-ags-py/issues"
PROJECT_API_DOCS = "http://open-geotechnical.github.io/ogt-ags-py"


def get_project_info():
    """
    :return: A `dict` with the project info
    """
    return dict(
        version = PROJECT_VERSION,
        short = PROJECT_SHORT,
        long = PROJECT_LONG,
        description = PROJECT_DESCRIPTION,
        contact = PROJECT_CONTACT,
        domain = PROJECT_DOMAIN,
        www = PROJECT_WWW,
        home = PROJECT_HOME,
        issues = PROJECT_ISSUES,
        api_docs = PROJECT_API_DOCS
    )



HERE_PATH =  os.path.abspath( os.path.dirname( __file__))

PROJECT_ROOT_PATH = os.path.abspath( os.path.join(HERE_PATH, ".."))
"""Root dir of this project"""

TEMP_DIR = tempfile.gettempdir()
#TEMP_WORKSPACE = os.path.join(PROJECT_ROOT_PATH, "temp_workspace")
TEMP_WORKSPACE = os.path.join(TEMP_DIR, "temp_workspace")
"""Path to temporary directory"""

EXAMPLES_DIR = os.path.join(TEMP_DIR, "example_files")
"""Path to examples folder"""

USER_HOME = os.path.expanduser("~")
"""Path to users home dir"""

USER_TEMP = os.path.join(USER_HOME, "ogt-workspace")
"""Path to open-getechnical cache directory"""




FORMATS = ["json", "js", "geojson", "yaml", "xlsx", "ags4"]
"""Formats allowed, depending on stuff installed"""



HAVE_YAML = False
"""`True` if :ref:`yaml` lib is installed"""
try:
    import yaml
    HAVE_YAML = True
except ImportError:
    #print("yaml inavailable as lib not installed")
    pass

HAVE_EXCEL = False
"""`True` if :ref:`excel`  handling libs installed"""
try:
    import openpyxl
    HAVE_EXCEL = True
except ImportError as e:
    pass

HAVE_GEOJSON = False
"""`True` if :ref:`excel`  handling libs installed"""
try:
    import geojson
    HAVE_GEOJSON = True
except ImportError as e:
    pass


HAVE_BNG_LATLON = False
"""`True` if :ref:`excel`  handling libs installed"""
try:
    import bng_to_latlon # https://github.com/fmalina/bng_latlon

    HAVE_BNG_LATLON = True
except ImportError as e:
    pass

class ERR_COLORS:
    noerr_bg = "#D8FFC5"
    err_bg = "#FFC5C5"
    warn_bg = "#FFEDC5"

class OgtError:

    WARN = 0
    ERR = 1


    def __init__(self, message, type=1, lidx=None, cidx=None, rule=None, cell=None):

        self.type = type
        """True to flag as error(default), False is a warning"""

        self.message = message
        """The error message"""

        self.rule = None if rule == None else str(rule)
        """The ags4 rule of error"""

        self.lidx = lidx
        """The line index of error """

        self.cidx = cidx
        """The csv column index of the error """

        self.cell = cell

    def __repr__(self):
        return "<Ogt %s - %s [%s,%s]>" % ("ERR" if self.type else "WARN", self.message, self.lidx, self.cidx)

    @property
    def line_no(self):
        """The line no is the line index +1 """
        if self.cell:
            return self.cell.lidx + 10
        if self.lidx == None:
            return 9999
        return self.lidx + 1

    @property
    def column_no(self):
        """The column_no no is the column index +1 """
        return 22
        return self.cidx + 1

    @property
    def bg(self):
        """Background color of error/warning"""
        return ERR_COLORS.err_bg if self.type else ERR_COLORS.warn_bg
