# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

from Qt import QtGui, QtCore, Qt, pyqtSignal

from ogt import ags4

import app_globals as G
from img import Ico
import ags4_widgets
import xwidgets



class OGTHeaderWidget( QtGui.QWidget ):
    """The HEADER info which in row 0 """

    sigGoto = pyqtSignal(str)

    def __init__( self, parent=None, ogtDoc=None):
        QtGui.QWidget.__init__( self, parent )

        self.ogtDoc = ogtDoc
        self.ogtHeading = None

        self.debug = False


        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        row = 0
        ## So splits up tthe header into parts..
        #self.headerWidget = QtGui.QWidget()
        self.headerGridLay = QtGui.QHBoxLayout()
        #self.headerWidget.setLayout(self.headerGridLay)
        self.mainLayout.addLayout(self.headerGridLay, row, 0, 1, 3)

        self.lblHeadCode = xwidgets.XLabel("-", bold=True)
        self.headerGridLay.addWidget(self.lblHeadCode, 10)

        #self.buttGroup = xwidgets.XToolButton(self, text="group")
        #self.headerGridLay.addWidget(self.buttGroup)

        self.buttHeadCode = xwidgets.XToolButton(self, ico=Ico.BulletDown,  bold=True, popup=True, menu=True)
        self.buttHeadCode.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.headerGridLay.addWidget(self.buttHeadCode, 0)
        #print "ss", self.buttHeadCode.isCheckable()

        self.buttHeadCode.menu().addAction("Open Group TODO")
        self.buttHeadCode.menu().addAction("Select another heading TODO")

        #sp = self.buttHeadCode.sizePolicy()
        #sp.setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        #self.buttHeadCode.setSizePolicy(sp)

        sty = "background-color: #dddddd; color: black; padding: 3px; font-size: 8pt;"

        # description
        row += 1
        self.lblHeadDescription = QtGui.QLabel()
        self.lblHeadDescription.setStyleSheet(sty)
        self.lblHeadDescription.setFixedHeight(60)
        self.lblHeadDescription.setWordWrap(True)
        self.lblHeadDescription.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.mainLayout.addWidget(self.lblHeadDescription, row, 0, 1, 3)


        # unit
        row += 1
        lbl = xwidgets.XLabel("Unit:", align=Qt.AlignRight, style=sty)
        self.mainLayout.addWidget(lbl, row, 0)

        self.lblUnit = xwidgets.XLabel("-", bold=True, style=sty + "color: #000099;")
        self.mainLayout.addWidget(self.lblUnit, row, 1, 1, 2)

        # Type
        row += 1
        lbl = xwidgets.XLabel("Type:", align=Qt.AlignRight, style=sty )
        self.mainLayout.addWidget(lbl, row, 0)

        self.lblType = xwidgets.XLabel("-", bold=True, style=sty + "color: #000099;" )
        self.mainLayout.addWidget(self.lblType, row, 1)

        self.buttLink = QtGui.QToolButton()
        #self.buttLink.setAutoRaise(True)
        self.buttLink.setText("Goto")
        self.mainLayout.addWidget(self.buttLink, row, 2)
        self.buttLink.setVisible(False)
        self.buttLink.clicked.connect(self.on_goto)

        self.mainLayout.setColumnStretch(0, 1)
        self.mainLayout.setColumnStretch(1, 5)

    def set_link(self, state):
        self.buttLink.setVisible(state)

    def set_heading(self, ogtHeading):

        self.ogtHeading = ogtHeading

        descr = self.ogtHeading.head_description
        t = "-" if descr == None else descr
        para = '<p style="line-height: 80%">' + t + '</p>'
        self.lblHeadDescription.setText(para)

        self.lblHeadCode.setText(ogtHeading.head_code)

        self.lblUnit.setText(self.ogtHeading.unit_label)
        #typ = "<a href="""
        self.lblType.setText(self.ogtHeading.unit_label)
        #self.lblType.setToolTip(hrec['type'])

        #print hrec['type'], self.doc.type(hrec['type'])
        typ = ags4.AGS4.type(self.ogtHeading.type)
        if typ:
            self.lblType.setToolTip(typ['description'])
        else:
            self.lblType.setToolTip(self.ogtHeading.type_label)

    def on_goto(self):
        self.sigGoto.emit(self.ogtHeading.head_code)

