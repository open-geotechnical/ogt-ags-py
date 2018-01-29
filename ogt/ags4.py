
import os
import io
from operator import itemgetter
import urllib, urllib2
import json

from ogt import USER_TEMP, OgtError
import ogt.ogt_doc
import ogt.utils
#from ogt import utils, EXAMPLES_DIR

def ags4dd_file():
    """
    :return: str with path to the `ags4.min.json` data dict file
    """
    return os.path.join(USER_TEMP, "ags4.min.json")



class AGS4_DataDict:
    """This dict contains all the ags4 data, loaded in initialise()"""

    GROUP = "GROUP"
    HEADING = "HEADING"
    UNIT = "UNIT"
    TYPE = "TYPE"
    DATA = "DATA"


    def __init__(self):

        self._data = None
        self._groups = None
        self._abbrs = None
        self._types = None
        self._units = None

        self._types_lookup_cache = None

        self.initialise()

    def update(self):
        """Downloads data dict file from online

        :return: An error if one occured,  else None
        """
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



    def initialise(self):
        """Check env is sane and loads the ags data dict file"""
        if not os.path.exists(USER_TEMP):
            os.makedirs(USER_TEMP)

        if not os.path.exists(ags4dd_file()):
            return "Missing ags4 data dict"

        self._data, err = ogt.utils.read_json_file(ags4dd_file())
        #print self._data.keys()
        if err:
            return err

        self._abbrs = self._data['abbrs']
        self._groups = self._data['groups']
        self._types = self._data['data_types']
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
            dic[t['data_type']] = t['description']
        return dic


    def units_list(self):
        return self._units

    def picklist(self, head_code):
        return self._abbrs.get(head_code).get("abbrs")

    def deaddata_types(self):
        return self._data_types



    def type(self, abbr_code):
        if self._types_lookup_cache == None:
            self._types_lookup_cache = {}
            #typs = AGS4_DD.get("data_types")
            #print self._data_types
            for typ in self._types:
                #print "typ=", typ
                self._types_lookup_cache[typ['data_type']] = typ
        return self._types_lookup_cache.get(abbr_code)

    @staticmethod
    def descriptors():
        """Returns a list of descriptors  in correct order rule_3"""
        return [
            AGS4_DataDict.GROUP, AGS4_DataDict.HEADING, AGS4_DataDict.UNIT, AGS4_DataDict.TYPE, AGS4_DataDict.DATA
        ]


    def headings(self, group_code):

        if not group_code in self._groups:
            return None

        return self._groups.get("headings")

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
            AGS4_DESCRIPTOR.group,
            AGS4_DESCRIPTOR.heading,
            AGS4_DESCRIPTOR.unit,
            AGS4_DESCRIPTOR.type
        ]

    @staticmethod
    def list():
         return AGS4_DESCRIPTOR.group_header() + [AGS4_DESCRIPTOR.data]




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

def run_tests(rules):
    """Run tests on files in ags4_tests/

    :param rules: A list of test to run eg [7 8 9]. Empty = all
    :type rule: list of int's
    :rtype: tuple
    :return:

        - A list of ags errors
        - A list of system errors
    """


    files, err = ogt.utils.list_examples("ags4_tests")
    if err:
        return None, err

    summary = []
    for ags_file in files:
        #print "-----------------------"
        print "file=", ags_file
        # print "-----------------------"

        report, err = validate_ags4_file(ags_file)
        print report, err

        summary.append(report)

    s = summary_to_string(summary)
    return s, None

def summary_to_string(summary):
    #line = "=".repeat(30)
    ret = "" # "=".repeat(30)

    for sum_dic in summary:
        ret += report_to_string(sum_dic)

    return ret

def validate_ags4_file(file_path, rules=[]):

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


