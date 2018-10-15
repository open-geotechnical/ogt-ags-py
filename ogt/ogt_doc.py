# -*- coding: utf-8 -*-

import os
import csv
import StringIO
import hashlib
import zipfile

from . import HAVE_GEOJSON, HAVE_BNG_LATLON
if HAVE_GEOJSON:
    import geojson

if HAVE_BNG_LATLON:
    import bng_to_latlon # https://github.com/fmalina/bng_latlon

from . import FORMATS, OgtError, CELL_COLORS
import ags4
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
        #"""Includes 'source'  and 'source_cells' in output """

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

        self.source_string = ""
        """The original source files contents as string
            TODO: need to sort out utf8 vs ascii vs windows characters
        """

        self.groups_list = []
        """A `dict` of group code to :class:`~ogt.ogt_group.OGTGroup` instances"""

        self.lines = []
        """A `list` of strings with original source lines"""

        self.csv_rows = []
        """A `list` or `list` of each csv value"""

        self.error_cells = {}
        """A `dict` of row/col indexes with errors"""

        self.opts = OGTDocumentOptions()
        """Set default options :class:`~ogt.ogt_doc.OGTDocumentOptions` """

        self.cells = []



    #def deadcells(self):
    #    return self._csv_cells

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
        return groups_sort(self.groups.keys())

    def groups_list(self):
        lst = []
        for grp_code in self.groups_sort():
            lst.append(self.groups.get(grp_code))
        return lst

    def group_from_index(self, ridx):
        return self.groups_list[ridx]

    def groups_count(self):
        """Returns no of groups in the document

        :rtype: int
        :return: Groups count
        """
        return len(self.groups_list)

    def add_group(self, rows, lidx):
        """Appends an :class;`~ogt.ogt_group.OGTGroup` instance to this document

        : TODO:  decide what to do with dupes.. append or keep both says pedor ?

        :param grp: The group object to add
        :type grp: ~ogt.ogt_group.OGTGroup
        :return: An `Error` message is group exists, else `None`
        """
        #if ogtGroup.group_code in  self.groups:
        #    return "Error: Group already exists in doc"

        gcell = rows[1]
        gcell.value, errs = ags4.validate_group_str(gcell.value)
        gcell.add_errors(errs)
        self.add_errors(errs)

        # create group object and add to doc
        ogtGroup = OGTGroup(ogtDoc=self)
        ogtGroup.set_group(rows, lidx)
        ogtGroup.group_start_lidx = lidx
        self.groups_list.append(ogtGroup)
        return ogtGroup

    def deadgroups(self):
        return self._groups

    def group(self, group_code):
        """
        :param group_code: Four character group code
        :type group_code: str
        :return: An instance of :class:`~ogt.ogt_group.OGTGroup` if exists, else `None`
        """
        for grp in self.groups_list:
            #print grp.group_code, group_code, grp.group_code == group_code
            if grp.group_code == group_code:
                return grp
        return None


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
        if grpOb.data_rows_count(): # should always oen project row
            return grpOb.data_row_dict(0)
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

    def ddtype(self, code):
        #print self.group("TYPE").types
        return "rrr"


    def get_column_data(self, head_code):
        # get the group from eg LOCA_ID
        grp_code = head_code.split("_")[0]
        grp = self.group(grp_code)
        if grp == None:
            return
        return sorted(grp.get_column_data(head_code))

    def add_error(self, er):
        """e = OgtError(message)
        e.lidx = lidx
        e.rule = str(rule)
        if not lidx in self.error_rows:
            self.error_cells[lidx] = {}
        """
        if er == None:
            return
       # print er
        if not er.lidx in self.error_cells:
            self.error_cells[er.lidx] = {}
        if not er.cidx in self.error_cells[er.lidx]:
            self.error_cells[er.lidx][er.cidx] = []

        self.error_cells[er.lidx][er.cidx].append(er)

    def add_errors(self, errs):
        if errs == None:
            return
        if isinstance(errs, OgtError):
            self.add_error(errs)
            return
        if len(errs) == 0:
            return
        for e in errs:
            self.add_error(e)


    def errors(self, lidx=None, cidx=None):

        if lidx != None:
            recs = self.error_cells.get(lidx)
            if recs == None:
                return None
            if cidx == None:
                return recs
            return recs.get(cidx)
        return None

    def errors_list(self):

        lst = []
        for ridx, row in enumerate(self.cells):
            for cidx, cell in enumerate(row):
                lst.extend(cell.errors)

        #print lst
        return lst

        lst = []
        for lidx in sorted(self.error_cells.keys()):
            for cidx in sorted(self.error_cells[lidx].keys()):
                lst.extend(self.error_cells[lidx][cidx])
        return lst

    def errors_count(self):
        ec = 0
        for idx, grp in enumerate(self.groups_list):
            ec += grp.errors_count()

        return ec

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

    def get_points(self):

        grpLoca = self.group("LOCA")
        if grpLoca == None:
            return
        print "get CLOCA", grpLoca
        lst = []

        ## WSG84
        if grpLoca.has_heading("LOCAL_LAT") and grpLoca.has_heading("LOCAL_LON"):
            for rec in grpLoca.data:
                lat_s = rec.get("LOCA_LAT")
                lon_s = rec.get("LOCA_LON")
                ## addd Point
                #print "YES=", lat_s, lon_s



        ## BNG British National grid
        elif grpLoca.has_heading("LOCA_NATE") and grpLoca.has_heading("LOCA_NATN"):
            if not HAVE_BNG_LATLON:
                return lst
            for rec in grpLoca.data:
                #print rec
                loca_id = rec.get("LOCA_ID")
                east = float(rec.get("LOCA_NATE"))
                north = float(rec.get("LOCA_NATN"))
                #print east, north, rec.get("LOCA_NATE"), rec.get("LOCA_NATN")
                if east and north:
                    lat, lon = bng_to_latlon.OSGB36toWGS84(east, north)
                    lst.append(dict(lat=lat, lon=lon, east=east, north=north, loca_id=loca_id))
                    #features.append(make_feature(rec, lat, lon))

        return lst


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



    def load_ags4_string(self, ags4_str, file_name=None):
        """Load  document from an :term:`ags4` formatted string


        :param ags4_str: string to load
        :type ags4_str: str
        :rtype: str
        :return: An `Error` message if string not loaded, else `None`
        """

        # this code parses in a strange way atmo, r+d, with following steps
        #   1) parse csv file line by line into self.lines + self.csv_rows
        #   2) walk the self.csv_rows and mark the start+end index of each group
        #      marking some basic errors
        #   3) parse each group into its headings, units data etc

        ## Copy source as a string into mem here
        self.source = ags4_str

        if file_name:
            self.source_file_path = file_name



        ## Step 1:
        #  - split ags_string into lines
        #  - and parse `each line` into csv
        #  - and add to the doc
        loopGroup = None
        for lidx, line in enumerate(self.source.split("\n")):

            # removing and trailing whitespace eg \r
            # were in nix land, so reassemble with CRLF when dumping to ags
            stripped = line.strip()

            if stripped == "":
                # append blank line
                self.lines.append([])
                self.csv_rows.append([])
                self.cells.append([])
                continue

            # decode csv line
            reader = csv.reader( StringIO.StringIO(stripped) )
            csv_row = reader.next() # first row of reader

            self.lines.append(line)
            self.csv_rows.append(csv_row)

            row_cells = []

            for cidx, val in enumerate(csv_row):
                row_cells.append( OGTCell(lidx=lidx, cidx=cidx, value=val) )
            self.cells.append(row_cells)

        #################################======================================================================
        # next walk and clean
        loopGroup = None
        for lidx, rrow in enumerate(self.cells):
            #for cidx, cell in enumerate(row):
            #print "is_descr", cell, cell.cidx
            #if cidx == 0:
            #print lidx, row
            lenny = len(rrow)
            if lenny == 0:
                continue

            # DO DO catch row == 1 and row == 2

            # validate its a descriptor
            dcell = rrow[0]
            dcell.value, valid, errs = ags4.validate_descriptor(dcell.value, lidx=lidx, cidx=cidx)
            dcell.add_errors(errs)
            if valid:
                descriptor = dcell.value
                #drow = rrow[1:] # data row

                if descriptor == ags4.AGS4.GROUP:
                    """
                    if len(drow) == 0:
                        # TODO missing group descr
                        fix_me
                        grp_cell = OGTCell(lidx=lidx, cidx=cidx, value="MISSING")
                    elif len(drow) == 1:
                        grp_cell = drow[0]
                    else:
                        # TODO too many item for group
                        print len(drow), drow
                        sss
                        grp_cell = drow[1]
                    """
                    loopGroup = self.add_group(rrow, lidx)
                    #loopGroup.add_raw_row(rrow)

                elif descriptor == ags4.AGS4.HEADING:
                    # Its a HEADING row
                    #loopGroup.headings_source_sort = []
                    loopGroup.set_headings_row(rrow, lidx)
                    #loopGroup.add_raw_row(rrow)

                elif descriptor == ags4.AGS4.UNIT:
                    # a UNIT row
                    loopGroup.set_units_row(rrow, lidx)
                    #loopGroup.add_raw_row(rrow)

                elif descriptor == ags4.AGS4.TYPE:
                    # a TYPE row
                    loopGroup.set_types_row(rrow, lidx)
                    #loopGroup.add_raw_row(rrow)

                elif descriptor == ags4.AGS4.DATA:
                    # a DATA row
                    loopGroup.add_data_row(rrow, lidx)
                    #loopGroup.add_raw_row(rrow)
                    #if loopGroup.data_start_lidx == None:
                    #    loopGroup.data_start_lidx = lidx
            else:

                print "LOST row"
                loopGroup.add_lost_row(rrow, lidx)


        for g in self.groups_list:
            g.validate()


        ## Step 2
        # walk the decoded rows, and recognise the groups
        # and mark the start_index and end index of group

        # the pointer used for group
        loop_grp = None
        #print self.cells
        return None
        # walk the parsed cvs rows
        for lidx, row in []: #enumerate(self.csv_rows):

            #line_no = lidx + 1
            lenny = len(row)

            if lenny == 0:
                ## ags can allow no spaces between groups
                # blank row so ignore, eg mightbe a space between data or alike ?
                continue


            elif lenny == 1:
                # so we only got a first column, to check its valid
                #err = ags4.rule_3()
                self.add_error("Row has no data", rule=4, lidx=lidx)
                continue

            elif lenny < 2:
                # min of two items, so add to errors
                #self.error_rows[lidx] = row
                #err = ags4.rule_3()
                self.add_error("Row has no data", rule=4, lidx=lidx)
                continue

            else:

                # first item is data descriptor, but check code is valid (whitespace etc)
                cleaned_code, errs = ags4.validate_clean_str(row[0], lidx=lidx, cidx=0)
                self.add_errors(errs)

                # Check tis a valid descriptor
                clean, ok, er = ags4.validate_descriptor(cleaned_code, lidx=lidx, cidx=0)
                #self.add_error(er)


                if cleaned_code == ags4.AGS4.GROUP:

                    # close existing group if open
                    if loop_grp != None:
                        loop_grp.csv_end_index = lidx

                    ## we got a new group, check group has ucase, no whitespace etc
                    gcode, errs = ags4.validate_clean_str(row[1], lidx=lidx, cidx=1)
                    if len(errs) > 0:
                        self.add_errors(errs)

                    loop_grp = OGTGroup(gcode)
                    loop_grp.csv_start_index = lidx
                    self.append_group(loop_grp)


        # thirdly
        # - we parse each group's csv rows into the parts
        return None
        for group_code, grp in self.groups.iteritems():
            #print "========", group_code, grp, grp.csv_rows()
            #print grp.csv_rows()
            ss
            # walk the csv rows in this group
            for iidx, row in enumerate(grp.csv_rows()):

                if len(row) == 0:
                    # empty row so ignore
                    continue

                # We already validated descriptiors above but still need to clean here (TODO)
                descriptor = row[0].strip().upper()

                # xrow is the stuff without data descriptor in first col
                xrow = row[1:]

                # the line index is the group's start_index + iterator
                lidx = grp.csv_start_index + iidx

                if descriptor == ags4.AGS4.GROUP:
                    # already got group above so ignore
                    pass

                elif descriptor == ags4.AGS4.HEADING:
                    # Its a HEADING row

                    # first create a list in headings in original file order, cleaned
                    grp.headings_source_sort = []
                    for didx, raw_head_code in enumerate(xrow):
                        cleaned_head_code, errs = ags4.validate_clean_str(raw_head_code, lidx=lidx, cidx=didx+1)
                        self.add_errors(errs)
                        grp.headings_source_sort.append(cleaned_head_code)

                    # next loop the headings, create `OGTHeading objects` and add to group
                    for didx, head_code in enumerate(grp.headings_source_sort):
                        ogr = OGTHeading(ogtGroup=grp)
                        ogr.set_head_code(head_code, iidx, didx)
                        grp.headings[head_code] = ogr

                        # Validate heading code
                        errs = ags4.validate_heading_str(head_code, lidx=lidx, cidx=didx+1)
                        self.add_errors(errs)

                        # TODO validate custom headings first

                        # validate heading to ags4
                        err = ags4.validate_heading_ags(head_code, grp.group_code, lidx=lidx, cidx=didx+1)
                        self.add_errors(err)

                    errs = ags4.validate_headings_sort(grp.group_code, grp.headings_source_sort, lidx=lidx)
                    self.add_errors(errs)

                elif descriptor == ags4.AGS4.UNIT:
                    # a UNIT row
                    for didx, head_code in enumerate(grp.headings_source_sort):
                        grp.headings[head_code].set_unit(xrow[didx], iidx, didx)

                elif descriptor == ags4.AGS4.TYPE:
                    # a TYPE row
                    for didx, head_code in enumerate(grp.headings_source_sort):
                        clean_str, errs = ags4.validate_clean_str(xrow[didx], lidx=lidx, cidx=didx+1)
                        self.add_errors(errs)

                        ## Aae there custom types ??
                        errs = ags4.validate_type_ags(clean_str, lidx=lidx, cidx=didx+1)
                        self.add_errors(errs)
                        grp.headings[head_code].set_type(clean_str, iidx, didx)

                elif descriptor == ags4.AGS4.DATA:
                    # a DATA row
                    dic = {}
                    for didx, head_code in enumerate(grp.headings_source_sort):
                        dic[head_code] = xrow[didx]
                    grp.data.append( dic )


            #print group_code, grp.headings_source_sort

        #print self.error_rows

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

