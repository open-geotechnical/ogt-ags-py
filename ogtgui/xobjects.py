# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

from Qt import Qt, QtGui, QtCore

from . import xwidgets


DATA_ROLE = Qt.UserRole + 20
SORT_NO = "sort_no"
SORT_DATE = "sort_date"


class XSortFilterProxyModel(QtGui.QSortFilterProxyModel):

    def __init__( self, parent=None, active=None, source_model=None):
        QtGui.QSortFilterProxyModel.__init__( self, parent )
        #super(QtGui.QSortFilterProxyModel, self).__init__(parent)

        self.active = active



        self.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setDynamicSortFilter(True)

        if source_model:
            self.setSourceModel(source_model)

    def lessThan(self, lidx, ridx):
        #print lidx.column(), ridx.column()
        #
        # sm = self.sourceModel()

        #hi = sm.horizontalHeaderItem( lidx.column() ).data(DATA_ROLE).toString()
        #sort_role = sm.horizontalHeaderItem( lidx.column() ).data(DATA_ROLE).toString()
        #print lidx.column(), sort_role,sort_role.length(), sort_role == DATA_ROLE
        #if sort_role.length() > 0 :
        #    if  sort_role == SORT_NO:
        #        ld, _ = sm.itemFromIndex( lidx ).text().replace(",", "").toFloat()
        #        rd, _ = sm.itemFromIndex( ridx ).text().replace(",", "").toFloat()
        #        return rd > ld

        return QtGui.QSortFilterProxyModel.lessThan(self, lidx, ridx)

    def set_active_filter(self, activ):

        self.active = activ
        self.invalidateFilter()


    def get_items_from_index(self, pidx):
        sidx = self.mapToSource(pidx)
        return self.sourceModel().get_items_from_index(sidx)

    def get_dic_from_index(self, pidx):
        sidx = self.mapToSource(pidx)
        return self.sourceModel().get_dic_from_index(sidx)


    def get_dic_items_from_index(self, pidx):
        return self.get_dic_from_index(pidx), self.get_items_from_index(pidx)


##==============================================================================================
class XStandardItemModel( QtGui.QStandardItemModel ):
    """An extended model with convenience functions, intended as a base model"""


    def __init__( self, parent=None ):
        QtGui.QStandardItemModel.__init__( self, parent )

        self.widget = None



    def set_widget(self, widget):
        self.widget = widget



    def set_header(self, col, text, align=None, tooltip=None, sort=None):
        """Sets a horizontal header

        :param col: The column index
        :type col: int
        :param label: The text label
        :type label: str`
        :param align: Text alignment
        :type align: Qt.Align
        :param tooltip: The tooltip to show on header hover
        :type tooltip: str
        :param sort: # TBA
        :type sort: int

        """
        item = xwidgets.StandardItem()
        item.setText(text)
        if align:
            item.setTextAlignment(align)
        if tooltip:
            item.setToolTip(tooltip)
        if sort:
            item.setData(sort, DATA_ROLE)
        self.setHorizontalHeaderItem(col, item)

        #print " header >>>", col, label, self.columnCount()
    def remove_rows(self):
        self.removeRows( 0, self.rowCount() )

    def make_blank_row(self):
        arr = []
        for _ in range(0, self.columnCount()):
            item = xwidgets.StandardItem()
            arr.append(item)

        return arr

    def make_row(self, xid, col):
        arr = []
        for c in range(0, self.columnCount()):
            item = xwidgets.StandardItem()
            if c == col:
                item.setText(str(xid))
            arr.append(item)
        self.appendRow(arr)
        return arr[0].row()



    def set_row_bg(self, ridx, color):

        for c in range(0, self.columnCount()):
            self.item(ridx, c).set_bg(color)

    def get_items_from_item(self, item):
        ridx = item.index()
        return self.get_items_from_index(ridx)

    def get_items_from_index(self, midx):
        arr = []
        for cidx in range(0, self.columnCount()):
            idx = self.index(midx.row(), cidx, midx.parent() )
            arr.append( self.itemFromIndex( idx) )
        #print "get_items_from_row", idx, arr
        return arr

        #idx = self.index(sidx.row(), )
        #return self.get_items_from_row( sidx.row() )

    def get_items_from_row(self, ridx):

        arr = []
        for cidx in range(0, self.columnCount()):
            arr.append( self.item(ridx, cidx) )
        #print "get_items_from_row", ridx, arr
        return arr


    def strike_row(self, ridx, state):
        for cidx in range(0, self.columnCount()):
            font = self.item(ridx, cidx).font()
            font.setStrikeOut(state)
            self.item(ridx, cidx).setFont(font)