def rule_3(descriptor):
    """Validate  :ref:`www:ags4_rule_3`

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    #problems = []
    #report = []
    #errors = []

    #if isinstance()
    descriptor

    #descriptors = AGS.list()
    ## .. TODO
    """
    for lidx, row in enumerate(doc.csv_rows):
        if len(row) > 0:
            if row[0] not in descriptors:
                #report.append("Invalid descriptor `%s` line %s has " % (row[0], lidx+1))
                p = Problem(row=lidx)
                p.message = "Invalid descriptor"
                p.data = row[0]
                problems.append(p)

    return problems, errors
    """

def rule_4(doc):
    """Validate  :ref:`www:ags4_rule_4`

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


    ## The GROUP row contains only one DATA item, the GROUP name, in addition to the Data
    for idx, row in enumerate(doc.csv_rows):
        lenny = len(row)
        if lenny > 0:

            if row[0] == AGS4_DESCRIPTOR.group:
                if lenny != 2:
                    g = "?" if lenny == 1 else row[1]
                    p = Problem(group_code=g, row=idx)
                    p.message = "Group descriptor has %s items, should be one" % idx + 1
                    problems.append(p)
                    #report.append("Group descriptor `%s` at line %s  has %s items, should be one" % (g, idx + 1, lenny - 1))


    # All other rows in the GROUP have a number of DATA items defined by the HEADING row.
    header_len = -1
    for idx, row in enumerate(doc.csv_rows):
        lenny = len(row)
        if lenny == 0:
            # got a blank line
            header_len = -1

        if lenny > 0:
            if row[0] == AGS4_DESCRIPTOR.heading:
                header_len = lenny
            if row[0] == AGS4_DESCRIPTOR.data:
                if header_len != lenny:
                    p = Problem(row=idx)
                    p.message = "DATA field's dont match headers"
                    problems.append(p)
                    #report.append("DATA field's dont match headers at line %s" % (idx + 1))


    return problems, errors

def rule_5(doc):
    """Validate  :ref:`www:ags4_rule_5`

    .. todo:: Rule 5 validation

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    problems = []
    errors = []

    errors.append("TODO - csv double quotes")

    return problems, errors

def rule_6(doc):
    """Validate  :ref:`www:ags4_rule_6`

    .. todo:: Rule 6 validation

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    problems = []
    errors = []

    errors.append("TODO - comma separated")

    return problems, errors

def rule_7(doc):
    """Validate  :ref:`ags4_rule_7`

    .. todo:: Rule 7 Field ordering

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    problems = []
    errors = []

    ## HEADING s shall be in the order described in the AGS4 Data Dictionary
    for group_code, grp in doc.groups.items():

        if grp.data_dict() == None:
            print "--------"
            print group_code
            print "+++++++++"
            #ags_sort = grp.data_dict().headings_sort()

            #print grp.headings_sort
            #sss


    return problems, errors

def rule_8(doc):
    """Validate  :ref:`ags4_rule_8`

    .. todo:: Rule 8 Units

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    problems = []
    errors = []

    return problems, errors

def rule_9(doc):
    """Validate  :ref:`ags4_rule_9`

    .. todo:: Rule 9 Data Dictionary

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    problems = []
    errors = []

    return problems, errors

def rule_10(doc):
    """Validate  :ref:`ags4_rule_10`

    .. todo:: Rule 10 validation

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    problems = []
    errors = []

    return problems, errors


def examples():
    # TODO check dir exists
    pth =  os.path.join(USER_TEMP, "ags4_examples.min.json")
    data, err = ogt.utils.read_json_file(pth)
    return data, err

def examples_list():
    # TODO check dir exists
    pth =  os.path.join(USER_TEMP, "ags4_examples.min.json")
    data, err = ogt.utils.read_json_file(pth)
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

"""
def get_example_dirs():
    if not os.path.exists(EXAMPLES_DIR):
        return None, "dir '%s' not exist " % EXAMPLES_DIR
    return sorted(os.listdir(EXAMPLES_DIR)), None
"""

