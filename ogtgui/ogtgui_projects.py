# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

from Qt import QtGui, QtCore, Qt, pyqtSignal



from img import Ico
import xwidgets

class OgtHomePortal( QtGui.QWidget ):

    #sigFileSelected = pyqtSignal(object)

    def __init__( self, parent):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False

        self.setMinimumWidth(300)

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        self.projectsWiget = OgtProjectsWidget()
        self.mainLayout.addWidget(self.projectsWiget)

class C_EG:
    """Columns for examples"""
    file_name = 0

class OgtProjectsWidget( QtGui.QWidget ):

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

        self.load_projects()



    def load_projects(self, sub_dir=None):
        return
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