def create_doc_from_ags4_string(ags4_string, file_name=None):
    """Convenience function to create and load an OGTDocument from an ags string

    .. code-block:: python

        doc, err = ogt_doc.create_doc_from_ags4_string(ags4_string)
        if err:
            print err
        else:
            print doc.group("PROJ")
    """
    doc = OGTDocument()
    doc.source_file_path = file_name
    err = doc.load_ags4_string(ags4_string)
    return doc, err

def deadcreate_empty_doc():
    doc = OGTDocument()
    return doc

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

GROUPS_FIRST_CODES  = ["PROJ", "TRAN", "LOCA", "HDPH", "GEOL", "SAMP"]
"""The groups to appear first"""

GROUPS_LAST_CODES = ["ABBR", "DICT", "FILE", "TYPE", "UNIT"]
"""The groups to appear last"""

GROUPS_REQUIRED = ["PROJ", "TRAN", "TYPE", "UNIT"]
"""Mandatory groups"""

def groups_sort(unsorted_groups):
    """Returns a 'preferred' order for the group keys

    .. note::

        This is a bit hacky as the ags spec does not define
        any group order, however PROJ does sensibly tend to come first etc.


        So this return a list with

        - at the start list
        - at end list
        - and everything else in the middle sorted alphabetically
        - BUT ??
        - one idea might be to push insitu stuff to front
        - and lab stuff next
        - and main reporting stuff to end
        - although it might be preferable the opposite away around


    :return: An `list` of group codes in preffered order
    """

    # make a newlist/copy of the groups in doc
    grps = unsorted_groups[:]

    ## the start groups
    ret_start = []
    for gc in GROUPS_FIRST_CODES:
        if gc in grps:
            # exists so add to start, and remove from list
            ret_start.append(gc)
            grps.remove(gc)

    # the end groups
    ret_end = []
    for gc in GROUPS_LAST_CODES:
        if gc in grps:
            # exists so add to end, and remove from list
            ret_end.append(gc)
            grps.remove(gc)

    return ret_start + sorted(grps) + ret_end


