# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

from Qt import QtGui, QtCore, Qt, pyqtSignal


from ogt import FORMATS
from ogt import ogt_doc

import app_globals as G

from img import Ico
import xwidgets

import ogtgui_doc
import ogtgui_groups
import ogtgui_widgets
import map_widgets

class OGTProjectWidget( QtGui.QWidget ):

    sigUpdated = pyqtSignal(object)

    def __init__( self, parent=None, empty=False):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False

        self.ogtDoc = None
        if empty:
            self.ogtDoc = ogt_doc.OGTDocument()

        self.mainLayout = xwidgets.vlayout()
        self.setLayout(self.mainLayout)

        ##====== Top Bar ===
        self.topLay = xwidgets.hlayout()
        self.mainLayout.addLayout(self.topLay)

        ## Header Label
        self.lblHeader = QtGui.QLabel()
        self.lblHeader.setStyleSheet("background-color: #444444; color: #dddddd; font-size: 14pt; padding: 3px 5px;")
        self.topLay.addWidget(self.lblHeader, 100)

        ## Add button
        self.buttActAdd = xwidgets.XToolButton(text="Add..", ico=Ico.Add, menu=True, popup=True)
        self.topLay.addWidget(self.buttActAdd)

        ## Import button
        self.buttImport = xwidgets.XToolButton(text="Import", ico=Ico.Import, menu=True, popup=True)
        self.topLay.addWidget(self.buttImport)
        self.buttImport.menu().addAction("Add default PROJ, UNIT, etc groups", self.on_add_default_groups)

        ## Export button
        self.buttExport = xwidgets.XToolButton(text="Export", ico=Ico.Export, menu=True, popup=True)
        self.topLay.addWidget(self.buttExport)
        for a in FORMATS:
            self.buttExport.menu().addAction("%s - TODO" % a)

        ## Reload button
        self.buttReload = xwidgets.XToolButton(text="Reload", ico=Ico.Refresh, popup=True, callback=self.on_reload)
        self.topLay.addWidget(self.buttReload)

        self.mainLayout.addSpacing(5)

        ##========= Content ===============

        ## tabar + Stack
        self.tabBar = QtGui.QTabBar()
        f = self.tabBar.font()
        f.setBold(True)
        self.tabBar.setFont(f)
        self.mainLayout.addWidget(self.tabBar)

        self.stackWidget = XStackedWidget() #QtGui.QStackedWidget()
        self.mainLayout.addWidget(self.stackWidget)

        ## Summary Tab
        self.tabBar.addTab(Ico.icon(Ico.Summary), "Summary")
        self.ogtProjSummaryWidget = OGTProjectSummaryWidget()
        self.stackWidget.addWidget(self.ogtProjSummaryWidget, "Project Summary")
        self.ogtProjSummaryWidget.sigGoto.connect(self.on_goto)
        self.ogtProjSummaryWidget.sigGotoSource.connect(self.on_goto_source)

        ## Groups Tab
        self.tabBar.addTab(Ico.icon(Ico.Groups), "Groups")
        self.ogtDocWidget = ogtgui_doc.OGTDocumentWidget()
        nidx = self.stackWidget.addWidget(self.ogtDocWidget, "Groups")

        chk = QtGui.QCheckBox()
        chk.setText("Show Data Count")
        self.stackWidget.addHeaderWidget(nidx, chk)

        ## Schedule Tab
        self.tabBar.addTab(Ico.icon(Ico.Schedule), "Schedule")
        self.ogtScheduleWidget = ogtgui_widgets.OGTScheduleWidget()
        self.stackWidget.addWidget(self.ogtScheduleWidget, "Schedule")

        ## Source tab
        self.tabBar.addTab(Ico.icon(Ico.Source), "Source")
        self.ogtSourceViewWidget = ogtgui_widgets.OGTSourceViewWidget()
        self.stackWidget.addWidget(self.ogtSourceViewWidget, "Sources")


        if False:
            self.tabBar.addTab(Ico.icon(Ico.Map), "Map")
            self.mapOverviewWidget = map_widgets.MapOverviewWidget()
            self.stackWidget.addWidget(self.mapOverviewWidget)


        self.tabBar.currentChanged.connect(self.on_tab_changed)

        if G.args.dev:
            self.tabBar.setCurrentIndex(1)
            pass

    def init_load(self):
        pass

    def on_tab_changed(self, idx):
        self.stackWidget.setCurrentIndex(idx)

    def on_reload(self):

        fp = self.ogtDoc.source_file_path

        self.ogtSourceViewWidget.clear()
        self.ogtDocWidget.clear()

        self.ogtScheduleWidget.clear()
        self.ogtProjSummaryWidget.clear()

        self.ogtDoc = None
        self.load_ags4_file(fp)

    def load_ags4_string(self, contents, file_name):


        self.ogtDoc, err = ogt_doc.create_doc_from_ags4_string(contents, file_name)
        self.load_document()
        #proj = self.ogtDoc.proj_dict()
        #self.lblHeader.setText(proj['PROJ_NAME'])

        #self.ogtDocWidget.load_document(self.ogtDoc)
        #self.ogtScheduleWidget.load_document(self.ogtDoc)
        #self.ogtSourceViewWidget.load_document(self.ogtDoc)

    def load_ags4_file(self, file_path):

        #self.file_path = None
        """
        self.doc, err = ogt_doc.OGTDocument()
        err = self.doc.load_from_ags4_file(file_path)

        """
        self.ogtDoc, err = ogt_doc.create_doc_from_ags4_file(file_path)
        self.load_document()

    def load_document(self):
        proj = None #self.ogtDoc.proj_dict()
        print "proj=", proj, self
        if proj:
            self.lblHeader.setText(proj['PROJ_NAME'])

        self.ogtDocWidget.load_document(self.ogtDoc)
        self.ogtProjSummaryWidget.load_document(self.ogtDoc)

        return
        self.ogtScheduleWidget.load_document(self.ogtDoc)
        self.ogtSourceViewWidget.load_document(self.ogtDoc)


        ## HACK
        QtCore.QTimer.singleShot(4000, self.do_map_after)

    def do_map_after(self):
        self.mapOverviewWidget.load_document(self.ogtDoc)

    def on_goto(self, code):

        self.ogtDocWidget.select_group(code)
        idx = self.stackWidget.indexOf(self.ogtDocWidget)
        self.tabBar.setCurrentIndex(idx)



    def on_goto_source(self, lidx, cidx):

        self.ogtSourceViewWidget.select_cell(lidx, cidx)
        idx = self.stackWidget.indexOf(self.ogtSourceViewWidget)
        self.tabBar.setCurrentIndex(idx)


    def on_add_default_groups(self):

        for g in ogt_doc.GROUPS_REQUIRED:
            self.ogtDoc.add_group(g)

