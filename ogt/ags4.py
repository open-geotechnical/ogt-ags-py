
import os
import io
from operator import itemgetter
#import urllib, urllib2
#import json

from ogt import PROJECT_ROOT_PATH, OgtError
import ogt.ogt_doc
import ogt.utils
#from ogt import utils, EXAMPLES_DIR

def ags4dd_file():
    """
    :return: str with path to the `ags4.min.json` data dict file
    """
    return os.path.join(PROJECT_ROOT_PATH, "static", "ags-4.0.4.json")



class AGS4_DataDict:
    """This dict contains all the ags4 data, loaded in initialise()"""

    GROUP = "GROUP"
    HEADING = "HEADING"
    UNIT = "UNIT"
    TYPE = "TYPE"
    DATA = "DATA"


    @staticmethod
    def group_header():
        """The list of headers as required and defined in :ref:`ags4_rule_2a`

        - GROUP = first .. obviously = tab on spreadsheet or db table
        - HEADING = second.. the columns, = cols on spreasheet or db fields
        - the data type and unit
        - then the almighty DATA ! ;-)
        - as this is the "group_header(), doth not return the DATA

        :return: A list of `descriptors` in order
        """
        return [
            AGS4_DataDict.group,
            AGS4_DataDict.heading,
            AGS4_DataDict.unit,
            AGS4_DataDict.type
        ]

    @staticmethod
    def list():
         return AGS4_DataDict.group_header() + [AGS4_DataDict.data]

    def __init__(self):

        self._data = None
        self._groups = None
        self._abbrs = None
        self._types = None
        self._units = None

        self._types_lookup_cache = None

        self.initialise()

    """
    def update(self):
        #Downloads data dict file from online
        #
        #:return: An error if one occured,  else None
        #TODO later
        #
        return
        if not os.path.exists(USER_TEMP):
            os.makedirs(USER_TEMP)



        for blobby in ["ags4.min.json", "ags4_examples.min.json"]:
            u = "https://open-geotechnical.github.io/data/%s" % blobby
            print "Requesting: %s" % u
            try:
                response = urllib2.urlopen(u)
            except Exception as e:
                return e

            txt = response.read()

            ## check its ok
            try:
                json.loads(txt)
            except Exception as e:
                print e

            ogt.utils.write_file(os.path.join(USER_TEMP, blobby), txt)
        return None
    """


    def initialise(self):
        """Check env is sane and loads the ags data dict file"""
        #if not os.path.exists(USER_TEMP):
        #    os.makedirs(USER_TEMP)

        if not os.path.exists(ags4dd_file()):
            return "Missing ags4 data dict"

        self._data, err = ogt.utils.read_json_file(ags4dd_file())

        if err:
            return err

        self._abbrs = self._data['abbrs']
        self._groups = self._data['groups']
        self._types = self._data['types']
        self._units = self._data['units']

        return None

    def groups(self):
        return self._groups

    def group(self, group_code):
        """Return all :term:`GROUP` s in the ags4 data dict

        :param group_code: The four character group code to initialize with
        :type group_code: str
        :rtype: dict
        :return:  the data if successful, else `None`
        """

        return self._groups.get(group_code)

    def abbrs(self):
        return self._abbrs

    def types_list(self):
        return self._types

    def types_dict(self):
        dic = {}
        for t in  self._types:
            dic[t['type']] = t['description']
        return dic


    def units_list(self):
        return self._units

    def picklist(self, head_code):
        return self._abbrs.get(head_code).get("abbrs")





    def type(self, abbr_code):
        if self._types_lookup_cache == None:
            self._types_lookup_cache = {}
            for typ in self._types:
                self._types_lookup_cache[typ['type']] = typ
        return self._types_lookup_cache.get(abbr_code)

    @staticmethod
    def descriptors():
        """Returns a list of descriptors  in correct order rule_3"""
        return [
            AGS4_DataDict.GROUP, AGS4_DataDict.HEADING, AGS4_DataDict.UNIT, AGS4_DataDict.TYPE, AGS4_DataDict.DATA
        ]


    def headings(self, group_code):
        #print sorted(self._groups.keys())
        #print self._groups
        if not group_code in self._groups:
            # print "NOT HOUND"
            return None
        #print self._groups[group_code]["headings"]
        return self._groups[group_code]["headings"]

    def headings_index(self, group_code):
        if not group_code in self._groups:
            return None
        return [h['head_code'] for h in self._groups[group_code]["headings"]]

