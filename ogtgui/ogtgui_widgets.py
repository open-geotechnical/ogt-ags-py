# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

import os
import collections

from Qt import QtGui, QtCore, Qt, pyqtSignal

import xwidgets
from img import Ico
from ogt import ags4
from ogt import CELL_COLORS

import app_globals as G

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

class FILTER_ROLE:
    warn = Qt.UserRole + 3
    err = Qt.UserRole + 5
class OGTSourceViewWidget( QtGui.QWidget ):
    """The SourceViewWidget info which in row 0 """



    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False
        self.setObjectName("OGTSourceViewWidget")

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        self.tabWidget = QtGui.QTabWidget()
        self.mainLayout.addWidget(self.tabWidget)

        # Source View
        self.sourceView = xwidgets.LNTextEdit()
        self.tabWidget.addTab(self.sourceView, "Raw Text")

        # Grid view
        widget = QtGui.QWidget()
        gridLay = xwidgets.vlayout()
        widget.setLayout(gridLay)
        self.tabWidget.addTab(widget, "Grid View")

        self.splitter = QtGui.QSplitter()
        self.splitter.setObjectName(self.objectName() + "grid_splitter")
        gridLay.addWidget(self.splitter)

        sty = "QTableView {gridline-color: #dddddd;}"
        self.tableWidget = QtGui.QTableWidget()
        self.splitter.addWidget(self.tableWidget)

        self.tableWidget.setStyleSheet(sty)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableWidget.itemSelectionChanged.connect(self.on_select_changed)
        self.tableWidget.horizontalHeader().sectionClicked.connect(self.on_row_clicked)

        self.errorsWidget = OGTErrorsWidget(mode=VIEW_ERR_MODE.document)
        self.errorsWidget.setMinimumWidth(300)
        self.splitter.addWidget(self.errorsWidget)
        self.errorsWidget.sigGotoSource.connect(self.select_cell)
        self.errorsWidget.sigErrorsFilter.connect(self.update_colours)

        G.settings.restore_splitter(self.splitter)
        self.splitter.splitterMoved.connect(self.on_splitter_moved)

        self.tabWidget.setCurrentIndex(1)

    def clear(self):
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)
        self.sourceView.setText("")
        self.errorsWidget.clear()

    def on_splitter_moved(self, i, pos):
        G.settings.save_splitter(self.splitter)

    def load_document(self, doco):

        self.sourceView.setText(doco.source)

        show_warn, show_err = self.errorsWidget.get_error_filters()
        #print "filters=", show_warn, show_err
        #print doco.cells()
        self.tableWidget.setRowCount(len(doco.csv_rows))

        for ridx, row in enumerate(doco.csv_rows):

            # each csv_row is not the same, so extend here
            if self.tableWidget.columnCount() < len(row):
                self.tableWidget.setColumnCount(len(row))


            #errs = doco.error_cells.get(ridx)
            #print ridx, errs
            bg = None
            for cidx, cell in enumerate(row):
                #print ridx, cidx
                #if cidx == 0:
                #    bg = bg_color(cell)
                item = xwidgets.XTableWidgetItem()
                item.setText( cell )
                item.set_bg("#EAFFE0")
                self.tableWidget.setItem(ridx, cidx, item)


                errs = doco.get_errors(lidx=ridx, cidx=cidx)
                if errs != None:
                    #print ridx, cidx, errs
                    for er in errs:
                        #print ridx, cidx, er.error
                        if er.type:
                            item.setData(FILTER_ROLE.err, "1")
                        else:
                            item.setData(FILTER_ROLE.warn, "1")
                        """    
                        if er.cidx == cidx:
                            item.set_bg(er.bg)
                        """
                    self.set_item_bg(item, show_warn, show_err)
                ## color the row
                #item.setBackgroundColor(QtGui.QColor(bg))
            self.tableWidget.setRowHeight(ridx, 20)


        self.errorsWidget.load_document(doco)

    def set_item_bg(self, item, show_warn, show_err):
        has_warn = item.data(FILTER_ROLE.warn).toBool()
        has_err = item.data(FILTER_ROLE.err).toBool()
        item.set_bg("white")
        if show_warn and has_warn:
            item.set_bg(ERR_COLORS.warn_bg)
        if show_err and has_err:
            item.set_bg(ERR_COLORS.err_bg)


    def update_colours(self, show_warn, show_err):
        self.tableWidget.setUpdatesEnabled(False)
        for ridx in range(0, self.tableWidget.rowCount()):
            for cidx in range(0, self.tableWidget.columnCount()):
                item = self.tableWidget.item(ridx, cidx)
                if item:
                    self.set_item_bg(item, show_warn, show_err)
        self.tableWidget.setUpdatesEnabled(True)

    def select_cell(self, lidx, cidx):
        self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.tableWidget))
        self.tableWidget.setCurrentCell(lidx, cidx)
        item = self.tableWidget.currentItem()
        self.tableWidget.scrollToItem(item, QtGui.QAbstractItemView.PositionAtCenter)


    def on_select_changed(self):
        item = self.tableWidget.currentItem()
        if item == None:
            self.errorsWidget.select_items(None, None)
            return

        self.errorsWidget.select_items(item.row(), item.column())


    def on_row_clicked(self, ridx):
        print ridx

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


    def clear(self):
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)


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



