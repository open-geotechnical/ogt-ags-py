# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

from Qt import QtGui, QtCore, Qt, pyqtSignal



from img import Ico
import xwidgets



class GroupListModel(QtCore.QAbstractTableModel):

    class C:
        data_count = 0
        group_code = 1
        group_description = 2

    def __init__(self):
        QtCore.QAbstractTableModel.__init__(self)

        self.ogtDoc = None

        self._col_labels = ["Data", "Group Code", "Descripton"]

    def set_document(self, ogtDoc):
        self.ogtDoc = ogtDoc
        #self.modelReset.emit()
        #print self.ogtDoc, self

    def columnCount(self, foo):
        #print foo
        return 3

    def rowCount(self, midx):
        #print "rc=", self.ogtDoc.groups_count()
        if self.ogtDoc == None:
            return 0
        return self.ogtDoc.groups_count()

    def data(self, midx, role=Qt.DisplayRole):
        """Returns the data at the given index"""
        row = midx.row()
        col = midx.column()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            grp = self.ogtDoc.group_by_index(row)
            #print "grp=", grp
            if midx.column() == self.C.group_code:
                return grp.group_code
            if midx.column() == self.C.group_description:
                return grp.group_description
            if midx.column() == self.C.data_count:
                return grp.data_rows_count()
            return "?"

        if role == Qt.DecorationRole:
            if col == self.C.group_code:
                return Ico.icon(Ico.Group)

        if role == Qt.FontRole:
            if col == self.C.group_code:
                f = QtGui.QFont()
                f.setBold(True)
                return f

        if role == Qt.TextAlignmentRole:
            return Qt.AlignRight if col == 0 else Qt.AlignLeft

        if False and role == Qt.BackgroundColorRole:
            #print self.ogtGroup.data_cell(index.row(), index.column())
            cell = self.ogtDoc.group_by_index(row)[col]
            #bg = cell.get_bg()
            if len(self.ogtGroup.data_cell(row, col).errors) > 0:
                print bg, self.ogtGroup.data_cell(row, col).errors
            return QtGui.QColor(bg)


        return QtCore.QVariant()


    def headerData(self, idx, orient, role=None):
        if role == Qt.DisplayRole and orient == Qt.Horizontal:
            return QtCore.QVariant(self._col_labels[idx])

        if role == Qt.TextAlignmentRole and orient == Qt.Horizontal:
            return Qt.AlignRight if idx == 0 else Qt.AlignLeft

        return QtCore.QVariant()


class GroupsListWidget( QtGui.QWidget ):

    sigFileSelected = pyqtSignal(object)

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False

        self.setMinimumWidth(300)

        self.mainLayout = xwidgets.vlayout()
        self.setLayout(self.mainLayout)


        #=============================
        ## Set up tree
        self.tree = QtGui.QTreeView()
        self.mainLayout.addWidget(self.tree)

        self.tree.setMinimumWidth(300)
        self.tree.setRootIsDecorated(False)
        self.tree.header().setStretchLastSection(True)

        self.model = GroupListModel()
        self.tree.setModel(self.model)

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

        #self.load_projects()

    def set_document(self, ogtDoc):
        self.model.set_document(ogtDoc)


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
