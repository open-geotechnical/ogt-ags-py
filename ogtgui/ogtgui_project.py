# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

from Qt import QtGui, QtCore, Qt, pyqtSignal


from ogt import FORMATS
from ogt import ogt_doc

from . import ogtgui_doc
from . import ogtgui_widgets
from .img import Ico
from . import xwidgets

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
        self.lblHeader.setStyleSheet("background-color: green; color: white; font-size: 14pt; padding: 3px 5px;")
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
        self.tabBar.addTab(Ico.icon(Ico.Groups), "Tables")
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


        #self.tabBar.setCurrentIndex(1)

    def init(self):
        pass

    def on_tab_changed(self, idx):
        self.stackWidget.setCurrentIndex(idx)



    def load_ags4_file(self, file_path):

        #self.file_path = None
        """
        self.doc, err = ogt_doc.OGTDocument()
        err = self.doc.load_from_ags4_file(file_path)
        #print "err=", err
        """
        self.ogtDoc, err = ogt_doc.create_doc_from_ags4_file(file_path)
        proj = self.ogtDoc.proj_dict()
        print "proj=", proj
        self.lblHeader.setText(proj['PROJ_NAME'])

        self.ogtDocWidget.load_document(self.ogtDoc)
        self.ogtScheduleWidget.load_document(self.ogtDoc)
        self.ogtSourceViewWidget.load_document(self.ogtDoc)




class OGTProjectSummaryWidget( QtGui.QMainWindow ):

    sigUpdated = pyqtSignal(object)

    def __init__( self, parent=None):
        QtGui.QMainWindow.__init__( self, parent )

        self.debug = False

        self.file_path = None
        self.doc = None



        self.docProject = QtGui.QDockWidget()
        self.docProject.setWindowTitle("Project")
        self.docProject.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.docProject.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.docProject)

        self.lblProjectPlace = QtGui.QLabel()
        self.lblProjectPlace.setText("project placeholder")

        self.docProject.setWidget(self.lblProjectPlace)
