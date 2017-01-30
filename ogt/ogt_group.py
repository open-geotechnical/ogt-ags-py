# -*- coding: utf-8 -*-

import ogt.ags4

def groups_sort(unsorted_groups):
    """Returns a preffered order for the groups"""

    start = ["PROJ", "TRAN", "LOCA", "HDPH", "GEOL", "SAMP"]
    end = ["ABBR", "DICT", "FILE", "TYPE", "UNIT"]

    grps = unsorted_groups[:]

    ret_start = []
    for gc in start:
        if gc in grps:
            ret_start.append(gc)
            grps.remove(gc)

    ret_end = []
    for gc in end:
        if gc in grps:
            ret_end.append(gc)
            grps.remove(gc)

    ret = ret_start + sorted(grps) + ret_end
    #print ret
    return ret


class OGTGroup:
    """Represents a Document's :term:`GROUP` and headings"""

    def __init__(self, group_code):
        """

        :param group_code: The four character group code to initialize with
        :type group_code: str
        """
        self.parentDoc = None
        """Pointer to parent :class:`~ogt.ogt_doc.OGTDocument` instance"""

        self.group_code = group_code
        """The four character group code"""

        self.headings = {}
        """A `dict` of headings"""

        self._headings_sort = None
        """A list of head_codes in recommended sort order"""

        self.headings_source_sort = []
        """The list of head_code with the sort order in original file"""


        self.units = {}
        """A `dict` of `head_code:unit`  """

        self.types = {}
        """A `dict` of `head_code:type` """

        self.data = []
        """A `list` of `dict`s with `head_code:value`  """

        #self.csv_rows = []
        #"""A `list` of csv rows  """

        self.csv_start_index = None
        """The line no this groups start at"""

        self.csv_end_index = None
        """The line no this groups start at"""



        self._data_dict = None


    def csv_rows(self):
        """Returns the csv rows used in this group"""
        return self.parentDoc.csv_rows[self.csv_start_index:self.csv_end_index]

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


    def data_dict(self):
        """Returns the data dictionary for this group, if it exists

        :return: An instance of  :class:`~ogt.ags.ags4.AGS4GroupDataDict` if
                 it exists, else `None`

        """
        if self._data_dict == None:
            self._data_dict = ogt.ags4.AGS4GroupDataDict(self.group_code)
        return self._data_dict


    def to_dict(self, edit_mode=False):
        """Return a dictionary  of the group data in two formats

        :param edit_mode: see :ref:`edit_mode`
        :type edit_mode: bool
        :rtype: dict
        :return: A dictionary with the data
        """
        if edit_mode:

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


    def data_column(self, head_code):
        if head_code in self.headings:

            return [rec[head_code] for rec in self.data]
        return None

    def units_list(self):

        lst = []
        for ki in self.headings_sort():
            lst.append( self.units[ki] )

        return lst

    def types_list(self):

        lst = []
        for ki in self.headings_sort():
            lst.append( self.types[ki] )

        return lst
"""
class OGTHeading:

    def __init__(self, head_code=None, index=None):

        self.head_code = head_code
        self.index = index

        self.unit = None
        self.type = None
"""