class OGTGroup:
    """Represents a Document's :term:`GROUP` and headings"""

    def __init__(self, ogtDoc):
        """

        :param group_code: The four character group code to initialize with
        :type group_code: str
        """
        self.ogtDoc = ogtDoc
        """Pointer to parent :class:`~ogt.ogt_doc.OGTDocument` instance"""

        self.group_code = None
        """The four character group code"""

        #self.headings = {}
        self._headings = []
        """A `dict` of head_code > ogtHeadings"""

        #self.headings_sort = []
        """A list of head_codes in recommended sort order"""

        #self.headings_source_sort = []
        """The list of head_code with the sort order in original file"""

        #self.units = {}
        """A `dict` of `head_code:unit`  """

        #self.types = {}
        self.rows = []
        self.raw_rows = []
        """A `dict` of `head_code:type` """

        self.data = []
        """A `list` of `list`s with `head_code:value`  """

        #self.group_start_lidx = None
        """The line index this groups start at"""

        #self.csv_end_index = None
        """The line index this groups ends at"""

        self._data_dict = None

        self.headings_idx = None
        self.units_idx = None
        self.types_idx = None
        self.data_start_idx = None
        self.lost_idxs = []

        self.column_count = 0
        self.errors = []

    def __repr__(self):
        return "<OGTGroup %s>" % self.group_code

    def _update_col_count(self, rows):
        if len(rows) > self.column_count:
            self.column_count = len(rows)

    @property
    def group_description(self):
        dic =  self.data_dict()
        if dic:
            return self.data_dict().group_description
        return None

    def set_group(self, row_cells, lidx):

        # validate
        self.group_code = row_cells[1].value
        self.rows.append(row_cells)
        self.group_start_lidx = lidx
        self._update_col_count(row_cells)

    def set_headings_row(self, row_cells, lidx):
        print "----------------------------"
        print "set_headings", row_cells
        self.headings_idx = lidx - self.group_start_lidx
        self.rows.append(row_cells)
        self._update_col_count(row_cells)

        self.headings_source_sort = []

        for cidx, hcell in enumerate(row_cells[1:]):
            print "ll=", cidx, hcell
            # validate the headings string
            hcell.value, fatal, errs = ags4.validate_heading_str(hcell.value, lidx=lidx, cidx=cidx + 1)
            #hcell.add_errors(errs)
            #self.add_errors(errs)
            #self.headings_source_sort.append(hcell.value)self.headersListWidget.model.layoutChanged.emit()vla

            # create `OGTHeading objects` and add to group
            oHead = OGTHeading(ogtGroup=self, cidx=cidx)
            #self.headings[hcell.value] = oHead
            self._headings.append(oHead)
            #print "done-", self._headings


    def has_heading(self, head_code):
        return head_code in self.headings

    def headings_sort(self):

        if self._headings_sort == None:
            dd = self.data_dict()
            #print "dd=", dd, self.headings
            if dd == None:
                return []
            self._headings_sort = []
            if dd.headings_sort() == None:
                return self.headings.keys()
            else:
                for head_code in dd.headings_sort():
                    if head_code in self.headings:
                        self._headings_sort.append(head_code)

        return self._headings_sort

    def headings_list(self):
        """Return a list of heading """
        #print "headings_list", self._headings, self
        return self._headings
        lst = []
        for hcode in self.headings_source_sort:
            #dic = dict(head_code = hcode, unit=self.units[hcode], data_type=self.data_types[hcode])
            lst.append( self.headings[hcode] )
        return lst

    def heading_by_index(self, idx):
        # TODO trap
        #cidx = col_idx + 1
        #print self._headings
        return self._headings[idx]
        """hcell = self.cell(self.headings_idx, cidx)
        if hcell:
            head = OGTHead(hcell.value)

            unitcell = self.cell(self.units_idx, cidx)
            if unitcell:
                head.unit = unitcell.value

            typecell =  self.cell(self.types_idx, cidx)
            if typecell:
                head.type = typecell.value

            dd = self.data_dict()
            if dd:
                headDD, found = dd.heading(head.head_code)
                if found:
                    head.head_description = headDD.get("head_description")

            return head
        return None
        """
    @property
    def headings_count(self):
        # its the total columns minux the descriptor
        return self.column_count - 1

    def deadcells(self):
        """Returns the csv rows used in this group, return data from parentDocument """
        return self.parentDoc.csv_rows[self.csv_start_index:self.csv_end_index]

    def cell(self, ridx, cidx):
        if ridx == None:
            return None

        row = self.rows[ridx]
        if cidx > len(row) - 1 :
            return None
        return row[cidx]

    def set_cell_value(self, ridx, cidx, value):
        cell = self.cell(ridx, cidx)
        if cell:
            cell.value = value
            self.validate()
            return True
        return False

    def set_data_cell_value(self, ridx, cidx, value):
        cell = self.data_cell(ridx, cidx)
        if cell:
            cell.value = value
            self.validate()
            return True
        return False

    def data_cell(self, ridx, cidx):
        #print self.data
        #return self.parentDoc.cells[self.csv_start_index + ridx + 4][cidx+1]
        #return self.data[ridx][self.headings_source_sort[cidx]]
        #print self.data_start_lidx
        re_idx = self.data_start_idx + ridx
        ce_idx = cidx + 1
        return self.rows[re_idx][ce_idx]

    def add_raw_row(self, raw_cells):
        self.raw_rows.append(raw_cells)

    def add_data_row(self, row_cells, lidx):
        """Adds a DATA Row

        TODO check lidx is valid
        """
        if self.data_start_idx == None:

            self.data_start_idx = len(self.rows)
        self.rows.append(row_cells)

    def add_lost_row(self, row_cells, lidx):
        """Not sure, but we need add rows with no descriptors, or merge erors"""
        self.rows.append(row_cells)
        self.lost_idxs.append(lidx)

    def data_row_cells(self, ridx):
        #return dself.parentDoc.cells[self.csv_start_index + ridx + 4]
        #return self.data[ridx]
        return self.data[ridx]

    def data_rows_dict(self):
        return ss

    def data_row_dict(self, ridx):
        dic  = {}
        lst = self.data_row_cells(ridx)
        for idx, head_code in enumerate(self.headings_source_sort):
            dic[head_code] = lst[idx].value
        return dic


    def data_column_from_head_code(self, head_code):
        if head_code in self.headings:
            return [rec[head_code] for rec in self.data]
        return None

    def data_rows_count(self):
        return len(self.rows) - 4

    def row_count(self):
        return len(self.rows)

    def data_dict(self):
        """Returns the data dictionary for this group, if it exists

        :return: An instance of  :class:`~ogt.ags.ags4.AGS4GroupDataDict` if
                 it exists, else `None`

        """
        if self._data_dict == None:
            self._data_dict = ogt.ags4.AGS4GroupDataDict(self.group_code)
        return self._data_dict


    def to_dict(self):
        """Return a dictionary  of the group data in two formats

        :param edit_mode: see :ref:`edit_mode`
        :type edit_mode: bool
        :rtype: dict
        :return: A dictionary with the data
        """
        #print self.docParent.opts, self
        if self.docParent.opts.xmode:

            # shortcut to data dict
            grp_dd = self.data_dict()
            heads = []
            for idx, head_code in enumerate(self.headings_sort()):

                ags_data_dict, found = grp_dd.heading(head_code)
                #print "hh=", ags_data_dict, found

                heads.append( { "head_code": head_code,
                                    "data_dict": ags_data_dict,
                                    "unit": self.units[head_code],
                                    "type": self.types[head_code]
                                    })

            dic = { "group_code": self.group_code,
                    "data_dict": grp_dd.group(),
                    "headings": heads,
                    "headings_sort": self.headings_sort(),
                    "notes": grp_dd.notes(),
                    "data": self.data}
            return dic

        dic = {ogt.ags4.AGS4_DESCRIPTOR.unit: self.units,
               ogt.ags4.AGS4_DESCRIPTOR.type: self.types,
               ogt.ags4.AGS4_DESCRIPTOR.data: self.data}

        return dic

    def set_units_row(self, row_cells, lidx):

        self.units_idx = lidx - self.group_start_lidx
        self.rows.append(row_cells)
        self._update_col_count(row_cells)
        return
        for idx, cell in enumerate(row_cells):
            self._headings[idx].set_unit(cell)

    def units_list(self):

        lst = []
        for ki in self.headings_sort():
            lst.append( self.units[ki] )

        return lst

    def set_types_row(self, row_cells, lidx):

        self.types_idx = lidx - self.group_start_lidx
        self.rows.append(row_cells)
        self._update_col_count(row_cells)
        for idx, cell in enumerate(row_cells[1:]):
            self._headings[idx].set_type(cell)

    def types_list(self):

        lst = []
        for ki in self.headings_sort():
            lst.append( self.types[ki] )

        return lst

    def errors_count(self):
        return len(self.errors)
        ec = 0
        for h in self.headings_list():
            #print h.errors_count()
            ec += h.errors_count()
        return ec

    def deaderrors_list(self):
        errs = []
        for ridx, row in enumerate(self.rows):
            for cidx, cell in enumerate(row):
                errs.extend(cell.errors)
                #for e in cell.errors:
                #    yield e
        return errs

    def add_errors(self, errs):
        if errs == None:
            return
        if isinstance(errs, OgtError):
            self.add_error(errs)
            return
        if len(errs) == 0:
            return
        for e in errs:
            self.add_error(e)

    def add_error(self, err):
        self.errors.append(err)


    def validate(self):
        print "VALIDATE-------------------", self.group_code
        self.errors = []
        for ridx, row in enumerate(self.rows):


            for cidx, cell in enumerate(row):

                # validate descriptor
                if cidx == 0:
                    cell.value, ok, errs = ags4.validate_descriptor(cell.value)
                    self.add_errors(errs)
                else:

                    if ridx == self.headings_idx:
                        # validate headings
                        cell.value, fatal, errs = ags4.validate_heading_str(cell.value, cidx=cidx, lidx=ridx)
                        self.add_errors(errs)
                        print errs, cell.value
                        if not fatal:
                            errs = ags4.validate_heading_ags(cell.value, self.group_code, cidx=cidx, lidx=ridx)
                            print "RRRRR", errs
                            self.add_errors(errs)

                    if ridx == self.types_idx:
                        pass

        print "afterVALID", len(self.errors), self.errors



