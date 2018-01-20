# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""
import os
import sys


from Qt import Qt, QtGui, QtCore

import app_globals as G

import ags4_widgets
import ags4_models
import www_client
import settings
import ogtgui_widgets
import ogtgui_project
from img import Ico


class MainWindow( QtGui.QMainWindow ):
    """Inherited by all other main windows"""

    @staticmethod
    def show_splash():

        splashImage = QtGui.QPixmap( "../images/splash.png" )
        splashScreen = QtGui.QSplashScreen( splashImage )
        splashScreen.showMessage( "  Loading . . ." )
        splashScreen.show()
        return splashScreen


    def __init__( self, args ):
        QtGui.QMainWindow.__init__( self )

        # ===========================================
        # Bit hacky, but sticking stuff in Globals :ref:`app_globals`
        # and initialising stuff
        G.mainWindow = self
        G.args = args # command args

        G.settings = settings.XSettings(self)

        self.server = www_client.ServerConnection( self )
        self.server.response.connect( self.on_www_request_finished )
        G.server = self.server

        G.ags = ags4_models.AgsObject()


        ##===============================================
        # Main window stuff
        self.setObjectName("OGTMainWindow")
        QtGui.QApplication.setStyle( QtGui.QStyleFactory.create( 'Cleanlooks' ) )
        self.setWindowTitle("Open GeoTechnical Desktop - %s" % G.version)
        self.setWindowIcon(Ico.icon(Ico.FavIcon))


        ##=================================================
        ## Le Menu's
        ## Warning.. meniw = woman in welsh.. Joke is.. do u want the menu ? no. food first and then afters

        #=======
        ## File
        self.menuFile = self.menuBar().addMenu("File")
        self.actionQuit = self.menuFile.addAction(Ico.icon(Ico.Quit), "Quit", self.on_quit)


        #=======
        self.menuViews = self.menuBar().addMenu("View")
        self.actionAgs4Browse = self.menuViews.addAction(Ico.icon(Ico.Ags4), "AGS4 data dict", self.on_ags4_browse)
        self.actionAgs4Browse.setCheckable(True)

        self.actionAgs3Browse = self.menuViews.addAction(Ico.icon(Ico.Ags4), "AGS 3: data dict", self.on_ags3_browse)
        self.actionAgs3Browse.setCheckable(True)
        self.actionAgs3Browse.setDisabled(True)

        #=======
        ## Examples - its an example widget within
        self.menuExamples = self.menuBar().addMenu("Examples")

        self.widgetActionExamples = QtGui.QWidgetAction(self.menuExamples)
        self.examplesWidget = ogtgui_widgets.ExamplesWidget(self)
        self.examplesWidget.setMinimumHeight(600)
        self.widgetActionExamples.setDefaultWidget(self.examplesWidget)
        self.examplesWidget.sigLoadFile.connect(self.load_ags4_file)

        self.actionExamples = self.menuExamples.addAction(self.widgetActionExamples)

        ##===========================
        ## Top Bar
        self.toolBar = QtGui.QToolBar()
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolBar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.toolBar.addAction(self.actionAgs4Browse)

        self.toolBar.addSeparator()

        self.toolBar.addAction(self.actionQuit)

        self.toolBar.addSeparator()


        ### add a Banner for coolnees...
        self.lblBanner = QtGui.QLabel()
        self.lblBanner.setText("Open GeoTechnical")
        self.lblBanner.setAlignment(Qt.AlignRight)
        self.lblBanner.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)

        sty = "font-style:italic; font-weight: bold;  color: #187300; margin: 0; font-size: 20pt; font-family: arial;"
        sty += "padding: 5px;"
        sty += "background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, "
        sty += "stop: 0 #eeeeee "
        sty += ", stop: 0.2 #F7FB93 "
        sty += "stop: 1 #FCFFBB"
        sty += ");"
        self.lblBanner.setStyleSheet(sty)
        self.toolBar.addWidget(self.lblBanner)



        ##===============================================
        ## Central widget contains  tabBar and a stack
        centralWidget = QtGui.QWidget()
        centralLayout = QtGui.QVBoxLayout()
        centralLayout.setContentsMargins(0, 0, 0, 0)
        centralLayout.setSpacing(0)
        centralWidget.setLayout(centralLayout)
        self.setCentralWidget(centralWidget)

        self.tabBar = QtGui.QTabBar()
        self.tabBar.setMovable(False)
        self.tabBar.setTabsClosable(True)
        centralLayout.addWidget(self.tabBar)
        self.tabBar.currentChanged.connect(self.on_tab_changed)
        self.tabBar.tabCloseRequested.connect(self.on_tab_close_requested)

        self.stackWidget = QtGui.QStackedWidget()
        centralLayout.addWidget(self.stackWidget)



        #=========================================
        # Seutp basic window dims, and restore
        self.setMinimumWidth(800)
        self.setMinimumHeight(800)
        G.settings.restore_window( self )

        ## run some stuff a few moments after window shown
        QtCore.QTimer.singleShot(200, self.on_after)


    def on_after(self):
        #self.examplesWidget.load()
        print "on_after", self, G.args.dev
        #self.on_ags4_browse()

        #G.Ags.load()
        if G.args.dev:
            self.on_ags4_browse()



        fnn = "/home/ags/ags-play/example_files/pete_stuff/example_schedule.ags"
        if os.path.exists(fnn):
            self.load_ags4_file(fnn)




    def load_widget(self, widget, label, ico=None):

        idx = self.tabBar.addTab(label)
        self.stackWidget.addWidget(widget)
        self.tabBar.setTabIcon(idx, Ico.icon(ico))

        self.tabBar.setCurrentIndex(self.tabBar.count() - 1)
        self.stackWidget.setCurrentIndex(self.stackWidget.count() - 1)

        widget.init()

    def on_www_request_finished(self, xreply):
        #print xreply
        ## we loop though all the widgets and load_reply
        ## More than one widget may be interested in data
        for i in range(0, self.stackWidget.count()):
            self.stackWidget.widget(i).load_reply(xreply)

    def closeEvent( self, event ):
        G.settings.save_window( self )

    def on_quit(self):
        ret = QtGui.QMessageBox.warning( self, "Desktop", "Sure you want to Quit ?", QtGui.QMessageBox.No | QtGui.QMessageBox.Yes )
        if ret == QtGui.QMessageBox.Yes:
            G.settings.save_window(  self )
            sys.exit( 0 )

    def on_show_examples(self):
        chk = self.buttExamples.isChecked()
        self.dockExamples.setVisible(chk)

    def load_ags4_file(self, file_path):

        print "load_ags4_file", file_path, self
        proj = ogtgui_project.OGTProjectWidget()
        proj.load_ags4_file(file_path)

        self.load_widget(proj, os.path.basename(file_path), ico=Ico.Project)
        self.menuExamples.close()

    def on_tab_changed(self, idx):
        self.stackWidget.setCurrentIndex(idx)

    def set_action_checked(self, act, state):
        act.blockSignals(True)
        act.setChecked(state)
        act.blockSignals(False)

    def on_tab_close_requested(self, idx):

        widget = self.stackWidget.widget(idx)

        if isinstance(widget, ags4_widgets.AGS4_DataDictBrowser):
            self.set_action_checked(self.actionAgs4Browse, False)

        self.tabBar.removeTab(idx)
        self.stackWidget.removeWidget( widget )

    def on_ags4_browse(self):
        """Opens or switches to the :ref:`ags4_data_dict`"""
        for idx in range(0, self.stackWidget.count()):
            if isinstance(self.stackWidget.widget(idx), ags4_widgets.AGS4DataDictBrowser):
                self.stackWidget.setCurrentIndex(idx)
                self.tabBar.setCurrentIndex(idx)
                self.set_action_checked(self.actionAgs4Browse, True)
                return

        # create new instance
        browseWidget = ags4_widgets.AGS4DataDictBrowser()
        self.load_widget(browseWidget, "AGS4 Data Dict", ico=Ico.Ags4)
        self.set_action_checked(self.actionAgs4Browse, True)


    def on_ags3_browse(self):
        """

        .. todo:: :term:`ags3` browser


        """
        print "TODO", "on_ags3_browse", self