def validate_code(raw_code, lidx=None, cidx=None):
    """Validates adn checks a code eg PROJ, """
    err_list = []

    ## Check for whitespace
    code = raw_code.strip()
    if code != raw_code:
        if code == raw_code.lstrip():
            e = OgtError("Leading white Space `%s`" % raw_code, error=False, cidx=cidx, lidx=lidx)
            err_list.append(e)
        elif code == raw_code.rstrip():
            e = OgtError("Trailing white Space `%s`" % raw_code, error=False, cidx=cidx, lidx=lidx)
            err_list.append(e)
        else:
            e = OgtError("White Space`%s`" % raw_code, error=False, cidx=cidx, lidx=lidx)
            err_list.append(e)

    ucode = code.upper()
    if ucode != code:
        e = OgtError("Lower space characters `%s`" % code, error=False, cidx=cidx, lidx=lidx)
        err_list.append(e)

    return ucode, err_list

def validate_descriptor(des, lidx=None, cidx=None):
    """Check its one of GROUP, UNIT, DATA, etc"""
    if des in AGS4.descriptors():
        return None
    return OgtError("Invalid descriptor `%s` not found" % des, error=True, cidx=cidx, lidx=lidx)

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWZYZ"
NUMBERS = "0123456789"
CHARS = A2Z + NUMBERS

def validate_group_str(group_code, lidx=None, cidx=None):
    """Rule 19 Group Heading"""

    # first check lengths
    lenny = len(group_code)
    if lenny == 0:
        # no group code so get outta here
        return [OgtError("Invalid GROUP, needs one char at least `%s`" % group_code,
                         error=True, cidx=cidx, lidx=lidx, rule=19)]

    if lenny > 4:
        return [OgtError("Invalid GROUP, longer then four chars `%s`" % group_code, error=True, cidx=cidx, lidx=lidx, rule=19)]


    # check characters are valid
    errs = []
    for idx, char in enumerate(group_code):
        if char in A2Z or char in NUMBERS:
            # ok
            pass
        else:
            errs.append(OgtError("Invalid char in  GROUP position %s `%s`" % (idx+1, group_code), error=True, cidx=cidx, lidx=lidx, rule=19))
    if len(errs) > 0:
        return errs

    return []


def validate_heading_str(head_code, lidx=None, cidx=None):
    """Checks the heading is valid"""
    errs = []
    if not "_" in head_code:
        errs.append( OgtError("Invalid HEADING requires a _ `%s` not found" % head_code, error=True, cidx=cidx, lidx=lidx))
        # cannot continue ??
        return errs

    ## split the heading into group + remainder
    group_code, head_part = head_code.split("_")

    # validate the group part
    errs = validate_group_str(group_code, lidx=lidx, cidx=cidx)
    if len(errs) > 0:
        # assume we cannot continue
        return errs

    if len(head_code) > 9:
        return [OgtError("Invalid HEADING > 9 chars `%s`" % head_code,
                     error=True, cidx=cidx, lidx=lidx, rule="19a")]
    if len(head_code) == 0:
        return OgtError("Invalid HEADING needa at least onc char `%s`" % head_code, error=True, cidx=cidx, lidx=lidx, rule="19a")

    return None

def validate_heading_ags(head_code, lidx=None, cidx=None):
    """Check the heading is in ags data dict"""

    group_code, _ = head_code.split("_")

    # check group exists
    grpdic = AGS4.group(group_code)

    if grpdic == None:
        return OgtError("Invalid GROUP part of HEADING not in ags data dict `%s`" % head_code, error=True, cidx=cidx, lidx=lidx, rule="9")

    heads = grpdic.get("headings")
    for h in heads:
        if head_code == h['head_code']:
            return None
    return OgtError("HEADING `%s` not found in GROUP `%s`" % (head_code, group_code), error=True, cidx=cidx, lidx=lidx, rule="9")