class OGTCell:

    def __init__(self, lidx, cidx, value):
        """Line and col index = value
        """

        self.lidx = lidx
        self.cidx = cidx

        self.raw = value

        self.errors = []
        self.value, errs = ags4.strip_string(self.raw)
        for e in errs:
            self.errors.append(e)

    def add_errors(self, errs):
        if errs == None:
            return
        if isinstance(errs, OgtError):
            self.errors.append(errs)
        if len(errs) == 0:
            return
        self.errors.extend(errs)

    def errors_count(self):
        return len(self.errors)

    def get_bg(self, errors_only=False):
        """Ok so its not really logic, but idea is to color cells in code, and acorss www, desktop, mobile,
        - no erros its white
        - an data dic violation = dd vilolation
        - a error eg incorrect stuff = rule
        - warn = stuff fixed, eg white space
        """
        for err in self.errors:
            if err.type == OgtError.ERR: # found an error
                return err.bg
        if not errors_only:
            for err in self.errors:
                if err.type == OgtError.WARN: # found a warning
                    return err.bg
        return CELL_COLORS.ok_bg

    def __repr__(self):
        return "<Cell [%s,%s] `%s`>" % (self.lidx, self.cidx, self.raw)

class deadOGTHead:
    def __init__(self, head_code):
        self.head_code = head_code
        self.unit = None
        self.type = None
        self.head_description = None

