# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

import os
import collections

from Qt import QtGui, QtCore, Qt, pyqtSignal

from  . import xwidgets
from .img import Ico
from ogt import ags4


def bg_color(descr):
    if descr == ags4.AGS4.GROUP:
        return "#D4C557"

    if descr == ags4.AGS4.HEADING:
        return "#FCF66D"

    if descr in [ags4.AGS4.UNIT, ags4.AGS4.TYPE]:
        return "#FFE8B9"

    if descr == ags4.AGS4.DATA:
        return "#DFD1FF"

    return "#ffffff"


class OGTSourceViewWidget( QtGui.QWidget ):
    """The SourceViewWidget info which in row 0 """

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        self.tabWidget = QtGui.QTabWidget()
        self.mainLayout.addWidget(self.tabWidget)

        # Source View
        self.sourceView = xwidgets.LNTextEdit()
        self.tabWidget.addTab(self.sourceView, "Raw Text")

        # spread view
        self.tableWidget = QtGui.QTableWidget()
        self.tabWidget.addTab(self.tableWidget, "Grid View")

        self.tabWidget.setCurrentIndex(1)

    def load_document(self, doco):

        self.sourceView.setText(doco.source)

        #print doco.cells()
        self.tableWidget.setRowCount(len(doco.csv_rows))

        for ridx, row in enumerate(doco.csv_rows):

            if self.tableWidget.columnCount() < len(row):
                self.tableWidget.setColumnCount(len(row))
            errs = doco.error_rows.get(ridx)
            print ridx, errs
            bg = None
            for cidx, cell in enumerate(row):
                #print ridx, cidx
                #if cidx == 0:
                #    bg = bg_color(cell)
                item = xwidgets.XTableWidgetItem()
                item.setText( cell )
                self.tableWidget.setItem(ridx, cidx, item)

                if errs != None:
                    s = []
                    for er in errs:
                        if er.cidx == cidx:
                            item.set_bg(er.bg)
                            s.append(er.message)
                    if len(s) > 0:
                        item.setToolTip("\n".join(s))
                ## color the row
                #item.setBackgroundColor(QtGui.QColor(bg))

    def select_cell(self, lidx, cidx):
        self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.tableWidget))
        self.tableWidget.setCurrentCell(lidx, cidx)


class OGTScheduleWidget( QtGui.QWidget ):
    """The SourceViewWidget info which in row 0 """

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        # spread view
        self.tableWidget = QtGui.QTableWidget()
        self.mainLayout.addWidget(self.tableWidget)




    def load_document(self, doco):


        samples = doco.group("SAMP")
        sched_group = doco.group("LBST")

        if samples == None or sched_group == None:
            return

        sched = {}
        locs = {}
        for row in sched_group.data:
            #print row
            tst = row.get('LBST_TEST')
            if not tst in sched:
                sched[tst] = dict(test=tst, samp_refs={})
                #tests.append(tst)
            loc = row.get('LOCA_ID') # + "~~" + row.get("SAMP_REF")
            if not loc in locs:
                locs[loc] = collections.OrderedDict()

            samp_ref = row.get("SAMP_REF")
            if not samp_ref in locs[loc]:
                locs[loc][samp_ref] = {}

            locs[loc][samp_ref][tst] = dict(loca_id=loc,
                                            samp_ref=samp_ref,
                                            params = row.get('LBST_METH') )

        #print sched
        tests = sorted(sched.keys())
        self.tableWidget.setColumnCount(len(tests) + 2)

        hitem = xwidgets.XTableWidgetItem()
        hitem.set("LOCA_ID", bold=True)

        self.tableWidget.setHorizontalHeaderItem(0, hitem)

        hitem = xwidgets.XTableWidgetItem()
        hitem.set("SAMP_REF", bold=True)
        f = hitem.font()
        f.setBold(True)
        hitem.setFont(f)
        self.tableWidget.setHorizontalHeaderItem(1, hitem)

        for cidx, ki in enumerate(tests):
            tst = sched[ki]
            hitem = xwidgets.XTableWidgetItem()
            hitem.set(ki, bold=True)
            self.tableWidget.setHorizontalHeaderItem(cidx + 2, hitem)

        #print locs
        for loca in sorted(locs.keys()):

            for samp_ref in locs[loca].keys():

                row_idx = self.tableWidget.rowCount()
                self.tableWidget.setRowCount(row_idx  + 1)

                bg = "#dddddd"

                #print loca, locs[loca]
                item = xwidgets.XTableWidgetItem()
                item.set(loca, bold=True, bg=bg)
                self.tableWidget.setItem(row_idx, 0, item)

                item = xwidgets.XTableWidgetItem()
                item.set(samp_ref, bold=True, bg=bg, align=Qt.AlignCenter)
                self.tableWidget.setItem(row_idx, 1, item)

                #print locs[loca][samp_ref]
                for cidx, tst_ki in enumerate(tests):

                    item = xwidgets.XTableWidgetItem()

                    if tst_ki in locs[loca][samp_ref]:

                        tst = locs[loca][samp_ref][tst_ki]


                        item.set(tst['params'], bg="yellow", check=Qt.Checked)


                    else:
                        item.setCheckState(Qt.Unchecked)

                    self.tableWidget.setItem(row_idx, cidx + 2, item)

        # resize columns, with max_width
        col_width = 200

        self.tableWidget.resizeColumnsToContents()
        for cidx in range(0, self.tableWidget.columnCount()):
            if self.tableWidget.columnWidth(cidx) > col_width:
                self.tableWidget.setColumnWidth(cidx, col_width)