class ErrorsListModel(QtCore.QAbstractTableModel):

    class C:
        err = 0
        lidx = 1
        cidx = 2
        rule = 3
        highlight = 4
        description = 5
        search = 6

    def __init__(self, mode):
        QtCore.QAbstractTableModel.__init__(self)

        self.mode = mode
        self.ogtDoc = None
        self.ogtGroup = None
        self._col_labels = ["Type", "Line", "Col", "Rule", "High", "Description", "search"]

    def set_group(self, ogtGroup):
        self.ogtGroup = ogtGroup

    def load_document(self, ogtDoc):
        self.ogtDoc = ogtDoc
        sself.modelReset.emit()
        #print self.ogtDoc, self



    def columnCount(self, foo):
        return len(self._col_labels)

    def rowCount(self, midx):
        if self.mode == VIEW_ERR_MODE.document:
            if self.ogtDoc == None:
                return 0
            return self.ogtDoc.errors_count()

        if self.mode == VIEW_ERR_MODE.group:
            if self.ogtGroup == None:
                return 0
            return self.ogtGroup.errors_count()
        panic____()

    def data(self, midx, role=Qt.DisplayRole):
        """Returns the data at the given index"""
        ridx = midx.row()
        cidx = midx.column()
        print "--------------"
        ## Get a list of errors (to do is generator)
        if self.mode == VIEW_ERR_MODE.document:
            errors = self.ogtDoc.errors_list()
        elif self.mode == VIEW_ERR_MODE.group:
            #print "group_errors"
            errors = self.ogtGroup.errors_list()
        else:
            pamnic___()

        #print "type=", type(errors), errors
        #print ridx, cidx, err_row, self
        """
        if cidx + 1 < len(err_row):
            err = err_row[cidx]
        else:
            err = None
        """
        err = errors[ridx]
        print "err=", err
        if role == Qt.DisplayRole:
            #grp = self.ogtDoc.group_by_index(row)
            #print "grp=", grp
            if err == None:
                return "None"
            if cidx == self.C.err:
                return "1"
            if cidx == self.C.description:
                print "m-=", err.message
                return err.message if err.message else "MISS"
            if cidx == self.C.rule:
                return err.rule if err.rule else "-"
            #if col == self.C.data_count:
            #    return grp.data_rows_count()
            return "?%s/%s?" % (ridx, cidx)

        if False and role == Qt.DecorationRole:
            if cidx == self.C.group_code:
                return Ico.icon(Ico.Group)

        if False and role == Qt.FontRole:
            if cidx == self.C.group_code:
                f = QtGui.QFont()
                f.setBold(True)
                return f

        if False and role == Qt.TextAlignmentRole:
            return Qt.AlignRight if col == 0 else Qt.AlignLeft

        if False and role == Qt.BackgroundColorRole:
            #print self.ogtGroup.data_cell(index.row(), index.column())
            cell = self.ogtDoc.group_by_index(row)[col]
            #bg = cell.get_bg()
            if len(self.ogtGroup.data_cell(row, col).errors) > 0:
                print bg, self.ogtGroup.data_cell(row, col).errors
            return QtGui.QColor(bg)


        return None # QtCore.QVariant()


    def headerData(self, idx, orient, role=None):
        if role == Qt.DisplayRole and orient == Qt.Horizontal:
            return QtCore.QVariant(self._col_labels[idx])

        if role == Qt.TextAlignmentRole and orient == Qt.Horizontal:
            return Qt.AlignRight if idx == 0 else Qt.AlignLeft

        return QtCore.QVariant()