class GroupModel(QtCore.QAbstractTableModel):
    """Model for groups
    """
    def __init__(self):
        QtCore.QAbstractTableModel.__init__(self)

        self.ogtGroup = None

    def load_group(self, ogtGroup):

        self.ogtGroup = ogtGroup

    def rowCount(self, parent=None, *args):
        """Returns the number of rows of the model"""
        if self.ogtGroup == None:
            return 0
        #print "=", self.ogtGroup.data_rows_count()
        return self.ogtGroup.data_rows_count()

    def columnCount(self, parent=None, *args):
        """Returns the number of columns of the model"""
        if self.ogtGroup == None:
            return 0
        return self.ogtGroup.headings_count()

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data at the given index"""
        #rint index, index.row(), index.column()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self.ogtGroup.data_cell(index.row(), index.column()).value

        if role == Qt.BackgroundColorRole:
            #print self.ogtGroup.data_cell(index.row(), index.column())
            cell = self.ogtGroup.data_cell(index.row(), index.column())
            bg = cell.get_bg()
            return QtGui.QColor(bg)


        return None

    def headerData(self, idx, orientation, role=Qt.DisplayRole):
        """Returns the headers to display"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.ogtGroup.headings_source_sort[idx]

        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(idx + 1)

        return None

    def dead_setData(self, index, value, role=None):
        """Updates data when modified in the view"""
        if role == Qt.EditRole:
            if index.column() == 1:
                self._editor.trains[index.row()].serviceCode = value
            elif index.column() == 2:
                self._editor.trains[index.row()].trainTypeCode = value
            elif index.column() == 3:
                self._editor.trains[index.row()].appearTimeStr = value
            elif index.column() == 4:
                self._editor.trains[index.row()].trainHeadStr = value
            elif index.column() == 5:
                self._editor.trains[index.row()].initialSpeed = value
            elif index.column() == 6:
                self._editor.trains[index.row()].initialDelayStr = value
            else:
                return False
            self.dataChanged.emit(index, index)
            return True
        return False

    def dead_flags(self, index):
        """Returns the flags of the model"""
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() != 0:
            flags |= Qt.ItemIsEditable
        return flags