class OGTHeading:

    def __init__(self,  ogtGroup=None, cidx=None):

        self.ogtGroup = ogtGroup
        self.cidx = cidx
        #self.head_code = head_code
        #self.unit = None
        #self.type = None

        #self.head_code_cell = cell
        #if isinstance( self.head_code_cell, str):
        #    stopppp
        #self.unit_cell = None
        #self.type_cell = None

    def __repr__(self):
        return "OGTHeading `%s`>" % self.head_code

    @property
    def head_description(self):
        dd = self.ogtGroup.data_dict()
        if dd:
            head, found = dd.heading(self.head_code)
            if found:
                return head.get("head_description")
        return None

    @property
    def head_code(self):
        cell = self.ogtGroup.cell(self.ogtGroup.headings_idx, self.cidx + 1)
        if cell:
            return cell.value
        return "???"
    """
    def dead_set_head_code(self, head_code, row_idx, col_idx):
        self.deadhead_code = head_code
        self.deadhead_code_index = [row_idx, col_idx]
    """

    def set_unit(self, cell):
        scell.value, errs = ags4.validate_clean_str(cell.value, upper=True)
        self.ogtGroup.add_errors(errs)
        self.unit_cell = cell

    @property
    def unit(self):
        cell = self.ogtGroup.cell(self.ogtGroup.units_idx, self.cidx)
        if cell:
            return cell.value
        return None


    @property
    def unit_label(self):
        v = self.unit
        if v:
            return v
        return ""


    def set_type(self, cell):
        cell.value, errs = ags4.validate_clean_str(cell.value, upper=True)
        cell.add_errors(errs)
        self.type_cell = cell

    @property
    def type(self):
        cell = self.ogtGroup.cell(self.ogtGroup.types_idx, self.cidx)
        if cell:
            return cell.value
        return None

    @property
    def type_label(self):
        v = self.type
        if v:
            return v
        return ""


    def errors_count(self):
        return self.errors
        ec = 0
        #print "hc=", [self.head_code_cell, self.unit_cell, self.type_cell]
        for cell in [self.head_code_cell, self.unit_cell, self.type_cell]:
            if cell != None:
                ec += cell.errors_count()

        return ec
