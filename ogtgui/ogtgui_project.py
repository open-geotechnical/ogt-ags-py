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

        self.topLay = xwidgets.hlayout()
        self.mainLayout.addLayout(self.topLay)


        self.lblHeader = QtGui.QLabel()
        self.lblHeader.setStyleSheet("background-color: black; color: #dddddd; font-size: 14pt; padding: 3px 5px;")
        self.topLay.addWidget(self.lblHeader, 100)

        self.buttActAdd = xwidgets.XToolButton(text="Add..", ico=Ico.Add, menu=True, popup=True)
        self.topLay.addWidget(self.buttActAdd)

        self.buttImport = xwidgets.XToolButton(text="Import", ico=Ico.Import, menu=True, popup=True)
        self.topLay.addWidget(self.buttImport)

        self.buttImport.menu().addAction("Add default PROJ, UNIT, etc groups", self.on_add_default_groups)

        self.buttExport = xwidgets.XToolButton(text="Export", ico=Ico.Export, menu=True, popup=True)
        self.topLay.addWidget(self.buttExport)

        for a in FORMATS:
            self.buttExport.menu().addAction("%s - TODO" % a)

        self.buttReload = xwidgets.XToolButton(text="Reload", ico=Ico.Refresh, popup=True, callback=self.on_reload)
        #self.buttReload.setText("Relaod")
        #self.buttReload.setIcon(Ico.icon(Ico.Refresh))
        #self.buttReload.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        #self.buttReload.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.topLay.addWidget(self.buttReload)

        self.mainLayout.addSpacing(5)

        self.tabBar = QtGui.QTabBar()
        f = self.tabBar.font()
        f.setBold(True)
        self.tabBar.setFont(f)
        self.mainLayout.addWidget(self.tabBar)

        self.stackWidget = QtGui.QStackedWidget()
        self.mainLayout.addWidget(self.stackWidget)

        self.tabBar.addTab(Ico.icon(Ico.Summary), "Summary")
        self.ogtProjSummaryWidget = OGTProjectSummaryWidget()
        self.stackWidget.addWidget(self.ogtProjSummaryWidget)
        self.ogtProjSummaryWidget.sigGoto.connect(self.on_goto)
        self.ogtProjSummaryWidget.sigGotoSource.connect(self.on_goto_source)

        ## add tables tab
        self.tabBar.addTab(Ico.icon(Ico.Groups), "Groups")
        self.ogtDocWidget = ogtgui_doc.OGTDocumentWidget()
        self.stackWidget.addWidget(self.ogtDocWidget)

        self.tabBar.addTab(Ico.icon(Ico.Schedule), "Schedule")
        self.ogtScheduleWidget = ogtgui_widgets.OGTScheduleWidget()
        self.stackWidget.addWidget(self.ogtScheduleWidget)

        ## add Sources tab
        self.tabBar.addTab(Ico.icon(Ico.Source), "Source")
        self.ogtSourceViewWidget = ogtgui_widgets.OGTSourceViewWidget()
        self.stackWidget.addWidget(self.ogtSourceViewWidget)




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
        proj = self.ogtDoc.proj_dict()
        print "proj=", proj, self
        self.lblHeader.setText(proj['PROJ_NAME'])

        self.ogtDocWidget.load_document(self.ogtDoc)
        return
        self.ogtScheduleWidget.load_document(self.ogtDoc)
        self.ogtSourceViewWidget.load_document(self.ogtDoc)
        self.ogtProjSummaryWidget.load_document(self.ogtDoc)

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



        self.model = None

        #self.tree = QtGui.QTreeView()
        #self.tree.setModel(QtGui.QStandardItemModel())
        self.tree = QtGui.QTreeWidget()
        self.tree.setRootIsDecorated(False)
        self.tree.header().setStretchLastSection(True)
        self.setCentralWidget(self.tree)




        hi = self.tree.headerItem()
        hi.setText(CP.group_code, "Group")
        hi.setText(CP.group_description, "Description")
        hi.setText(CP.node, "Rows")
        hi.setTextAlignment(CP.node, Qt.AlignRight)
        self.tree.itemDoubleClicked.connect(self.on_tree_double_clicked)


        self.dockGroups.setWidget(self.tree)

        self.tree.setColumnWidth(CP.node, 40)
        self.tree.setColumnWidth(CP.group_code, 70)
        self.tree.setMinimumWidth(300)


        centralWidget = QtGui.QWidget()
        centralLay = xwidgets.vlayout()
        centralWidget.setLayout(centralLay)

        self.setCentralWidget(centralWidget)

        lbl = QtGui.QLabel()
        lbl.setText("Errors and Warnings")
        lbl.setStyleSheet("font-weight: bold; padding: 3px; background-color: #eeeeee;")
        centralLay.addWidget(lbl)

        self.errorsWidget = ogtgui_widgets.OGTErrorsWidget()
        centralLay.addWidget(self.errorsWidget)
        self.errorsWidget.sigGotoSource.connect(self.on_goto_source)

    def clear(self):

        self.errorsWidget.clear()
        self.tree.clear()

    def load_document(self, ogtDoc):

       # self.model = OGTProjectsModel()
        #self.model.load_document(ogtDoc)
        self.ogtDoc = ogtDoc
        #self.tree.setModel(self.model)
        #return
        for g in self.ogtDoc.groups_list():
            #print "===", g.group_description
            item = xwidgets.XTreeWidgetItem()

            item.set(CP.group_code, g.group_code, bold=True, ico=Ico.AgsGroup)

            item.set(CP.group_description, g.group_description)

            item.set(CP.node, str(g.data_rows_count()), align=Qt.AlignRight)
            self.tree.addTopLevelItem(item)



        self.errorsWidget.load_document(self.ogtDoc)

    def on_tree_double_clicked(self, item, cidx):
        item = self.tree.currentItem()
        if item == None:
            return
        self.sigGoto.emit(item.text(CP.group_code))

    def on_goto_source(self, lidx, cidx):
        self.sigGotoSource.emit(lidx, cidx)