class C_ERR:
    """Columns for examples"""
    err = 0
    lidx = 1
    cidx = 2
    rule = 3
    highlight = 4
    descr = 5
    search = 6

class VIEW_ERR_MODE:
    document = "document"
    group = "group"
    #heading = "heading"

class OGTErrorsWidget( QtGui.QWidget ):

    sigGotoSource = pyqtSignal(int, int)
    sigErrorsFilter = pyqtSignal(bool, bool)



    def __init__( self, parent=None, mode=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False
        self.mode = mode
        if self.mode == None:
            freak_out()

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        self.toolBar = QtGui.QToolBar()
        self.mainLayout.addWidget(self.toolBar)

        self.buttGroupFilters = QtGui.QButtonGroup(self)
        self.buttGroupFilters.setExclusive(False)

        self.buttWarnings = xwidgets.XToolButton(text="Show Warnings", checkable=True, checked=True)
        self.buttGroupFilters.addButton(self.buttWarnings)

        self.buttErrors = xwidgets.XToolButton(text="Show Errors", checkable=True, checked=True)
        self.buttGroupFilters.addButton(self.buttErrors)

        self.buttGroupFilters.buttonClicked.connect(self.on_update_filter)

        self.toolBar.addWidget(self.buttWarnings)
        self.toolBar.addWidget(self.buttErrors)

        #=============================
        ## Set up tree
        self.tree = QtGui.QTreeView()
        self.mainLayout.addWidget(self.tree, 30)

        self.model = ErrorsListModel(mode=self.mode)
        self.tree.setModel(self.model)

        self.tree.setRootIsDecorated(False)
        self.tree.header().setStretchLastSection(True)
        #self.tree.setSortingEnabled(True)

        """
        hi = self.tree.headerItem()
        hi.setText(C_ERR.err, "Type")
        hi.setText(C_ERR.lidx, "Line")
        hi.setText(C_ERR.cidx, "Col")
        hi.setText(C_ERR.rule, "Rule")
        hi.setText(C_ERR.highlight, "Rule")
        hi.setText(C_ERR.descr, "Description")
        hi.setText(C_ERR.search, "search")
        """

        self.tree.setColumnHidden(C_ERR.err, True)
        self.tree.setColumnHidden(C_ERR.search, True)
        self.tree.setColumnWidth(C_ERR.lidx, 30)
        self.tree.setColumnWidth(C_ERR.cidx, 30)
        self.tree.setColumnWidth(C_ERR.rule, 50)
        self.tree.setColumnWidth(C_ERR.highlight, 8)

        #self.tree.itemClicked.connect(self.on_tree_item_clicked)

    def clear(self):
        print "clear", self #self.tree.clear()

    def set_group(self, ogtGroup):

        self.model.set_group(ogtGroup)

    def load_document(self, ogtDoc):
        print "load_codument", self
        #self.model.load_document(ogtDoc)
        return

        errrs = ogtDoc.get_errors_list()
        if len(errrs) == 0:
            item = xwidgets.XTreeWidgetItem()
            item.set(C_ERR.descr, "Yipee! no errors :-)", bg="#D5FF71")
            item.setFirstColumnSpanned(True)
            self.tree.addTopLevelItem(item)
            return

        for er in errrs:

            item = xwidgets.XTreeWidgetItem()
            item.set(C_ERR.err, "1" if er.type else "0")
            item.set(C_ERR.descr, er.message, bg=er.bg )
            item.set(C_ERR.lidx, er.line_no, align=Qt.AlignCenter)
            item.set(C_ERR.cidx, er.column_no, align=Qt.AlignCenter)
            item.set(C_ERR.rule, "-" if er.rule == None else er.rule, align=Qt.AlignCenter)
            item.set(C_ERR.search, "%s-%s" % (er.lidx, er.cidx) )
            self.tree.addTopLevelItem(item)

        self.on_show_warnings(sig=False)
        self.on_show_errors(sig=False)


    def on_tree_item_clicked(self, item, col):
        lidx = item.i(C_ERR.lidx) - 1
        cidx = item.i(C_ERR.cidx) - 1
        if lidx == None and cidx == None:
            return
        self.sigGotoSource.emit(lidx, cidx)


    def select_items(self, ridx, cidx):
        #print "select_items", ridx, cidx
        self.tree.blockSignals(True)

        # clear selection and  hightlight colors
        self.tree.clearSelection()
        root = self.tree.invisibleRootItem()
        for i in range(0, root.childCount()):
            root.child(i).set_bg(C_ERR.highlight, "white")

        if ridx != None and cidx != None:
            # search and hightlight row/col if any
            search = "%s-%s" % (ridx, cidx)
            items = self.tree.findItems(search, Qt.MatchExactly, C_ERR.search)
            if len(items) > 0:
                for item in items:
                    item.set_bg(C_ERR.highlight, "purple")
        self.tree.blockSignals(False)

    def on_update_filter(self):
        self.on_show_warnings()
        self.on_show_errors()
        self.emit_filters_sig()

    def on_show_warnings(self, sig=True):
        return
        hidden = self.buttWarnings.isChecked() == False
        root = self.tree.invisibleRootItem()
        self.tree.setUpdatesEnabled(False)
        for ridx in range(0, root.childCount()):
            if str(root.child(ridx).text(C_ERR.err)) == "0":
                root.child(ridx).setHidden(hidden)
        self.tree.setUpdatesEnabled(True)
        if sig:
            self.emit_filters_sig()

    def on_show_errors(self, sig=True):
        return
        hidden = self.buttErrors.isChecked() == False
        root = self.tree.invisibleRootItem()
        self.tree.setUpdatesEnabled(False)
        for ridx in range(0, root.childCount()):
            if str(root.child(ridx).text(C_ERR.err)) == "1":
                root.child(ridx).setHidden(hidden)
        self.tree.setUpdatesEnabled(True)
        if sig:
            self.emit_filters_sig()

    def emit_filters_sig(self):
        self.sigErrorsFilter.emit(self.buttWarnings.isChecked(), self.buttErrors.isChecked())

    def get_error_filters(self):
        return self.buttWarnings.isChecked(), self.buttErrors.isChecked()


class HelpDialog(QtGui.QDialog):
    debug = False

    def __init__(self, parent=None, page=None):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle("Help")
        self.setWindowIcon(dIco.icon(dIco.Help))

        # self.setWindowFlags(QtCore.Qt.Popup)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.setMinimumWidth(900)
        self.setMinimumHeight(700)

        # self.setStyleSheet("border: 1px solid black;")

        outerLayout = QtGui.QVBoxLayout()
        outerLayout.setSpacing(0)
        margarine = 0
        outerLayout.setContentsMargins(margarine, margarine, margarine, margarine)
        self.setLayout(outerLayout)

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.setSpacing(0)
        margarine = 0
        mainLayout.setContentsMargins(margarine, margarine, margarine, margarine)
        outerLayout.addLayout(mainLayout)

        self.helpWidget = HelpWidget.HelpWidget(page=page)
        mainLayout.addWidget(self.helpWidget)

    # if page:
    #	self.show_page(page)

    def show_page(self, page):
        self.helpWidget.load_page(page)
        self.exec_()



#import mistune
#from help import DOCS_PATH, DOCS_CONTENT

class C:
    node = 0
    page = 1


class HelpWidget(QtGui.QWidget):
    def __init__(self, parent=None, page=None):
        QtGui.QWidget.__init__(self, parent)

        self.debug = False

        outerLayout = QtGui.QVBoxLayout()
        outerLayout.setSpacing(0)
        margarine = 0
        outerLayout.setContentsMargins(margarine, margarine, margarine, margarine)
        self.setLayout(outerLayout)

        self.lblTitle = QtGui.QLabel()
        self.lblTitle.setText("Help")
        self.lblTitle.setStyleSheet("background-color: #333333; color: #999999; font-size: 19pt; padding: 4px; ")
        outerLayout.addWidget(self.lblTitle, 0)

        outerLayout.addSpacing(5)

        self.splitter = QtGui.QSplitter()
        outerLayout.addWidget(self.splitter, 100)

        ## Contents Tree
        self.tree = QtGui.QTreeWidget()
        self.splitter.addWidget(self.tree)
        hi = self.tree.headerItem()
        hi.setText(C.node, "File")
        hi.setText(C.page, "Page")

        self.tree.setColumnHidden(C.page, not self.debug)
        self.tree.header().setStretchLastSection(True)
        self.tree.setUniformRowHeights(True)

        self.tree.setFixedWidth(200)
        self.tree.itemSelectionChanged.connect(self.on_tree_selection)

        ## Tab Widget
        self.tabWidget = QtGui.QTabWidget()
        self.splitter.addWidget(self.tabWidget)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.on_tab_close_requested)
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)

        self.load_content_tree()

    def load_content_tree(self):

        self.tree.clear()
        self.tree.setUpdatesEnabled(False)

        item = TreeWidgetItem()
        item.set(C.node, "Index", ico=dIco.HelpPage)

        item.setText(C.page, "index.md")
        self.tree.addTopLevelItem(item)

        rootNode = self.tree.invisibleRootItem()
        self.load_dir_node(rootNode, DOCS_CONTENT)

        self.tree.setUpdatesEnabled(True)

    def load_dir_node(self, pItem, pth):

        files = os.listdir(pth)

        for f in sorted(files):
            xpth = os.path.join(pth, f)[len(DOCS_CONTENT):]
            # print f, xpth
            if f == "index.md" and pth == DOCS_CONTENT:
                continue
            if os.path.isdir(f):
                item = TreeWidgetItem(pItem)
                item.set(C.node, f, ico=dIco.Folder)
                item.setText(C.page, xpth)

                self.load_dir_node(item, os.path.join(pth, f))
                self.tree.setItemExpanded(item, True)

            elif f.endswith(".md"):
                item = TreeWidgetItem(pItem)
                item.set(C.node, self.title_from_filename(f), ico=dIco.HelpPage)
                item.setText(C.page, xpth)

    def dpage_path_fn(self, page):
        if page.endswith(".md"):
            "%s.md" % page
        read_fn = os.path.join(DOCS_CONTENT, page)
        # if self.debug:
        #	print "file_req=", read_fn, self.docs_root()
        if not os.path.exists(read_fn):
            print "ERROR: FILE not exits", read_fn
            return

    def title_from_filename(self, fn):
        fn = os.path.basename(fn)
        if fn.endswith(".md"):
            fn = fn[0:-3]
        return fn.replace("_", " ").title()

    def select_page(self, page):
        if self.debug:
            print "select_page", page, self.tabWidget.count()
        idx = None
        if self.tabWidget.count() == 0:
            return idx
        ## check page is aleady loaded, and select
        for i in range(0, self.tabWidget.count()):
            if self.debug:
                print "i=", i, self.tabWidget.widget(i).page, page, self.tabWidget.widget(i).page == page
            if self.tabWidget.widget(i).page == page:
                self.tabWidget.blockSignals(True)
                self.tabWidget.setCurrentIndex(i)
                self.tabWidget.blockSignals(False)
                idx = i
                if self.debug:
                    print "idx=", idx
                break
        items = self.tree.findItems(page, Qt.MatchExactly | Qt.MatchRecursive, C.page)
        if len(items) > 0:
            self.tree.blockSignals(True)
            self.tree.setCurrentItem(items[0])
            self.tree.blockSignals(False)
        if self.debug:
            print "items=", idx, items
        return idx

    def load_page(self, page):
        print "load_page=", page, type(page)
        page = str(page)

        full_path = DOCS_CONTENT + page
        if self.debug:
            print "------------------\nload_page=", page, full_path
        if os.path.isdir(full_path):
            return
        elif not page.endswith(".md"):
            full_path = full_path + ".md"

        idx = self.select_page(page)
        if idx != None:
            return

        if not os.path.exists(full_path):
            # print "ERROR: FILE not exits", full_path
            return

        container = G.ut.read_file(os.path.join(DOCS_PATH, "templates", "help_container.html"))

        txt = G.ut.read_file(full_path)
        html = mistune.markdown(txt, escape=False)

        out_html = container.replace("##++CONTENT++##", html)

        self.tabWidget.blockSignals(True)
        if self.debug:
            print "## create view"
        webView = HelpPageView()
        nidx = self.tabWidget.addTab(webView, self.title_from_filename(page))
        webView.set_data(page, out_html)
        self.tabWidget.setTabIcon(nidx, dIco.icon(dIco.HelpPage))

        webView.sigPageLinkClicked.connect(self.load_page)

        self.tabWidget.setCurrentIndex(nidx)
        self.select_tree_node(page)
        if self.debug:
            print "## view done"
        self.tabWidget.blockSignals(False)

    def on_tree_selection(self):
        item = self.tree.currentItem()
        if item == None:
            return
        self.load_page(item.s(C.page))

    def on_tab_close_requested(self, idx):
        if self.debug:
            print "on_tab_close_requested", idx
        self.tabWidget.removeTab(idx)

    def on_tab_changed(self, nidx):
        if nidx == -1:
            self.tree.blockSignals(True)
            self.tree.clearSelection()
            self.tree.blockSignals(False)
            return
        page = self.tabWidget.widget(nidx).page
        self.select_tree_node(page)

    def select_tree_node(self, page, block=True):

        self.tree.blockSignals(True)
        items = self.tree.findItems(page, Qt.MatchExactly | Qt.MatchRecursive, C.page)
        if self.debug:
            print "select_tree_node", page, items
        if len(items) > 0:
            self.tree.setCurrentItem(items[0])
        else:
            # page not in menu
            pass  # print ere
        self.tree.blockSignals(False)


class HelpPageView(QtGui.QWidget):
    sigPageLinkClicked = pyqtSignal(str)

    def __init__(self, parent=None, page=None):
        QtGui.QWidget.__init__(self, parent)

        self.debug = False
        self.page = None

        lay = QtGui.QVBoxLayout()
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)

        self.webView = QtWebKit.QWebView()
        lay.addWidget(self.webView, 2)

        if self.debug:
            page = self.webView.page()
            page.settings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
            # elf.webView.settings().globalSettings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)

            self.webInspector = QtWebKit.QWebInspector(self)
            self.webInspector.setPage(page)
            lay.addWidget(self.webInspector, 3)

        self.webView.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.webView.linkClicked.connect(self.on_link_clicked)

    def set_data(self, page, html):
        self.page = page
        base_url = QtCore.QUrl.fromLocalFile(DOCS_PATH + "/")
        # bu.setScheme("file")
        # print "  > out stuff=", base_url.toString(), base_url.isValid()
        self.webView.setHtml(html, base_url)

    def on_link_clicked(self, url):
        page = str(url.path())[1:]
        # print url,  page, type(page)
        self.sigPageLinkClicked.emit(page)
