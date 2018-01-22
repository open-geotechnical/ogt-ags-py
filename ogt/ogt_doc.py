# -*- coding: utf-8 -*-

import os
import csv
import StringIO
import hashlib
import zipfile

from . import HAVE_GEOJSON
if HAVE_GEOJSON:
    import geojson
    import bng_to_latlon # https://github.com/fmalina/bng_latlon

from . import FORMATS
import ogt.ags4
import ogt.ogt_group
import ogt.utils


class OGTDocumentOptions:

    def __init__(self):

        self.minify = False
        """Option whether to minify output Json only"""

        self.xmode = True
        """Option to `extend` output and not just the data"""

        self.include_stats = False
        """Stats such as groups, row count etc"""

        self.include_source = False
        """Includes 'source'  and 'source_cells' in output """

        #self.include_source = False
        """Includes 'source'  and 'source_cells' in output """

    def __repr__(self):
        return "<OGTDocOpts xmode=%s, mini=%s>" % (self.xmode, self.minify)

class OGTDocument:
    """Class :class:`~ogt.ogt_doc.OGTDocument` represents an ags file and
    contains the groups (:class:`~ogt.ogt_group.OGTGroup`).

    .. code-block:: python

        from ogt import ogt_doc

        doc = ogt_doc.OGTDocument()
        err = doc.load_ags4_file("/path/to/my.ags")
        if err:
            print err
        else:
            # print the groups index
            print doc.groups_index()

            # Headings in the SAMP group
            print doc.group("SAMP").headings()

            # Return a list of units used in the document
            print doc.units()

    """

    def __init__(self):

        self.source_file_path = None
        """Full path to original source file, if any"""

        self.source = ""
        """The original source files contents as string"""

        self.groups = {}
        """A `dict` of group code to :class:`~ogt.ogt_group.OGTGroup` instances"""

        self.lines = []
        """A `list` of strings with original source lines"""

        self.csv_rows = []
        """A `list` of a list of csv rows"""

        self.error_rows = {}
        """A `list` of rows with errors"""

        self.opts = OGTDocumentOptions()
        """Set default options :class:`~ogt.ogt_doc.OGTDocumentOptions` """



    def hash(self):
        """Calculate the `sha1` hash

        :rtype: str
        :return: A **`str`** with the hash

        .. seealso:: See also

            - https://en.wikipedia.org/wiki/SHA-1
            - https://docs.python.org/2/library/sha.html
        """
        hasher = hashlib.sha1()
        hasher.update(self.source)
        return hasher.hexdigest()

    def groups_sort(self):
        """Return a list of group_codes in preferred order (see :func:`~ogt.ogt_group.groups_sort`)"""
        return ogt.ogt_group.groups_sort(self.groups.keys())


    def groups_count(self):
        """Returns no of groups in document

        :rtype: int
        :return: Groups count
        """
        return len(self.groups.keys())

    def append_group(self, grp):
        """Appends an :class;`~ogt.ogt_group.OGTGroup` instance to this document

        :param grp: The group object to add
        :type grp: ~ogt.ogt_group.OGTGroup
        :return: An `Error` message is group exists, else `None`
        """
        if grp.group_code in  self.groups:
            return "Error: Group already exists in doc"
        grp.docParent = self
        #self.groups_sort.append(grp.group_code)
        self.groups[grp.group_code] = grp
        return None

    def group(self, group_code):
        """
        :param group_code: Four character group code
        :type group_code: str
        :return: An instance of :class:`~ogt.ogt_group.OGTGroup` if exists, else `None`
        """

        return self.groups.get(group_code)


    def proj(self):
        """Shortcut to `PROJ` group object

        :return: An instance of :class:`~ogt.ogt_group.OGTGroup` if exists, else `None`
        """
        return self.group("PROJ")

    def proj_dict(self):
        """Shortcut to `PROJ` group data

        :return: A dict with data if exists, else `None`
        """
        grpOb = self.group("PROJ")
        if not grpOb:
            return None
        #print grpOb.data[0]
        if len(grpOb.data) > 0:
            return grpOb.data[0]
        return None

    def units(self):
        """Shortcut to `UNIT` group

        :rtype: tuple
        :return:
            - An instance of :class:`~ogt.ogt_group.OGTGroup` if exists, else `None`
            - `bool` = `True` if group found in document, else false
        """
        return self.group("UNIT")

    def types(self):
        """Shortcut to `TYPE` group

        :rtype: tuple
        :return:
            - An instance of :class:`~ogt.ogt_group.OGTGroup` if exists, else `None`
            - `bool` = `True` if group found in document, else false
        """
        return self.group("TYPE")

    def write(self, ext="json", beside=False, file_path=None,
              zip=False, overwrite=False):
        """Write out the data to file in the selected format

        :param ext: The file format, see :data:`~ogt.__init__.FORMATS`
        :type ext: str

        :type beside: bool
        :param beside: Save the output file alongside the original with extention appended, eg

             - Source = `/path/to/myproject.ags`
             - Output = `/path/to/myproject.ags.json`

        :param file_path: Relative or absolute path to write to including extention
        :type file_path: str

        :param include_source: If `True`, the original ags source is also included.
        :type include_source: bool

        :param zip: If `True`, the original and converted file are packaged in a zip
        :type zip: bool

        :param minify: If `True`, all white space is removed from output file
        :type minify: bool

        :param overwrite: If `True`, the target file is overwritten, otherwise an error is returned
        :type overwrite: bool

        :return: A tuple with

                - A `Message` string  if no errors, else `None`
                - Any `Error` that occured, otherwise `None`

        .. Note:: **Note**

            - Either **`beside=True`** or a **`file_path`** is required, otherwise and error occurs
            - If both are provided, and error is returned

        """
        #print "----------------"
        stats = self.stats()['site_geometry']
        #print ".................."

        ## Do some validations
        if not ext in FORMATS:
            return None, "Error: Invalid format specified - `%s` % ext. Use %s" % ",".join(FORMATS)

        if beside == False and file_path == None:
            return None, "Error: need an output, either -b or -w"

        if beside == True and file_path != None:
            return None, "Error: conflict in options, either -b or -w, not BOTH"


        ## make target filename's
        base_name = os.path.basename(self.source_file_path)
        target_file_path = None
        if beside:
            # File is beside the original
            if zip:
                target_file_path = self.source_file_path + ".zip"

            else:
                target_file_path = self.source_file_path + ".%s" % ext

        else:
            # file is from argument
            target_file_path = file_path
            base_name = os.path.basename(file_path)
            if len(base_name) == 0:
                # directory given only
                return None, "Error: Invalid file name `%s`" % target_file_path

            parts = base_name.split(".")
            if len(parts) == 1:
                # no extention
                return None, "Error: Invalid file name `%s`" % target_file_path

            # Check the extention is what we expect
            gext = parts[-1]
            if zip == False and gext != ext:
                return None, "Error: Conflict in file name extention, expected '%s' `%s`" % (ext, target_file_path)

            elif zip == True and gext != "zip":
                # extentions mismatched eg json != yaml
                return None, "Error: Conflict in file name extention expected 'zip' `%s`" % target_file_path


        ## warn if not overwrite
        if overwrite == False:
            if os.path.exists(target_file_path):
                return None, "Error: Target file exists - `%s` " % target_file_path

        ## convert the file to target format string blob
        blob = None
        err = None
        if ext in ["js", "json"]:
            blob, err = self.to_json()

        elif ext == "geojson":
            blob, err = self.to_geojson()

        elif ext == "yaml":
            blob, err = self.to_yaml(include_source=include_source, edit_mode=edit_mode, include_stats=include_stats)

        elif ext == "ags4":
            blob, err = ogt.ags.ags4.doc_to_ags4_csv(self)

        else:
            return None, "Error: No valid output format specified - `%s` % ext"

        if err:
            return None, err

        if zip:
            # create zip
            try:
                zipee = zipfile.ZipFile(target_file_path, mode="w")

                # add source file
                zipee.writestr( base_name, self.source)

                # add converted file
                zipee.writestr( "%s.%s" % (base_name, ext), blob)

                # write out and done
                zipee.close()

                siz = ogt.utils.file_size(target_file_path, human=True)
                return "Wrote: %s `%s`" % (siz, target_file_path), None

            except Exception as e:
                return None, "Error: %s" % str(e)



        else:
            try:
                with open(target_file_path, "w") as f:
                    f.write(blob)
                    f.close()
                siz = ogt.utils.file_size(target_file_path, human=True)
                return "Wrote: %s `%s`" % (siz, target_file_path), None

            except Exception as e:
                return None, "Error: %s" % str(e)


        return None, "Error: OOPS unexpected error"

    def to_dict(self):
        """Return the document data

        :param include_source: if `True` then the source string is included in the **source:** key.
        :type include_source: bool
        :param edit_mode: see :ref:`edit_mode`
        :type edit_mode: bool
        :rtype: dict
        :return: A `dict` with the data
        """
        # base dict to return
        dic =  dict(file_name=self.source_file_path,
                    version="ags4",
                    groups={},
                    hash=self.hash())

        # loop groups and add struct based on edit_mode
        for k, g in self.groups.iteritems():
            dic['groups'][k] = g.to_dict()

        # include source raw source
        if self.opts.include_source:
            dic['source'] = self.source
            dic['source_cells'] = self.csv_rows

        # include statistics
        if self.opts.include_stats:
            dic['stats'] = self.stats()
        return dic

    def to_json(self): #, include_source=False, edit_mode=False, minify=False, include_stats=False):
        """Return the document data in :ref:`json` format

        :param include_source: if `True` then the source string is included in the **source:** key.
        :type include_source: bool
        :param edit_mode: see :ref:`edit_mode`
        :type edit_mode: bool
        :rtype: str
        :return: A tuple with:

                - `None` if error else a `str` with :ref:`json` encoded data
                - An `error` string is error occured, else `None`
        """

        return ogt.utils.to_json( self.to_dict(), minify=self.minify)



    def to_yaml(self, include_source=False, edit_mode=False, include_stats=False):
        """Return the document data in :ref:`yaml` format

        :param include_source: if `True` then the source string is included in the **source:** key.
        :type include_source: bool
        :param edit_mode: see :ref:`edit_mode`
        :type edit_mode: bool
        :rtype: str
        :return: A tuple with:

                - `None` if error else a `str` with :ref:`yaml` encoded data
                - An `error` string is error occured, else `None`
        """
        return ogt.utils.to_yaml( self.to_dict(include_source=include_source,
                                           include_stats=include_stats,
                                           edit_mode=edit_mode) )


    def to_geojson(self, minify=False):

        loca = self.group("LOCA")
        if loca == None:
            return None, "No `LOCA` Group"

        def make_feature(rec, lat, lon):
            props = dict(PointID=rec.get("LOCA_ID"), Type=rec.get("LOCA_TYPE"), GroundLevel=rec.get("LOCA_GL"))
            return geojson.Feature(geometry=geojson.Point((lon, lat)), properties=props)


        features = []

        ## WSG84
        if "LOCA_LAT" in loca.headings and "LOCA_LON" in loca.headings:
            for rec in loca.data:
                lat_s = rec.get("LOCA_LAT")
                lon_s = rec.get("LOCA_LON")
                if lat_s and lon_s:
                    features.append(make_feature(rec, lat_s, lon_s))

        ## BNG British National grid
        elif "LOCA_NATE" in loca.headings and "LOCA_NATN" in loca.headings:
            for rec in loca.data:
                east = ogt.utils.to_int(rec.get("LOCA_NATE"))
                north = ogt.utils.to_int(rec.get("LOCA_NATN"))
                if east and north:
                    lat, lon = bng_to_latlon.OSGB36toWGS84(east, north)
                    features.append(make_feature(rec, lat, lon))
                print rec
        print "ere", features
        if len(features) > 0:
            f = geojson.FeatureCollection(features)
            print f
            print ogt.utils.to_json(f, minify=minify)
            return ogt.utils.to_json(f, minify=minify)
        return None, None

    def write_excel(self):
        """Experimental writing to xlsx"""
        wbook = openpyxl.Workbook()

        for idx, ki in enumerate(self.groups_sort):
            grpobj = self.groups_sort[ki]
            if idx == 0:
                ## By default an empty workbook has a first sheet
                sheet = wbook.active
                sheet.title = ki
            else:
                sheet = wbook.create_sheet(title=ki)
        # DAMN this is where groups order goes mad

        wbook.save(self.file_path + ".xlsx")



    def stats(self):

        dic = {}

        ## Number of locations
        locaGrp = self.group("LOCA")
        if locaGrp == None:
            dic['locations'] = None
        else:
            recs =  locaGrp.data_column("LOCA_ID")
            dic['locations'] = dict(count=len(recs), data=recs)

        ## Data rows
        lst = []
        for gc in sorted(self.groups.keys()):
            grp = self.group(gc)
            lst.append(dict(GROUP=gc, count=len(grp.data)))
        dic['data'] = lst

        ## Sample Types
        grp = self.group("SAMP")
        if not grp:
            dic['sample_types'] = None
        else:
            d = {}
            recs =  grp.data_column("SAMP_TYPE")
            for st in sorted(recs):
                if not st in d:
                    d[st] = 0
                d[st] += 1
            dic['sample_types'] = d


        ## Site Geom
        d = {}
        # TODO X.Y.Z
        d['LOCA_LOCX'] = "todo"
        d['LOCA_LOCY'] = "todo"
        d['LOCA_LOCZ'] = "todo"

        # National Grid
        def calc_ng_stats(recs):
            # TODO - need to check type casting ?
            if recs == None:
                return None
            ds = {}
            ds['min'] = min(recs)
            ds['max'] = max(recs)
            ds['row_count'] = len(recs)
            ds['rows_with_data'] = 0
            ds['rows_without_data'] = 0
            for rec in recs:
                if rec == "":
                    ds['rows_without_data'] += 1
                else:
                    ds['rows_with_data'] += 1
            return ds


        recs = locaGrp.data_column("LOCA_NATE")
        d['LOCA_NATE'] = calc_ng_stats(recs)

        recs = locaGrp.data_column("LOCA_NATN")
        d['LOCA_NATN'] = calc_ng_stats(recs)

        recs = locaGrp.data_column("LOCA_GL")
        d['LOCA_GL'] = calc_ng_stats(recs)

        dic['site_geometry'] = d

        # GEOL
        grp = self.group("GEOL")
        if not grp:
            dic['geol'] = None
        else:
            recs = grp.data_column("LOCA_ID")
            locs = dic['locations']['data']
            ll = []
            for l in locs:
                if not l in recs:
                    if not l in ll:
                        ll.append(l)
            dic['geol'] = dict(no_entries=ll if len(ll) > 0 else None)

        # SAMP
        grp = self.group("SAMP")
        if not grp:
            dic['samp'] = None
        else:
            recs = grp.data_column("LOCA_ID")
            locs = dic['locations']['data']
            ll = []
            for l in locs:
                if not l in recs:
                    if not l in ll:
                        ll.append(l)
            dic['samp'] = dict(no_entries=ll if len(ll) > 0 else None)


        ## Unused Groups
        all_g = ogt.ags4.groups()
        dic['unused_groups'] = None
        ags_groups = all_g.keys()
        dic['unused_groups'] = sorted(list( set(ags_groups) - set(self.groups.keys())))

        return dic



    def load_ags4_file( self, ags4_file_path):
        """Loads document from an :term:`ags4` formatted file

        :param ags4_file_path: absolute or relative path to file, will be at source_file_path
        :type ags4_file_path: str
        :rtype: str
        :return: A String if an error else None

        .. todo:: Ensure we can read ascii
        """
        try:
            # TODO ensure asccii ??
            self.source_file_path = ags4_file_path
            with open(ags4_file_path, "r") as f:
                err =  self.load_ags4_string(  f.read() )
                if err:
                    return err
                return None

        except IOError as e:
            return None,  e

        # should never happen
        return  "WTF in `load_ags4_file`"



    def load_ags4_string(self, ags4_str):
        """Load  document from an :term:`ags4` formatted string

        Hackers guide
        This is a tthree step parsing process.
        -


        :param ags4_str: string to load
        :type ags4_str: str
        :rtype: str
        :return: An `Error` message if string not loaded, else `None`
        """




        ## Copy source as a string into mem here
        self.source = ags4_str

        # first:
        #  - split ags_string into lines
        #  - and parse each line into csv
        #  - and add to the doc
        for lidx, line in enumerate(self.source.split("\n")):

            # removing and trailing whitespace eg \r
            # were on nix land, so assemble with CRLF when dumping to ags
            stripped = line.strip()

            if stripped == "":
                # blank line
                self.lines.append([])
                self.csv_rows.append([])
                continue

            # decode the csv line
            reader = csv.reader( StringIO.StringIO(stripped) )
            row =  reader.next() # first row of reader

            self.lines.append(line)
            self.csv_rows.append(row)

        # second
        # walk the decoded rows, and recognise the groups
        # me mark the start_index, and end index of group
        curr_grp = None
        for lidx, row in enumerate(self.csv_rows):

            line_no = lidx + 1
            lenny = len(row)
            #print row
            if lenny == 0:
                # blank row so reset groups
                if curr_grp:
                    curr_grp.csv_end_index = lidx
                    #print "idx=", curr_grp.csv_start_index, curr_grp.csv_end_index
                    #print curr_grp.csv_rows()
                curr_grp = None
                continue

            if lenny < 2:
                # min of two items, so add to errors
                self.error_rows[lidx + 1] = row

            else:
                typ = row[0] # first item is row type
                #xrow = row[1:] # row without data descriptor

                if typ == ogt.ags4.AGS4_DESCRIPTOR.group:

                    ## we got a new group
                    curr_grp = ogt.ogt_group.OGTGroup(row[1])
                    #curr_grp.csv_rows.append(row)
                    curr_grp.csv_start_index = lidx
                    self.append_group(curr_grp)

                else:
                    if curr_grp == None:
                        self.error_rows[line_no] = row
                    #else:
                    #   curr_grp.csv_rows.append(row)
        # thirdly
        # - we parse each group's csv rows into the parts
        for group_code, grp in self.groups.items():
            #print group_code, "<<<<<<<<<"
            #print grp.csv_rows()

            for idx, row in enumerate(grp.csv_rows()):
                typ = row[0]
                xrow = row[1:] # row without data descriptor

                if typ == ogt.ags4.AGS4_DESCRIPTOR.group:
                    pass

                elif typ == ogt.ags4.AGS4_DESCRIPTOR.heading:
                    grp.headings_source_sort = xrow
                    for idx, head_code in enumerate(grp.headings_source_sort):
                        grp.headings[head_code] = xrow[idx]

                elif typ == ogt.ags4.AGS4_DESCRIPTOR.unit:
                    if grp.headings_source_sort == None:
                        self.error_rows[line_no] = row
                    else:
                        for idx, head_code in enumerate(grp.headings_source_sort):
                            grp.units[head_code] = xrow[idx]

                elif typ == ogt.ags4.AGS4_DESCRIPTOR.type:
                    if grp.headings_source_sort == None:
                        self.error_rows[line_no] = row
                    else:
                        for idx, head_code in enumerate(grp.headings_source_sort):
                            grp.types[head_code] = xrow[idx]

                elif typ == ogt.ags4.AGS4_DESCRIPTOR.data:

                    if grp.headings_source_sort == None:
                        self.error_rows[line_no] = row
                    else:
                        dic = {}
                        for idx, head_code in enumerate(grp.headings_source_sort):
                            dic[head_code] = xrow[idx]
                        grp.data.append( dic )

        print self.error_rows

        return  None