AGS4 = AGS4_DataDict()
"""Global Instance """

class DEADAGS4_DESCRIPTOR:
    """Constants defining the data descriptors (See :ref:`ags4_rule_3`)

       The data descriptor is in the first column of every AGS row
       If the first column is not one of above.. then ohh dear.. fail
    """
    group = "GROUP"
    heading = "HEADING"
    unit = "UNIT"
    type = "TYPE"
    data = "DATA"






def doc_to_ags4_csv(doc):
    """Serialize a document to :term:`ags4` format :ref:`csv`

    :param doc: The document to convert
    :type doc: ogt.ogt_doc.OGTDocument
    :rtype: tuple
    :return:

        -
        -
    """
    #out = StringIO.StringIO()
    out = io.BytesIO()
    writer = csv.writer(out,
                        delimiter=',', lineterminator='\r\n',
                        quotechar='"', quoting=csv.QUOTE_ALL)

    for group_code in doc.groups_sort():

        grp = doc.group(group_code)

        # write "GROUP"
        writer.writerow([AGS4_DESCRIPTOR.group, group_code])

        # write headings
        lst = [AGS4_DESCRIPTOR.heading]
        lst.extend(grp.headings_sort())
        writer.writerow(lst)

        # write units
        lst = [AGS4_DESCRIPTOR.unit]
        lst.extend(grp.units_list())
        writer.writerow(lst)

        # write types
        lst = [AGS4_DESCRIPTOR.type]
        lst.extend(grp.types_list())
        writer.writerow(lst)


        # write data
        for dic in grp.data:
            lst = [AGS4_DESCRIPTOR.data]
            for ki in grp.headings_sort():
                lst.append( dic[ki] )
            writer.writerow(lst)

        writer.writerow([])


    return out.getvalue(), None



def classified_groups():
    """Returns groups nested n classification"""
    classes = {}
    for gcode, grp in groups().iteritems():
        cls = grp['class']
        if not cls in classes:
            classes[cls] = {}
        classes[cls][gcode] = grp
    return classes




class AGS4GroupDataDict:

    """Data dictionary of an ags :term:`GROUP`, reads the :ref:`json` definiton file"""
    def __init__(self, group_code):
        """
        :param group_code: The four character group code
        :type group_code: str
        """

        self.group_code = group_code

        self.raw_dict = None
        self.load_def()

    def load_def(self):
        """Loads the definition file"""
        self.raw_dict = AGS4.group(self.group_code)



    def to_dict(self):
        """
        :rtype: dict
        :return: A dictionary of the definition
        """
        return self.raw_dict

    @property
    def group_description(self):
        if self.raw_dict == None:
            return None
        return self.raw_dict.get("group_description")

    def group(self):
        """Return the group details; description, status, suggested type etc

        :rtype: dict
        :return: A dictionary of the group details
        """
        if self.raw_dict == None:
            return None
        return {key: value for key, value in self.raw_dict.items()
                if key not in ["headings", "notes"]}


    def headings_list(self):
        """Return headings list

        :return: A `list` of `dict` items
        """
        if self.raw_dict == None:
            return None

        return self.raw_dict.get("headings")

    def headings_sort(self):
        """A list of headings in correct sort order

        :rtype: a `list` of strings
        :return: A list of head_codes
        """
        if self.headings_list() == None:
            return None
        newlist = sorted(self.headings_list(), key=itemgetter('sort_order'))
        return [rec['head_code'] for rec in newlist]


    def heading(self, head_code):
        """Return data on a heading (see :term:`HEADER`)

        :type head_code: str
        :param head_code: The
        :return: a `tuple` with:

                - A **`dict`** with the heading details if found, else **`None`**
                - **`True`** if heading found, else **`False`**
        """
        headings = self.headings_list()
        if headings == None:
            return None, False

        for head in headings:
            if head['head_code'] == head_code:
                return head, True

        return None, False

    def notes(self):
        """Returns notes for this group

        :rtype: list of strings
        :return: Notes list
        """
        if self.raw_dict == None:
            return None
        return self.raw_dict.get("notes")