class CP:
    node = 0
    group_code = 1
    group_description = 2



class OGTProjectsModel(QtCore.QAbstractItemModel):

    class C:
        node = 0
        group_code = 1
        group_description = 2

    def __init__( self, parent=None):
        QtCore.QAbstractItemModel.__init__( self, parent )

        self.ogtDoc = None

    def load_document(self, ogtDoc):
        self.ogtDoc = ogtDoc
        self.modelReset.emit()
        print self.ogtDoc, self

    def columnCount(self, pidx):
        return 3

    def headerData(self, p_int, orientation, role=None):
        #print p_int, orientation, role
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            lst = ["Rows", "Group", "Description"]
            return QtCore.QVariant(lst[p_int])
        return QtCore.QVariant()

    def rowCount(self, pidx):
        if self.ogtDoc == None:
            return 0
        if pidx.row() == -1:
            return self.ogtDoc.groups_count()
        print "rowcount", self.ogtDoc.groups_count(), pidx.row(), pidx.column(), pidx
        return 0 #self.ogtDoc.groups_count()

    def index(self, row, col, pidx):
        """
        if not pidx.isValid():
            return self.createIndex(row, col, None)
        parentNode = pidx.internalPointer()
        return self.createIndex(row, col, parentNode.subnodes[row])
        """
        return self.createIndex(row, col, None)
        #return QtCore.QModelIndex()

    def parent(self, index):

        if not index.isValid():
            print "parent index.isValue()  FALSE"
            return QtCore.QModelIndex()
        node = index.internalPointer()
        if node != None and node.parent() is None:
            ss
            return QtCore.QModelIndex()
        else:
            return self.createIndex(0, 0, None)
            return self.createIndex(node.parent.row, 0, node.parent)

        print "parent", child.row(), child.column(), child #, child.parent()
        #return None
        if False: #child.isValid():

            ip =  child.internalPointer()
            print "parent not valid", ip
            if ip:
                print "return"
                #return child.internalPointer().parent()
                return self.createIndex(ip.parent().row(), 0, ip.parent())
            #return QtCore.QModelIndex()
        #return self.createIndex(child.row(), child.column(), None)
        return QtCore.QModelIndex()

    def data(self, midx, role):

        if role == Qt.DecorationRole:
            return QtCore.QVariant()

        if role == Qt.TextAlignmentRole:
            return QtCore.QVariant(int(Qt.AlignTop | Qt.AlignLeft))

        if role != Qt.DisplayRole:
            return QtCore.QVariant()

        #node = self.nodeFromIndex(midx)

        if midx.column() == 0:
            return QtCore.QVariant(self.ogtDoc.group_by_index(midx.row()))

        elif midx.column() == 1:
            return QtCore.QVariant(self.ogtDoc.group_by_index(midx.row()))

        elif midx.column() == 2:
            return QtCore.QVariant(self.ogtDoc.group_by_index(midx.row()))

        return QtCore.QVariant()