def create_doc_from_ags4_file(ags_file_path):
    """Convenience function to create and load an OGTDocument from an ags file

    .. code-block:: python

        doc, err = ogt_doc.create_doc_from_ags4_file("/path/to/my.ags")
        if err:
            print err
        else:
            print doc.group("PROJ")
    """
    doc = OGTDocument()
    err = doc.load_ags4_file(ags_file_path)
    return doc, err

def create_doc_from_ags4_string(ags4_string):
    """Convenience function to create and load an OGTDocument from an ags string

    .. code-block:: python

        doc, err = ogt_doc.create_doc_from_ags4_string(ags4_string)
        if err:
            print err
        else:
            print doc.group("PROJ")
    """
    doc = OGTDocument()
    err = doc.load_ags4_string(ags4_string)
    return doc, err

def create_doc_from_json_file( json_file_path):
    """Creates a document from a :ref:`json` formatted file

    .. code-block:: python

        doc, err = ogt_doc.create_doc_from_json_file("/path/to/my.json")
        if err:
            print err

    :param json_file_path: absolute or relative path to file
    :type json_file_path: str
    :rtype: tuple
    :return: A `tuple` containing

        - An :class:`~ogt.ogt_doc.OGTDocument` object on success, else `None`
        - An `Error` message if error, otherwise `None`
    """
    data, err = ogt.utils.read_json_file(json_file_path)
    if err:
        return None, err

    groups = data.get('groups')
    if groups == None:
        return None, "Error: no `groups` key in json file"

    doc = ogt.ogt_doc.OGTDocument()
    doc.source_file_path = json_file_path

    for group_code in groups.keys():

        group = groups[group_code]

        grp = ogt.ogt_group.OGTGroup(group_code)
        doc.append_group(grp)

        ## add units + also headings
        for head_code  in group['UNIT'].keys():
            valu = str(group['UNIT'][head_code])
            grp.units[head_code] = valu
            grp.headings[head_code] = valu

        ## add TYPE
        for head_code  in group['TYPE'].keys():
            valu = str(group['TYPE'][head_code])
            grp.types[head_code] = valu

        ## add data
        for rec  in group['DATA']:
            dic = {}
            for head_code  in rec.keys():

                dic[head_code] = str(rec[head_code])

            grp.data.append(dic)


    return doc, None

