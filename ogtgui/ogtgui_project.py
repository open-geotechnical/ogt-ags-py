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

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False

        self.ogtDoc = None

        self.mainLayout = xwidgets.vlayout()
        self.setLayout(self.mainLayout)

        self.topLay = xwidgets.hlayout()
        self.mainLayout.addLayout(self.topLay)


        self.lblHeader = QtGui.QLabel()
        self.lblHeader.setStyleSheet("background-color: black; color: #dddddd; font-size: 14pt; padding: 3px 5px;")
        self.topLay.addWidget(self.lblHeader, 100)

        self.buttExport = QtGui.QToolButton()
        self.buttExport.setText("Export..")
        self.buttExport.setIcon(Ico.icon(Ico.Export))
        self.buttExport.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.buttExport.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.topLay.addWidget(self.buttExport)

        menu =  QtGui.QMenu()
        self.buttExport.setMenu(menu)

        for a in FORMATS:
            menu.addAction("%s - TODO" % a)


        self.mainLayout.addSpacing(5)

        self.tabBar = QtGui.QTabBar()
        f = self.tabBar.font()
        f.setBold(True)
        self.tabBar.setFont(f)
        self.mainLayout.addWidget(self.tabBar)

        self.stackWidget = QtGui.QStackedWidget()
        self.mainLayout.addWidget(self.stackWidget)

        self.tabBar.addTab(Ico.icon(Ico.Project), "Summary")
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
            self.tabBar.setCurrentIndex(3)

    def init_load(self):
        pass

    def on_tab_changed(self, idx):
        self.stackWidget.setCurrentIndex(idx)

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
        #print "err=", err
        """
        self.ogtDoc, err = ogt_doc.create_doc_from_ags4_file(file_path)
        self.load_document()

    def load_document(self):
        proj = self.ogtDoc.proj_dict()
        self.lblHeader.setText(proj['PROJ_NAME'])

        self.ogtDocWidget.load_document(self.ogtDoc)
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

class CP:
    node = 0
    group_code = 1
    group_description = 2


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
        self.dockErrors = QtGui.QDockWidget()
        self.dockErrors.setWindowTitle("Groups")
        self.dockErrors.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.dockErrors.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockErrors)


        self.tree = QtGui.QTreeWidget()
        self.tree.setRootIsDecorated(False)
        self.tree.header().setStretchLastSection(True)
        self.setCentralWidget(self.tree)


        hi = self.tree.headerItem()
        hi.setText(CP.group_code, "Group")
        hi.setText(CP.group_description, "Description")
        hi.setText(CP.node, "Rows")

        self.tree.itemDoubleClicked.connect(self.on_tree_double_clicked)
        self.dockErrors.setWidget(self.tree)

        self.errorsWidget = ogtgui_widgets.OGTErrorsWidget()
        self.setCentralWidget(self.errorsWidget)
        self.errorsWidget.sigGotoSource.connect(self.on_goto_source)

    def load_document(self, ogtDoc):

        self.ogtDoc = ogtDoc

        for g in self.ogtDoc.groups_list():
            #print "===", g.group_description
            item = QtGui.QTreeWidgetItem()

            item.setText(CP.group_code, g.group_code)
            f = item.font(CP.group_code)
            f.setBold(True)
            item.setFont(CP.group_code, f)
            item.setIcon(CP.group_code, Ico.icon(Ico.AgsGroup))

            item.setText(CP.group_description, g.group_description)

            item.setText(CP.node, str(g.data_rows_count()))
            item.setTextAlignment(CP.node, Qt.AlignRight)
            self.tree.addTopLevelItem(item)

        self.errorsWidget.load_document(self.ogtDoc)

    def on_tree_double_clicked(self, item, cidx):
        item = self.tree.currentItem()
        if item == None:
            return
        self.sigGoto.emit(item.text(CP.group_code))

    def on_goto_source(self, lidx, cidx):
        self.sigGotoSource.emit(lidx, cidx)
