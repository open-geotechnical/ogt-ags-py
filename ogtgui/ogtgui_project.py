# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

from Qt import QtGui, QtCore, Qt, pyqtSignal


from ogt import FORMATS
from ogt import ogt_doc

import app_globals as G
import ogtgui_doc
import ogtgui_widgets
from img import Ico
import xwidgets

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


        self.tabBar.addTab(Ico.icon(Ico.Project), "Summary")
        self.ogtProjSummaryWidget = OGTProjectSummaryWidget()
        self.stackWidget.addWidget(self.ogtProjSummaryWidget)


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


class PC:
    node = 0
    group_code = 1
    group_description = 1


class OGTProjectSummaryWidget( QtGui.QMainWindow ):

    sigUpdated = pyqtSignal(object)

    def __init__( self, parent=None):
        QtGui.QMainWindow.__init__( self, parent )

        self.debug = False

        self.file_path = None
        self.ogtDoc = None



        self.docProject = QtGui.QDockWidget()
        self.docProject.setWindowTitle("Project")
        self.docProject.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.docProject.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.docProject)


        self.lblProjectPlace = QtGui.QLabel()
        self.lblProjectPlace.setText("project placeholder")

        self.docProject.setWidget(self.lblProjectPlace)


        self.tree = QtGui.QTreeWidget()
        self.tree.setRootIsDecorated(False)
        self.setCentralWidget(self.tree)


        hi = self.tree.headerItem()
        hi.setText(PC.group_code, "Group")
        hi.setText(PC.group_description, "Description")
        hi.setText(PC.node, "Rows")


    def load_document(self, ogtDoc):

        self.ogtDoc = ogtDoc

        for g in self.ogtDoc.groups_list():
            print g.group_description
            item = QtGui.QTreeWidgetItem()

            item.setText(PC.group_code, g.group_code)
            f = item.font(PC.group_code)
            f.setBold(True)
            item.setFont(PC.group_code, f)
            item.setIcon(PC.group_code, Ico.icon(Ico.AgsGroup))

            item.setText(PC.group_description, g.group_description)

            item.setText(PC.node, str(g.data_rows_count()))
            item.setTextAlignment(PC.node, Qt.AlignRight)
            self.tree.addTopLevelItem(item)