class OGTProjectSummaryWidget( QtGui.QMainWindow ):

    sigGoto = pyqtSignal(object)
    sigGotoSource = pyqtSignal(int, int)

    def __init__( self, parent=None):
        QtGui.QMainWindow.__init__( self, parent )

        self.debug = False

        self.file_path = None
        self.ogtDoc = None



        self.dockProject = QtGui.QDockWidget()
        self.dockProject.setWindowTitle("Project")
        self.dockProject.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.dockProject.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockProject)


        self.lblProjectPlace = QtGui.QLabel()
        self.lblProjectPlace.setText("project placeholder")

        self.dockProject.setWidget(self.lblProjectPlace)


        ## Errors
        self.dockGroups = QtGui.QDockWidget()
        self.dockGroups.setWindowTitle("Groups")
        self.dockGroups.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.dockGroups.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockGroups)


        self.groupsListWidget = ogtgui_groups.GroupsListWidget()
        self.dockGroups.setWidget(self.groupsListWidget)

        #self.tree.setMinimumWidth(300)
        #self.tree.setRootIsDecorated(False)
        #self.tree.header().setStretchLastSection(True)
        #self.setCentralWidget(self.tree)

        #self.model = GroupListModel()
        #self.tree.setModel(self.model)

        """
        hi = self.tree.headerItem()
        hi.setText(CP.group_code, "Group")
        hi.setText(CP.group_description, "Description")
        hi.setText(CP.node, "Rows")
        hi.setTextAlignment(CP.node, Qt.AlignRight)
        self.tree.itemDoubleClicked.connect(self.on_tree_double_clicked)
        """



        #self.tree.setColumnWidth(CP.node, 40)
        #self.tree.setColumnWidth(CP.group_code, 70)

        centralWidget = QtGui.QWidget()
        centralLay = xwidgets.vlayout()
        centralWidget.setLayout(centralLay)

        self.setCentralWidget(centralWidget)

        lbl = QtGui.QLabel()
        lbl.setText("Errors and Warnings")
        lbl.setStyleSheet("font-weight: bold; padding: 3px; background-color: #eeeeee;")
        centralLay.addWidget(lbl)

        self.errorsWidget = ogtgui_widgets.OGTErrorsWidget(mode=ogtgui_widgets.VIEW_ERR_MODE.group)
        centralLay.addWidget(self.errorsWidget)
        self.errorsWidget.sigGotoSource.connect(self.on_goto_source)

    def clear(self):

        self.errorsWidget.clear()
        self.tree.clear()

    def load_document(self, ogtDoc):

       # self.model = OGTProjectsModel()
        #self.model.load_document(ogtDoc)
        self.ogtDoc = ogtDoc
        self.groupsListWidget.set_document(self.ogtDoc)
        #self.errorsWidget.load_document(self.ogtDoc)


        return
        for g in self.ogtDoc.groups_list:
            #print "===", g.group_description
            item = xwidgets.XTreeWidgetItem()

            item.set(CP.group_code, g.group_code, bold=True, ico=Ico.AgsGroup)

            item.set(CP.group_description, g.group_description)

            item.set(CP.node, str(g.data_rows_count()), align=Qt.AlignRight)
            #self.tree.addTopLevelItem(item)




    def on_tree_double_clicked(self, item, cidx):
        print "dbk", item, cidx
        item = self.tree.currentItem()
        if item == None:
            return
        self.sigGoto.emit(item.text(CP.group_code))

    def on_goto_source(self, lidx, cidx):
        self.sigGotoSource.emit(lidx, cidx)




class XStackedWidget( QtGui.QWidget ):

    """Psuedo Stack as it containes a header/label and widget"""
    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(4)
        self.setLayout(self.mainLayout)

        self.headerStack = QtGui.QStackedWidget()
        self.mainLayout.addWidget(self.headerStack, 0)

        self.contentStack = QtGui.QStackedWidget()
        self.mainLayout.addWidget(self.contentStack, 100)

    def addWidget(self, widget, header_text, bg="#dddddd"):

        tbar = QtGui.QWidget()
        tlay = QtGui.QHBoxLayout()
        tlay.setContentsMargins(0,0,0,0)
        tlay.setSpacing(0)
        tbar.setLayout(tlay)

        lbl = QtGui.QLabel()
        lbl.setText(header_text)
        sty = " color: #666666; font-size: 14pt; padding: 2px 5px;"
        sty += "background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, "
        sty += "stop: 0 #efefef "
        sty += ", stop: 0.3 #efefef "
        sty += "stop: 1 %s" % bg
        sty += ");"
        lbl.setStyleSheet(sty)
        tlay.addWidget(lbl, 10)

        self.headerStack.addWidget(tbar)

        nidx = self.contentStack.addWidget(widget)

        return nidx

    def setCurrentIndex(self, idx):
        self.headerStack.setCurrentIndex(idx)
        self.contentStack.setCurrentIndex(idx)

    def addHeaderWidget(self, idx, widget):

        wid = self.headerStack.widget(idx)
        wid.layout().addWidget(widget, 0)