class C_EG:
    """Columns for examples"""
    file_name = 0

class ExamplesWidget( QtGui.QWidget ):

    sigFileSelected = pyqtSignal(object)

    def __init__( self, parent):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False

        self.setMinimumWidth(300)

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        #=============================
        ## Set up tree
        self.tree = QtGui.QTreeWidget()
        self.mainLayout.addWidget(self.tree, 30)

        self.tree.setRootIsDecorated(False)
        self.tree.header().setStretchLastSection(True)
        self.tree.header().hide()

        hi = self.tree.headerItem()
        hi.setText(C_EG.file_name, "Example")


        self.tree.itemClicked.connect(self.on_tree_item_clicked)

        self.load_files_list()



    def load_files_list(self, sub_dir=None):

        files_list, err = ags4.examples_list()
        if err:
            pass #TODO
        self.tree.clear()

        for fd in files_list:
            file_name = fd["file_name"]
            item = QtGui.QTreeWidgetItem()
            item.setText(C_EG.file_name, file_name)
            item.setIcon(C_EG.file_name, Ico.icon(Ico.Ags4))
            f = item.font(C_EG.file_name)
            f.setBold(True)
            item.setFont(C_EG.file_name, f)
            self.tree.addTopLevelItem(item)



    def on_tree_item_clicked(self, item, col):

        file_name = str(item.text(C_EG.file_name))
        self.sigFileSelected.emit(file_name)


class C_ERR:
    """Columns for examples"""
    err = 0
    lidx = 1
    cidx = 2
    descr = 3

class OGTErrorsWidget( QtGui.QWidget ):

    sigGotoSource = pyqtSignal(int, int)

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False



        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        #=============================
        ## Set up tree
        self.tree = QtGui.QTreeWidget()
        self.mainLayout.addWidget(self.tree, 30)

        self.tree.setRootIsDecorated(False)
        self.tree.header().setStretchLastSection(True)

        hi = self.tree.headerItem()
        hi.setText(C_ERR.err, "Type")
        hi.setText(C_ERR.lidx, "Line")
        hi.setText(C_ERR.cidx, "Column")
        hi.setText(C_ERR.descr, "Description")


        self.tree.itemClicked.connect(self.on_tree_item_clicked)





    def load_document(self, ogtDoc):


        #print ogtDoc.error_rows
        for lidx in sorted(ogtDoc.error_rows.keys()):

            errs = ogtDoc.error_rows[lidx]

            for er in errs:

                item = xwidgets.XTreeWidgetItem()
                item.set(C_ERR.err, "Error" if er.error else "Warning", bg="pink" if er.error else "cyan")
                item.set(C_ERR.descr, er.message )
                item.set(C_ERR.lidx, er.line_no, align=Qt.AlignCenter)
                item.set(C_ERR.cidx, er.column_no, align=Qt.AlignCenter)
                #item.setIcon(C_EG.file_name, Ico.icon(Ico.Ags4))

                self.tree.addTopLevelItem(item)

        #self.tree.sortByColumn(C_ERR.lidx, Qt.AscendingOrder)

    def on_tree_item_clicked(self, item, col):

        self.sigGotoSource.emit(item.i(C_ERR.lidx) - 1, item.i(C_ERR.cidx) - 1)