class OGTGroupWidget( QtGui.QWidget ):
    """Shows a group with labels at top, and table underneath"""

    sigGoto = pyqtSignal(str)

    def __init__( self, parent, doc):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False
        #self.doc = doc
        self.ogtGroup = None

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        ## titles
        m = 3
        topLay = QtGui.QHBoxLayout()
        topLay.setSpacing(0)
        topLay.setContentsMargins(m,m,m,m)
        self.mainLayout.addLayout(topLay, 0)

        sty = "background-color: #333333; color: #dddddd; padding: 2px;"

        self.buttGroupCode = QtGui.QToolButton()
        self.buttGroupCode.setText("-")
        self.buttGroupCode.setIcon(Ico.icon(Ico.Ags4))
        self.buttGroupCode.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.buttGroupCode.setStyleSheet( "font-weight: bold;")
        topLay.addWidget(self.buttGroupCode, 0)
        self.buttGroupCode.clicked.connect(self.on_butt_group_code)

        self.lblGroupDescription = QtGui.QLabel()
        self.lblGroupDescription.setStyleSheet(sty + "")
        topLay.addWidget(self.lblGroupDescription, 100)

        self.tableHeadings = QtGui.QTableWidget()
        self.mainLayout.addWidget(self.tableHeadings, 0)
        self.tableHeadings.horizontalHeader().hide()
        self.tableHeadings.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableHeadings.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.tableData = QtGui.QTableView()
        self.mainLayout.addWidget(self.tableData, 200)
        self.tableData.horizontalHeader().hide()
        self.tableData.setModel(QtGui.QStandardItemModel()) # empty model

        self.tableData.horizontalScrollBar().valueChanged.connect(self.on_table_data_h_scroll)
        #self.tableData.verticalScrollBar().valueChanged.connect(self.on_tree_sched_v_scroll)

        self.model = None

    def on_table_data_h_scroll(self, x):
        self.tableHeadings.horizontalScrollBar().setValue(x)

    def on_tree_sched_v_scroll(self, x):
        self.treeSamples.verticalScrollBar().setValue(x)

    def load_group(self, ogtGroup):

        self.ogtGroup = ogtGroup
        ## Set the labels
        self.buttGroupCode.setText( self.ogtGroup.group_code  )

        descr = None
        if ogtGroup.data_dict():
            descr = self.ogtGroup.group_description
        self.lblGroupDescription.setText( "-" if descr == None else descr )

        self.model = GroupModel()
        self.model.load_group(self.ogtGroup)
        self.tableData.setModel(self.model)

        # Init table, first row = 0 is headings (cos we cant embed widgets in a header on pyqt4)
        #headings = self.ogtGroup.headings()
        self.tableHeadings.setRowCount(1)
        self.tableHeadings.setColumnCount( self.ogtGroup.headings_count() )

        #v_labels = QtCore.QStringList() # vertical labels

        ## Populate header
        HEADER_HEIGHT = 120
        #print "headings list", self.ogtGroup.headings_list()
        for cidx, heading in enumerate(self.ogtGroup.headings_list()):
            #print cidx, heading, self
            hitem = xwidgets.XTableWidgetItem()
            hitem.set(heading.head_code, bold=True)
            self.tableHeadings.setHorizontalHeaderItem(cidx, hitem)

            header_widget = OGTHeaderWidget(ogtDoc=self.ogtGroup.ogtDoc)
            header_widget.set_heading(heading)

            self.tableHeadings.setCellWidget(0, cidx, header_widget )
            header_widget.sigGoto.connect(self.on_goto)

        self.tableHeadings.setVerticalHeaderLabels([""])

        self.tableHeadings.setRowHeight(0, HEADER_HEIGHT)
        self.tableHeadings.setFixedHeight(HEADER_HEIGHT + 30)
        v_labels = QtCore.QStringList()

        # Load the data
        for ridx, row in enumerate(self.ogtGroup.data):

            #self.tableData.setRowCount( self.tableData.rowCount() + 1)
            v_labels.append( str(ridx + 1) )

            for cidx, heading in enumerate(self.ogtGroup.headings_list()):

                #item = QtGui.QTableWidgetItem()
                #item.setText(row[heading.head_code])
                #self.tableData.setItem(ridx + 1, cidx, item)

                if heading.type == "PA":
                    # Combo dropdown
                    self.tableData.setItemDelegateForColumn(cidx, ags4_widgets.PickListComboDelegate(self, heading))
                    #item.setBackgroundColor(QtGui.QColor("#FFFDBF"))

                if heading.type in ["2DP"]:
                    # Number editor
                    #item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                    self.tableData.setItemDelegateForColumn(cidx, ags4_widgets.NumberEditDelegate(self, heading))


                if heading.type == "ID":

                    if self.ogtGroup.group_code  == heading.head_code.split("_")[0]:
                        # in same group as heading, so highlight the ID
                        pass #item.setBackgroundColor(QtGui.QColor("#FFF96C"))
                    else:
                        # Dropdown for ID
                        optts = self.ogtGroup.parentDoc.get_column_data(heading.head_code)
                        self.tableData.setItemDelegateForColumn(cidx, ags4_widgets.IDComboDelegate(self, heading, options=optts))
                        #self.tableData.cellWidget(0, cidx).set_link(True)
                        #item.setBackgroundColor(QtGui.QColor("#FFFDBF"))

                self.tableData.setRowHeight(ridx + 1, 25)
        # resize columns, with max_width
        col_width = 200

        #self.tableHeadings.resizeColumnsToContents()
        for cidx in range(0, self.tableHeadings.columnCount()):
            self.tableHeadings.setColumnWidth(cidx, 120)
            if self.tableHeadings.columnWidth(cidx) > col_width:
                self.tableHeadings.setColumnWidth(cidx, col_width)
            self.tableData.setColumnWidth(cidx, self.tableHeadings.columnWidth(cidx))
        #print self.tableData.verticalHeader().width()
        self.tableHeadings.verticalHeader().setFixedWidth(self.tableData.verticalHeader().width())
        #self.table.setVerticalHeaderLabels(v_labels)

    def on_goto(self, code):
        #print "on_goto", code, self
        self.sigGoto.emit(code)

    def on_butt_group_code(self):
        d = ags4_widgets.AGS4GroupViewDialog(group_code=self.ogtGroup.group_code)
        d.exec_()
