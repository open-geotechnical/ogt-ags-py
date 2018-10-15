# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""
import os
import sys

from ogt import ags4

from Qt import Qt, QtGui, QtCore

import app_globals as G

import ags4_widgets
import ags4_models
import www_client
import settings
import ogtgui_widgets
import ogtgui_project
import ogtgui_projects
from img import Ico


class MainWindow( QtGui.QMainWindow ):
    """Inherited by all other main windows"""

    def on_after(self):
        #self.examplesWidget.load()
        #print "on_after", self, G.args.dev
        self.on_browse_ags4()

        #G.Ags.load()
        if G.args.dev:
            #self.on_browse_ags4()
            #self.on_new_project()
            pass


        #fnn = "AGS4-Example.ags"
        #self.load_ags4_example(fnn)
        fn =  "/home/ogt/AGS4-example-wrd.ags"
        if G.args.dev:
            fn = "/home/ogt/ags-play/example_files/pete_stuff/pete_tests.ags"
            fn = "/home/geo2lab/z_drive/jobs/40101-40200/40153/AGS/40153 AGS.ags"
            #self.load_ags4_file(fn)

        #w = ogtgui_widgets.ExpPortalWidget()
        #self.load_widget(w, "Experiments")

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

        G.ags = ags4_models.Ags4Object()


        ##===============================================
        # Main window stuff
        self.setObjectName("OGTMainWindow")
        QtGui.QApplication.setStyle( QtGui.QStyleFactory.create( 'Cleanlooks' ) )
        self.setWindowTitle("Open GeoTechnical Desktop - %s" % G.version)
        self.setWindowIcon(Ico.icon(Ico.FavIcon))


        ##=================================================
        ## Menus

        #=======
        ## File
        self.menuFile = self.menuBar().addMenu("File")

        self.actionOpen = self.menuFile.addAction("Open Ags File", self.on_open_ags_file)
        self.actionRecent = self.menuFile.addAction("Recent")
        self.actionRecent.setMenu(QtGui.QMenu())
        self.actionRecent.menu().triggered.connect(self.on_open_recent)
        self.menuFile.addSeparator()

        self.actionNewProject = self.menuFile.addAction(Ico.icon(Ico.Add), "New Project", self.on_new_project)
        self.menuFile.addSeparator()

        #self.actionQuit = self.menuFile.addAction(Ico.icon(Ico.Quit), "Quit", self.on_quit)


        #=======
        ## Projects
        self.menuProjects = self.menuBar().addMenu("Projects")

        self.widgetProjects = QtGui.QWidgetAction(self.menuProjects)
        self.projectsWidget = ogtgui_projects.OgtProjectsWidget(self)
        #self.projectsWidget.setMinimumHeight(600)
        self.widgetProjects.setDefaultWidget(self.projectsWidget)
        #self.examplesWidget.sigFileSelected.connect(self.load_ags4_example)

        self.actionProjects = self.menuProjects.addAction(self.widgetProjects)


        self.actionOpen = self.menuFile.addAction("Open Ags File", self.on_open_ags_file)
        self.actionRecent = self.menuFile.addAction("Recent")
        self.actionRecent.setMenu(QtGui.QMenu())
        self.actionRecent.menu().triggered.connect(self.on_open_recent)
        self.menuFile.addSeparator()

        self.actionNewProject = self.menuProjects.addAction(Ico.icon(Ico.Add), "New Project", self.on_new_project)
        self.menuProjects.addSeparator()

        self.actionQuit = self.menuFile.addAction(Ico.icon(Ico.Quit), "Quit", self.on_quit)

        #=======
        ## View
        self.menuViews = self.menuBar().addMenu("View")
        self.actionAgs4Browse = self.menuViews.addAction(Ico.icon(Ico.Ags4), "AGS4", self.on_browse_ags4)
        self.actionAgs4Browse.setCheckable(True)

        #self.actionAgs3Browse = self.menuViews.addAction(Ico.icon(Ico.Ags4), "AGS 3: data dict", self.on_ags3_browse)
        #self.actionAgs3Browse.setCheckable(True)
        #self.actionAgs3Browse.setDisabled(True)

        #=======
        ## Examples - its an example widget within
        self.menuExamples = self.menuBar().addMenu("Examples")

        self.widgetActionExamples = QtGui.QWidgetAction(self.menuExamples)
        self.examplesWidget = ogtgui_widgets.ExamplesWidget(self)
        self.examplesWidget.setMinimumHeight(600)
        self.widgetActionExamples.setDefaultWidget(self.examplesWidget)
        self.examplesWidget.sigFileSelected.connect(self.load_ags4_example)

        self.actionExamples = self.menuExamples.addAction(self.widgetActionExamples)

        # help meniw (meniw = woman in welsh, eg a cafe.. U want the menu?  no food first ;-))
        self.menuHelp = self.menuBar().addMenu("Help")

        self.menuHelp.addAction("OpenGeotechnical.github.com/ogs-ags-py")

        ##===========================
        ## Top Bar
        self.toolBar = QtGui.QToolBar()
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolBar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.toolBar.addAction(self.actionAgs4Browse)

        self.toolBar.addSeparator()

        #self.toolBar.addAction(self.actionQuit)

        self.toolBar.addSeparator()


        ### add a Banner for coolnees...
        self.lblBanner = QtGui.QLabel()
        self.lblBanner.setText("Open GeoTechnical")
        self.lblBanner.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.lblBanner.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)

        sty = "font-style:italic; font-weight: bold;  color: #444444; margin: 0; font-size: 10pt; font-family: arial;"
        sty += "padding: 2px;"
        if False:
            sty += "background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, "
            sty += "stop: 0 #FFE8CB "
            sty += ", stop: 0.3 #FFD7A4 "
            sty += "stop: 1 #C48C45"
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

        # create a progress dialog and hide
        self.progressDialog = QtGui.QProgressDialog()
        self.progressDialog.setMinimumWidth(300)
        self.progressDialog.setWindowIcon(Ico.icon(Ico.Busy))
        self.progressDialog.setRange(0, 0)
        self.progressDialog.setCancelButton(None)
        self.progressDialog.setModal(True)
        self.progressDialog.hide()

        #=========================================
        # Seutp basic window dims, and restore
        self.setMinimumWidth(800)
        self.setMinimumHeight(800)
        G.settings.restore_window( self )
        self.load_recent()

        ## run some stuff a few moments after window shown
        QtCore.QTimer.singleShot(200, self.on_after)






    def load_widget(self, widget, label, ico=None):

        idx = self.tabBar.addTab(label)
        self.stackWidget.addWidget(widget)
        self.tabBar.setTabIcon(idx, Ico.icon(ico))

        self.tabBar.setCurrentIndex(self.tabBar.count() - 1)
        self.stackWidget.setCurrentIndex(self.stackWidget.count() - 1)

        widget.init_load()

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

    def load_ags4_example(self, file_name):

        self.menuExamples.close()

        data, err = ags4.example(file_name)
        if err:
            pass

        proj = ogtgui_project.OGTProjectWidget()
        proj.load_ags4_string(data['contents'], file_name)

        self.load_widget(proj, file_name, ico=Ico.Project)

    def on_new_project(self):


        projWidget = ogtgui_project.OGTProjectWidget(empty=True)
        self.load_widget(projWidget, "New Project", ico=Ico.Project)

    def load_ags4_file(self, file_path):

        # first check its not open
        for idx in range(0, self.stackWidget.count()):
            #print self.stackWidget.widget(idx)
            if isinstance(self.stackWidget.widget(idx), ogtgui_project.OGTProjectWidget ):
                if self.stackWidget.widget(idx).ogtDoc.source_file_path == file_path:
                    self.tabBar.setCurrentIndex(idx)
                    return

        if False:
            self.progressDialog.setWindowTitle("Loading...")
            self.progressDialog.setLabelText(file_path)
            self.progressDialog.show()

            self.add_history(file_path)
        #print "load_ags4_file", file_path, self
        proj = ogtgui_project.OGTProjectWidget()
        proj.load_ags4_file(file_path)
        #print proj
        self.load_widget(proj, os.path.basename(file_path), ico=Ico.Project)

        if False:
            self.progressDialog.hide()

    def add_history(self, file_path):
        history = G.settings.get_list("history")

        if file_path in history:
            # remove if in history, so insert at top
            history.remove(file_path)
        history.insert(0, file_path)
        if len(history) > 20:
            history = history[0:20]
        G.settings.save_list("history", history)
        self.load_recent()

    def load_recent(self):
        files = G.settings.get_list("history")
        menu = self.actionRecent.menu()
        menu.clear()
        for f in files:
            menu.addAction(f)

    def on_open_recent(self, act):
        fn =  str(act.text())
        self.load_ags4_file(fn)

    def on_tab_changed(self, idx):
        self.stackWidget.setCurrentIndex(idx)

    def set_action_checked(self, act, state):
        act.blockSignals(True)
        act.setChecked(state)
        act.blockSignals(False)

    def on_tab_close_requested(self, idx):

        widget = self.stackWidget.widget(idx)

        if isinstance(widget, ags4_widgets.AGS4DataDictBrowser):
            self.set_action_checked(self.actionAgs4Browse, False)

        self.tabBar.removeTab(idx)
        self.stackWidget.removeWidget( widget )

    def on_browse_ags4(self):
        """Opens or switches to the :ref:`ags4_data_dict`"""

        ## Check it not already there
        for idx in range(0, self.stackWidget.count()):
            if isinstance(self.stackWidget.widget(idx), ags4_widgets.AGS4DataDictBrowser):
                ## its there so switch to
                self.stackWidget.setCurrentIndex(idx)
                self.tabBar.setCurrentIndex(idx)
                self.set_action_checked(self.actionAgs4Browse, True)
                return

        # create new instance
        browseWidget = ags4_widgets.AGS4DataDictBrowser()
        self.load_widget(browseWidget, "AGS4 Data Dict", ico=Ico.Ags4)
        ## set the menu/tbar actions checked
        self.set_action_checked(self.actionAgs4Browse, True)



    def on_open_ags_file(self):

        dial = QtGui.QFileDialog(self, "Select AGS File")
        dial.setFileMode(QtGui.QFileDialog.ExistingFile)
        #dial.setFilter(QtCore.QDir.Files)
        dial.setNameFilters(["Ags Files (*.ags *.ags4)"])

        if dial.exec_():
            fn = str(dial.selectedFiles()[0])
            self.load_ags4_file(fn)



    @staticmethod
    def show_splash():

        splashImage = QtGui.QPixmap( "../images/splash.png" )
        splashScreen = QtGui.QSplashScreen( splashImage )
        splashScreen.showMessage( "  Loading . . ." )
        splashScreen.show()
        return splashScreen