class Problem:
    """A container for ags validation problems and issues"""

    def __init__(self, row=None, column=None, field=None,
                 rule=None, group_code=None, head_code=None,
                 message=None, type=None, data=None):

        self.row = row
        """The row index in the csv file, ie line_no - 1"""

        self.column = column
        """The column in the source line"""

        self.field = field
        """The csv field index"""

        self.rule = rule
        """The ags rule (:ref:`ags4_rules`)"""

        self.group_code = group_code
        """The :term:`GROUP` """

        self.head_code = head_code
        """The :term:`HEADING` """

        self.message = message
        """A quick message"""

        self.data = data
        """The data message"""

    def __repr__(self):
        return "<Problem rule=%s row=%s col=%s m=%s>" % (self.rule, self.row, self.column, self.message)



def summary_to_string(summary):
    #line = "=".repeat(30)
    ret = "" # "=".repeat(30)

    for sum_dic in summary:
        ret += report_to_string(sum_dic)

    return ret

def DEADvalidate_ags4_file(file_path, rules=[]):

    #print "rules=", rules

    doc, err = ogt.ogt_doc.create_doc_from_ags4_file(file_path)
    contents, err = ogt.utils.read_file(file_path)
    if err:
        return None, err

    all_problems = []
    report = {}

    rule_functions =  [
            rule_1, rule_2, rule_3, rule_4, rule_5,
            rule_6, rule_7, rule_8, rule_9, rule_10,


        ]

    def call_func(report, func_to_call):
        func_name = func_to_call.__name__
        report[func_name] = {}
        report[func_name]['problems'], report[func_name]['problems'] = func_to_call(doc)


    if len(rules) > 0:
        print rule_functions
        for ru in rules:
            print ru
            call_func( report, rule_functions[ru - 1] )

    else:
        ## iterate the pointer to  functions
        for rule_func in rule_functions:

            func_name = rule_func.__name__
            report[func_name] = {}
            report[func_name]['problems'], report[func_name]['errors'] = rule_func(doc)
            all_problems.extend(report[func_name]['problems'])

    print "ALLL=", all_problems

    th = ["rule", "row", "col", "field", "data", "message"]
    trs = []
    for p in all_problems:
        #print "p=", p
        tr = []
        tr.append(p.rule if p.rule else "-")
        tr.append(p.row if p.row != None else "-")
        tr.append(p.column if p.column != None else "-")
        tr.append(p.field if p.field != None else "-")
        tr.append(p.data if p.data != None else "-")
        tr.append(p.message if p.message != None else "-")
        trs.append(tr)
    print trs
    all = dict(file_path=file_path, rules=report)

    return all, err

def report_to_string(report):
    print report
    ret = "=" * 50
    ret += "\n%s\n" % report['file_path']
    ret += "-" * 50
    ret += "\n"
    #print report

    for rule, dic in sorted(report['rules'].items()):


        if len(dic['errors']) == 0 and len(dic['problems']) == 0:
            #ret += " PASS\n"
            pass
        else:
            ret += "%s:" % rule.replace("_", " ").capitalize()
            ret += " FAIL\n"


            if len(dic['errors']):
                ret += "\tSystem Errors:\n"
                for item in dic['errors']:
                    ret += "\t\t%s\n" % item


            lp = len(dic['problems'])
            if lp:
                ret += "\tProblem: %s %s\n" % (lp, "item" if lp == 1 else "items")
                for prob in dic['problems']:
                    ret += "\t\t%s\n" % prob

    return ret

def rule_1(doc):
    """ Validate :ref:`www:ags4_rule_1`

    :param raw_str:
    :rtype: tuple
    :return:
        - A list of ags_errors
        - A list of sys_errors
    """
    warnings = []
    errors = []
    try:
        ## try and force to ascii in a one liner
        doc.source.decode("ascii")
        return warnings, errors

    except UnicodeDecodeError:

        #  raw_str has problem somewhere.
        # so split to lines, = line
        # and then check every char in line = column
        # if char fail, we add to errrors
        errors.append("Unicode decode error")
        for lidx, line in enumerate(doc.source.split("\n")):

            #safeS = ""
            for cidx, charlie in  enumerate(line):
                # TODO . check visible.. maybe some < 30 chard are a hacker
                if ord(charlie) < 128:
                    pass
                else:

                    warnings.append(dict(line=lidx+1, column=cidx+1, illegal=[]))
    return warnings, errors

def rule_2(doc):
    """ Validate :ref:`www:ags4_rule_2`

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    problems = []
    #report = []
    errors = []

    RULE = 2

    ## check more than one group
    if doc.groups_count() < 2:
        #report.append("Need more than one group", rule=R)
        p = Problem(message="Need more than one group")
        problems.append( p )

    ## Each data GROUP shall comprise a number of GROUP HEADER
    # TODO


    ## rows must have one or more ref DATA rows
    for group_code, grp in doc.groups.items():
        if len(grp.data) == 0:
            p = Problem(group_code=group_code, rule=RULE)
            problems.append(p)
            #report.append("group `%s` has no DATA rows" % group_code)

    ## Rule 2b - CRLF end each line
    # so we in unix.. so split source with \n and check there's a \r at end
    # can only be done with raw files
    # TODO
    l_rep = []
    if False:
        for idx, line in enumerate( doc.source.split("\n") ):
            print line
            if len(line) > 1:
                  print line[0], ord(line[-1])
            if len(line) > 1 and line[-1] != "\r":
                l_rep.append(line)
        if len(l_rep) > 0:
            #report.append("The following lines do not end with CRLF [%s]" % ", ".join(l_rep))

            p = Problem(rule=RULE)
            p.message = "Lines do not end with CRLF"
            p.data = l_rep
            problems.append(p)

    ## Rule 2c GROUP HEADER
    # loop each group, and check the headers
    l_rep = []
    for group_code, grp in doc.groups.items():

        for idx, dd in enumerate( AGS4_DESCRIPTOR.group_header()):

            if grp.csv_rows()[0] != dd:
                p = Problem(group_code=group_code, row=idx, rule=RULE)

                p.message = "GROUP_HEADER error. "
                p.message += "Incorrect order line "
                problems.append(p)
                #m += " is `%s` and should be `%s` " % (grp.csv_rows[idx][0], dd)
                #l_rep.append(m)

    if len(l_rep):
        pass #report.append(l_rep)



    return problems, errors











EXAMPLES_FILE = os.path.join(PROJECT_ROOT_PATH, "static", "ags4_examples.min.json")
def examples():
    # TODO check dir exists

    data, err = ogt.utils.read_json_file(EXAMPLES_FILE)
    return data, err

def examples_list():
    data, err = ogt.utils.read_json_file(EXAMPLES_FILE)
    if err:
        return None, err
    return [ {"file_name": r['file_name']} for r in data['ags4_examples'] ], None

def example(file_name):

    data, err = examples()
    if err:
        return None, err
    for r in data['ags4_examples']:
        if r['file_name'] == file_name:
            return r, None
    return None, "Example `%s` not found " % file_name

def strip_string(raw_str,  lidx=None, cidx=None, cell=None):
    """Validates and checks a code eg PROJ, """
    err_list = []

    ## Check for whitespace
    strippped = raw_str.strip()
    if strippped != raw_str:
        if strippped == raw_str.lstrip():
            e = OgtError("Leading white space `%s`" % raw_str, warn=True, cidx=cidx, lidx=lidx, cell=None)
            err_list.append(e)
        elif strippped == raw_str.rstrip():
            e = OgtError("Trailing white space `%s`" % raw_str, warn=True, cidx=cidx, lidx=lidx, cell=None)
            err_list.append(e)
        else:
            e = OgtError("White space`%s`" % raw_str, warn=True, cidx=cidx, lidx=lidx, cell=None)
            err_list.append(e)

    return strippped, err_list

def validate_clean_str(raw_code, upper=True, lidx=None, cidx=None):
    """Validates and checks a code eg PROJ, """
    err_list = []

    ## Check for whitespace
    code = raw_code.strip()
    if code != raw_code:
        if code == raw_code.lstrip():
            e = OgtError("Leading white space `%s`" % raw_code, warn=True, cidx=cidx, lidx=lidx)
            err_list.append(e)
        elif code == raw_code.rstrip():
            e = OgtError("Trailing white space `%s`" % raw_code, warn=True, cidx=cidx, lidx=lidx)
            err_list.append(e)
        else:
            e = OgtError("White space`%s`" % raw_code, warn=True, cidx=cidx, lidx=lidx)
            err_list.append(e)

    if upper:
        ucode = code.upper()
        if ucode != code:
            e = OgtError("Contains lower chars `%s`" % code, warn=True, cidx=cidx, lidx=lidx)
            err_list.append(e)

    return ucode, err_list

def validate_upper(raw_str, lidx=None, cidx=None):
    """Validate uppercase """
    err_list = []
    ustr = raw_str.upper()
    if ustr != raw_str:
        e = OgtError("Contains lower chars `%s`" % raw_str, warn=True, cidx=cidx, lidx=lidx)
        err_list.append(e)
    return  ustr, err_list


A2Z = "ABCDEFGHIJKLMNOPQRSTUVWZYZ"
NUMBERS = "0123456789"
CHARS = A2Z + NUMBERS

def validate_a2z(astr):
    """Ensure string contains only A-Z uppercase

    :return: A list of errors
    """
    errs = []
    for idx, char in enumerate(astr):
        if not char in A2Z:
            errs.append(OgtError("Invalid char at position %s `%s`" % (idx+1, astr), rule=19))
    return errs

def validate_descriptor(des, lidx=None, cidx=None, cell=None):
    """Check its case and whether its a data descriptor

    :return: Cleaned descriptor, valid_descroiptor and list of errors

    """

    # check upper
    up_des, errs = validate_upper(des)

    # check only a2z
    cerrs = validate_a2z(up_des)
    if cerrs:
        errs.extend(cerrs)

    # check it a description
    if up_des in AGS4.descriptors():
        return up_des, True, errs

    errs.append( OgtError("Invalid descriptor `%s` " % des, warn=True, cidx=cidx, lidx=lidx, rule=3))
    return up_des, False, errs


def validate_group_str(group_code, lidx=None, cidx=None):
    """Rule 19 Group Heading"""

    # first check length for empty
    lenny = len(group_code)
    if lenny == 0:
        # no group code so get outta here
        return group_code, [OgtError("Invalid GROUP, needs one char at least `%s`" % group_code,
                         cidx=cidx, lidx=lidx, rule=19)]

    # check upper
    group_code, errs = validate_upper(group_code)

    if lenny > 4:
        errs.append( OgtError("Invalid GROUP, longer then four chars `%s`" % group_code, cidx=cidx, lidx=lidx, rule=19))

    # check characters are valid
    errs = []
    for idx, char in enumerate(group_code):
        if char in A2Z or char in NUMBERS:
            # ok
            pass
        else:
            errs.append(OgtError("Invalid char in  GROUP position %s `%s`" % (idx+1, group_code), cidx=cidx, lidx=lidx, rule=19))

    return group_code, errs


def validate_heading_str(head_code, lidx=None, cidx=None):
    """Checks the heading is valid
    - cleaned code
    - whether fatal
    - errors list
    """

    head_code, errs = validate_upper(head_code)

    if not "_" in head_code:
        errs.append( OgtError("Invalid HEADING requires a _ `%s` not found" % head_code, cidx=cidx, lidx=lidx))
        # cannot continue ??
        return head_code, True, errs

    ## split the heading into group + remainder
    group_code, head_part = head_code.split("_")

    # validate the group part
    group_code, errs = validate_group_str(group_code, lidx=lidx, cidx=cidx)
    if len(errs) > 0:
        # assume we cannot continue
        return group_code, True, errs

    if len(head_code) > 9:
        errs.append(OgtError("Invalid HEADING > 9 chars `%s`" % head_code, cidx=cidx, lidx=lidx, rule="19a"))

    if len(head_code) == 0:
        errs.append(OgtError("Invalid HEADING needs at least one char `%s`" % head_code,  cidx=cidx, lidx=lidx, rule="19a"))

    return head_code, False, errs

def validate_heading_ags(head_code, group_code_in, lidx=None, cidx=None):
    """Check the heading is in ags data dict. This is done by
         - First check if the heading is in the group (eg SPEC_*)
         - Then split the HEAD_ING and check the group and the heading in theat group

    """
    # first get the group that this heading is in
    # check group exists
    grpdic = AGS4.group(group_code_in)

    if grpdic == None:
        return OgtError("Invalid GROUP `%s` for HEADING `%s`, not in ags data dict" % (group_code_in,head_code), cidx=cidx, lidx=lidx, rule="9")

    heads = grpdic.get("headings")
    for h in heads:
        if head_code == h['head_code']:
            # Yipee, the head_code is in the origin group
            return None

    # split the head code amd check source group + heading i that group

    sgroup_code, _ = head_code.split("_")

    # check group exists
    grpdic = AGS4.group(sgroup_code)

    if grpdic == None:
        return OgtError("Invalid GROUP part of HEADING not in ags data dict `%s`" % head_code, cidx=cidx, lidx=lidx, rule=9)

    heads = grpdic.get("headings")
    for h in heads:
        if head_code == h['head_code']:
            return None
    return OgtError("HEADING `%s` not found in GROUP `%s`" % (head_code, sgroup_code), warn=True, cidx=cidx, lidx=lidx, rule=9)


def validate_type_ags(typ, lidx=None, cidx=None):

    types = AGS4.types_dict()
    if types.has_key(typ):
        return None

    return OgtError("TYPE `%s` not ing AGS4 " % (typ), cidx=cidx, lidx=lidx, rule="TODO")


def validate_headings_sort(group_code, heading_codes, cidx=None, lidx=None):

    # get ags headings list for group
    ags_headings = AGS4.headings_index(group_code)
    if ags_headings == None:
        return

    plst = []
    for ags_head in ags_headings:
        if ags_head in heading_codes:
            plst.append(ags_head)
        #else:
        #    plst.append(None)
    if plst == heading_codes:
        return None

    clst = []
    cidxs = []
    print "----------------------"
    print plst
    print heading_codes
    for idx, c in enumerate(plst):
        if c == None:
            continue
        if heading_codes[idx] != c:
            clst.append(c)
            cidxs.append(idx + 1)
    if len(clst) == 0:
        return None
    errs = []
    for idx, cidx in enumerate(cidxs):
        errs.append( OgtError("Headings order incorrect, should be `%s` cols %s " % (",".join(clst), ",".join([str(c) for c in cidxs])),
                              lidx=lidx, cidx=cidx, rule=9))








    return errs
