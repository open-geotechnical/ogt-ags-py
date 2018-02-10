# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

from Qt import QtGui, QtCore, Qt, pyqtSignal

from ogt import ags4, CELL_COLORS

import app_globals as G
from img import Ico
import ags4_widgets
import xwidgets
import ogtgui_widgets


class HeadersListModel(QtCore.QAbstractTableModel):

    class C:
        #node = 0
        valid = 0
        head_code = 1
        unit = 2
        type = 3
        head_description = 4


    def __init__(self):
        QtCore.QAbstractTableModel.__init__(self)

        self.ogtGroup = None
        self._col_labels = ["Valid", "Heading", "Unit", "Type", "Descripton"]

    def set_group(self, ogtGroup):
        self.ogtGroup = ogtGroup

    def columnCount(self, foo):
        return len(self._col_labels)

    def rowCount(self, midx):

        if self.ogtGroup == None:
            return 0
        return self.ogtGroup.headings_count

    def data(self, midx, role=Qt.DisplayRole):
        """Returns the data at the given index"""
        row = midx.row()
        col = midx.column()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            #print "==", row, col, self
            hd = self.ogtGroup.heading_by_index(row)
            if col == self.C.head_code:
                return hd.head_code
            if col == self.C.unit:
                return hd.unit_label
            if col == self.C.type:
                return hd.type_label
            if col == self.C.head_description:
                return hd.head_description
            if col == self.C.valid:
                return "TODO"
            return "?"

        if role == Qt.DecorationRole:
            if col == self.C.head_code:
                return Ico.icon(Ico.AgsHeading)

        if role == Qt.FontRole:
            if col == self.C.head_code:
                f = QtGui.QFont()
                f.setBold(True)
                return f

        if role == Qt.TextAlignmentRole:
            if col == 0:
                return Qt.AlignRight
            if col in [self.C.valid, self.C.unit, self.C.type]:
                return Qt.AlignCenter
            return Qt.AlignLeft

        if False and role == Qt.BackgroundColorRole:
            cell = self.ogtDoc.group_by_index(row)[col]
            #bg = cell.get_bg()
            if len(self.ogtGroup.data_cell(row, col).errors) > 0:
                pass #print bg, self.ogtGroup.data_cell(row, col).errors
            return QtGui.QColor(bg)


        return QtCore.QVariant()


    def headerData(self, idx, orient, role=None):
        if role == Qt.DisplayRole and orient == Qt.Horizontal:
            return QtCore.QVariant(self._col_labels[idx])

        if role == Qt.TextAlignmentRole and orient == Qt.Horizontal:
            if  idx == 0:
                return Qt.AlignRight
            if idx in [self.C.valid, self.C.unit, self.C.type]:
                return Qt.AlignCenter
            return Qt.AlignLeft

        return QtCore.QVariant()

class HeadersListWidget( QtGui.QWidget ):


    #sigGoto = pyqtSignal(str)

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False
        self.ogtGroup = None

        self.mainLayout = xwidgets.vlayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.addWidget(xwidgets.XLabel("Foooo"))

        self.tree = QtGui.QTreeView()
        self.tree.setRootIsDecorated(False)
        self.mainLayout.addWidget(self.tree, 0)


        self.model = HeadersListModel()
        self.tree.setModel(self.model)

        self.tree.setColumnWidth(HeadersListModel.C.head_code, 110)
        self.tree.setColumnWidth(HeadersListModel.C.valid, 50)
        self.tree.setColumnWidth(HeadersListModel.C.unit, 50)
        self.tree.setColumnWidth(HeadersListModel.C.type, 50)


    def set_group(self, ogtGrp):
        self.model.set_group(ogtGrp)


class HeadCodeWidget( QtGui.QWidget ):
    """The info in tableWidget """

    #sigGoto = pyqtSignal(str)

    def __init__( self, parent=None, ogtDoc=None):
        QtGui.QWidget.__init__( self, parent )

        self.ogtDoc = ogtDoc
        self.ogtHeading = None

        self.debug = False
        self.setAutoFillBackground(True)

        self.mainLayout = xwidgets.vlayout()
        self.setLayout(self.mainLayout)


        ## So splits up tthe header into parts..
        #self.headerWidget = QtGui.QWidget()
        self.headerCodeLay = xwidgets.hlayout()
        #self.headerWidget.setLayout(self.headerGridLay)
        self.mainLayout.addLayout(self.headerCodeLay)

        self.lblHeadCode = xwidgets.XLabel("-", bold=True)
        self.headerCodeLay.addWidget(self.lblHeadCode, 10)

        #self.buttGroup = xwidgets.XToolButton(self, text="group")
        #self.headerGridLay.addWidget(self.buttGroup)

        self.buttHeadCode = xwidgets.XToolButton(self, ico=Ico.BulletDown,  bold=True, popup=True, menu=True)
        self.buttHeadCode.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.headerCodeLay.addWidget(self.buttHeadCode, 0)

        self.buttHeadCode.menu().addAction("Open Group TODO")
        self.buttHeadCode.menu().addAction("Select another heading TODO")

        #sp = self.buttHeadCode.sizePolicy()
        #sp.setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        #self.buttHeadCode.setSizePolicy(sp)
        """
        sty = "background-color: #dddddd; color: black; padding: 3px; font-size: 8pt;"

        # description
        self.lblHeadDescription = QtGui.QLabel()
        self.lblHeadDescription.setStyleSheet(sty)
        self.lblHeadDescription.setFixedHeight(60)
        self.lblHeadDescription.setWordWrap(True)
        self.lblHeadDescription.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.mainLayout.addWidget(self.lblHeadDescription)
        """

    def set_head_code(self, x):
        self.lblHeadCode.setText(x)


class TableHeaderWidget( QtGui.QWidget ):
    """The HEADER info in tableWidget """

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
        self.lblType.setText(self.ogtHeading.type_label)
        #self.lblType.setToolTip(hrec['type'])

        typ = ags4.AGS4.type(self.ogtHeading.type)
        if typ:
            self.lblType.setToolTip(typ['description'])
        else:
            self.lblType.setToolTip(self.ogtHeading.type_label)

    def on_goto(self):
        self.sigGoto.emit(self.ogtHeading.head_code)




class GroupHeadingsModel(QtCore.QAbstractTableModel):
    """Model for groups
    """
    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)

        self.ogtGroup = None

    def set_group(self, ogtGroup):

        self.ogtGroup = ogtGroup
        #print "set_grsoup", self
        self.layoutChanged.emit()

    def columnCount(self, parent=None):
        """Returns the number of columns of the model"""
        if self.ogtGroup == None:
            return 0
        #print "cc=", self.ogtGroup.headings_count, self
        return self.ogtGroup.headings_count

    def rowCount(self, parent=None):
        """Returns the number of rows of the model"""
        return 4
        #if self.ogtGroup == None:
        #    return 0
        #print "rc=", self.ogtGroup.data_rows_count(), self
        #return self.ogtGroup.data_rows_count()


    def data(self, index, role=Qt.DisplayRole):
        """Returns the data at the given index"""
        row = index.row()
        col = index.column()
        #last_col = col == self.columnCount() - 1
        #print "r/c=", row, col
        if role == Qt.DisplayRole or role == Qt.EditRole:
            #if last_col:
            #    return "last"
            head = self.ogtGroup.heading_by_index(col)
            if row == 0:
                return head.head_code
            if row == 1:
                return head.head_description
            if row == 2:
                return head.unit
            if row == 3:
                return head.type
            return "_NOCELL_"
            """
            cell = self.ogtGroup.data_cell(row, col)
            if cell:
                return cell.value
            
            """
        if False and role == Qt.BackgroundColorRole:
            cell = self.ogtGroup.data_cell(row, col)
            bg = cell.get_bg()
            if len(self.ogtGroup.data_cell(row, col).errors) > 0:
                pass
            return QtGui.QColor(bg)


        return None

    def headerData(self, idx, orientation, role=Qt.DisplayRole):
        """Returns the headers to display"""
        #print "headerData", idx, self
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            #print "hd=", idx, self.ogtGroup.heading_by_index(idx)
            return self.ogtGroup.heading_by_index(idx).head_code

        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(idx + 1)

        return None

    def setData(self, index, value, role=None):
        """Updates DATA when modified in the view"""
        if role == Qt.EditRole:
            success = self.ogtGroup.set_data_cell_value(index.row(), index.column(), value)
            self.layoutChanged.emit()
            return success
            #self.dataChanged.emit(index, index)
            #return True
        return False

    def flags(self, index):
        """Returns the flags of the model"""
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled #| Qt.ItemIsEditable
        #if index.column() != 0:
        #    flags |= Qt.ItemIsEditable
        return flags


class GroupDataModel(QtCore.QAbstractTableModel):
    """Model for groups
    """
    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)

        self.ogtGroup = None

    def set_group(self, ogtGroup):

        self.ogtGroup = ogtGroup
        #print "set_grsoup", self
        self.layoutChanged.emit()

    def columnCount(self, parent=None):
        """Returns the number of columns of the model"""
        if self.ogtGroup == None:
            return 0
        #print "cc=", self.ogtGroup.headings_count, self
        return self.ogtGroup.headings_count

    def rowCount(self, parent=None):
        """Returns the number of rows of the model"""
        if self.ogtGroup == None:
            return 0
        #print "rc=", self.ogtGroup.data_rows_count(), self
        return self.ogtGroup.data_rows_count()


    def data(self, index, role=Qt.DisplayRole):
        """Returns the data at the given index"""
        row = index.row()
        col = index.column()
        #last_col = col == self.columnCount() - 1
        #print "r/c=", row, col
        if role == Qt.DisplayRole or role == Qt.EditRole:
            #if last_col:
            #    return "last"
            cell = self.ogtGroup.data_cell(row, col)
            if cell:
                return cell.value
            return "_NOCELL_"

        if False and role == Qt.BackgroundColorRole:
            cell = self.ogtGroup.data_cell(row, col)
            bg = cell.get_bg()
            if len(self.ogtGroup.data_cell(row, col).errors) > 0:
                pass
            return QtGui.QColor(bg)


        return None

    def headerData(self, idx, orientation, role=Qt.DisplayRole):
        """Returns the headers to display"""
        #print "headerData", idx, self
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            #print "hd=", idx, self.ogtGroup.heading_by_index(idx)
            return self.ogtGroup.heading_by_index(idx).head_code

        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(idx + 1)

        return None

    def setData(self, index, value, role=None):
        """Updates DATA when modified in the view"""
        if role == Qt.EditRole:
            success = self.ogtGroup.set_data_cell_value(index.row(), index.column(), value)
            self.layoutChanged.emit()
            return success
            #self.dataChanged.emit(index, index)
            #return True
        return False

    def flags(self, index):
        """Returns the flags of the model"""
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        #if index.column() != 0:
        #    flags |= Qt.ItemIsEditable
        return flags


class GroupSourceGridTableWidget( QtGui.QWidget ):



    #sigGoto = pyqtSignal(str)

    def __init__( self, parent):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False
        self.ogtGroup = None

        self.mainLayout = xwidgets.vlayout()
        self.setLayout(self.mainLayout)

        ## View Checkboxes
        self.topLay = xwidgets.hlayout(margin=5, spacing=5)
        self.mainLayout.addLayout(self.topLay)

        self.buttGroup = QtGui.QButtonGroup(self)
        self.buttGroup.setExclusive(True)

        self.radFixed = QtGui.QRadioButton("Show Fixed Values")
        self.radFixed.setChecked(True)
        self.topLay.addWidget(self.radFixed)
        self.buttGroup.addButton(self.radFixed, GroupSourceGridModel.FIXED)

        self.radRaw = QtGui.QRadioButton("Show Raw Values")
        self.topLay.addWidget(self.radRaw)
        self.buttGroup.addButton(self.radRaw, GroupSourceGridModel.RAW)

        self.topLay.addStretch(30)
        self.buttGroup.buttonClicked.connect(self.on_view_raw_clicked)

        ## Main Table
        self.table = QtGui.QTableView()
        self.mainLayout.addWidget(self.table, 0)

        self.model = QtGui.QStandardItemModel()
        self.table.setModel(self.model)

    def on_view_raw_clicked(self, butt):
        self.model.set_view_raw(self.buttGroup.id(butt))

    def set_group(self, ogtGroup):
        ## SourceTable
        self.model = GroupSourceGridModel()
        self.model.set_group(ogtGroup)
        self.table.setModel(self.model)

class GroupSourceGridModel(QtCore.QAbstractTableModel):
    """Model for groups raw View
    """

    FIXED = 0
    RAW = 1

    def __init__(self):
        QtCore.QAbstractTableModel.__init__(self)

        self.ogtGroup = None
        self.view_raw = self.FIXED

    def set_group(self, ogtGroup):
        self.ogtGroup = ogtGroup

    def rowCount(self, parent=None, *args):
        """Returns the number of rows of the model"""
        if self.ogtGroup == None:
            return 0
        return self.ogtGroup.row_count()

    def columnCount(self, parent=None, *args):
        """Returns the number of columns of the model"""
        if self.ogtGroup == None:
            return 0
        return self.ogtGroup.column_count

    def set_view_raw(self, fr):
        self.view_raw = fr
        self.layoutChanged.emit()


    def data(self, index, role=Qt.DisplayRole):
        """Returns the data at the given index"""
        #rint index, index.row(), index.column()
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            cell =  self.ogtGroup.cell(row, col)
            if cell:
                return cell.raw if self.view_raw == self.RAW else cell.value
            return "-"

        if role == Qt.BackgroundColorRole:
            cell = self.ogtGroup.cell(row, col)
            #bg = "white"
            if cell:
                bg = cell.get_bg(self.view_raw == self.FIXED)
            else:
                bg = CELL_COLORS.empty_bg
            #print row, col, bg, cell
            return QtGui.QColor(bg)


        return None

    def headerData(self, idx, orientation, role=Qt.DisplayRole):
        """Returns the headers to display"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return str(idx + 1) #self.ogtGroup.headings_source_sort[idx]

        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(idx + 1)

        return None

    def setData(self, index, value, role=None):
        """Updates data when modified in the view"""
        if role == Qt.EditRole:
            v = str(value.toString())
            success = self.ogtGroup.set_cell_value(index.row(), index.column(), v)
            #self.dataChanged.emit(index, index)
            self.layoutChanged.emit()
            return success
        return False

    def flags(self, index):
        """Returns the flags of the model"""
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled |  Qt.ItemIsEditable
        #if index.column() != 0:
        #    flags |= Qt.ItemIsEditable
        return flags
"""
class HeadCodeDelegate(QtGui.QItemDelegate):
    def __init__(self):
        QtGui.QItemDelegate.__init__(self)


    def paint(self, painter, option, index):

        button = QtGui.QStyleOptionButton()
        r = option.rect

        x = r.left() + r.width() - 30 # ; // the        X coordinate

        y = r.top() #; // the       Y        coordinate
        w = 30 #; // button        width
        h = 30 #; // button        height
        button.rect = QtCore.QRect(x, y, w, h);
        button.text = "=^.^=";
        button.state = QtGui.QStyle.State_Enabled;

        QtGui.QApplication.style().drawControl(QtGui.QStyle.CE_ItemViewItem, button, painter)
"""

class GroupDataTableWidget( QtGui.QWidget ):


    sigGoto = pyqtSignal(str)

    def __init__( self, parent):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False
        self.ogtGroup = None

        self.mainLayout = xwidgets.vlayout()
        self.setLayout(self.mainLayout)

        #== Headings
        self.tableHeadings = QtGui.QTableView()
        self.mainLayout.addWidget(self.tableHeadings, 0)

        self.headingsModel = GroupHeadingsModel(self)
        self.tableHeadings.setModel(self.headingsModel)

        self.tableHeadings.horizontalHeader().hide()
        self.tableHeadings.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableHeadings.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        #== Data
        self.tableData = QtGui.QTableView()
        self.mainLayout.addWidget(self.tableData, 200)

        self.dataModel =  GroupDataModel(self)
        self.tableData.setModel(self.dataModel)

        self.tableData.horizontalHeader().hide()
        self.tableData.horizontalScrollBar().valueChanged.connect(self.on_table_data_h_scroll)

        HEADER_HEIGHT = 120
        self.tableHeadings.setRowHeight(1, 60)
        self.tableHeadings.setFixedHeight(HEADER_HEIGHT + 30)

        #self.headCodeDelegeate = HeadCodeDelegate()
        #self.tableHeadings.setItemDelegateForRow(0, self.headCodeDelegeate)
        #HeadCodeWidget



        self.headingsModel.dataChanged.connect(self.on_header_data_changed)

    def on_header_data_changed(self, tl, tr):
        print "on_header_data_changed", tl, tr
        dssdsa()

    def update_headings(self):

        for cidx in range(0, self.headingsModel.columnCount()):
            idx = self.headingsModel.index(0, cidx)
            widget = self.tableHeadings.indexWidget(idx)
            if widget == None:
                widget = HeadCodeWidget()
                self.tableHeadings.setIndexWidget(idx, widget)
            widget.set_head_code( self.headingsModel.data(idx, Qt.DisplayRole))

    def on_table_data_h_scroll(self, x):
        self.tableHeadings.horizontalScrollBar().setValue(x)

    def deadon_tree_sched_v_scroll(self, x):
        self.treeSamples.verticalScrollBar().setValue(x)

    def set_group(self, ogtGroup):

        self.ogtGroup = ogtGroup

        #self.headingsModel =
        self.headingsModel.set_group(self.ogtGroup)


        #self.dataModel =
        self.dataModel.set_group(self.ogtGroup)




        # Init table, first row = 0 is headings (cos we cant embed widgets in a header on pyqt4)
        # headings = self.ogtGroup.headings()
        #self.tableHeadings.setRowCount(1)
        #self.tableHeadings.setColumnCount(self.ogtGroup.headings_count)
        return
        # v_labels = QtCore.QStringList() # vertical labels

        ## Populate header
        HEADER_HEIGHT = 120
        for cidx, heading in enumerate(self.ogtGroup.headings_list()):
            hitem = xwidgets.XTableWidgetItem()
            hitem.set(heading.head_code, bold=True)
            self.tableHeadings.setHorizontalHeaderItem(cidx, hitem)

            header_widget = TableHeaderWidget(ogtDoc=self.ogtGroup.ogtDoc)
            header_widget.set_heading(heading)

            self.tableHeadings.setCellWidget(0, cidx, header_widget)
            header_widget.sigGoto.connect(self.on_goto)

        self.tableHeadings.setVerticalHeaderLabels([""])

        self.tableHeadings.setRowHeight(0, HEADER_HEIGHT)
        self.tableHeadings.setFixedHeight(HEADER_HEIGHT + 30)
        v_labels = QtCore.QStringList()

        # Load the data
        return
        for ridx, row in enumerate(self.ogtGroup.data):

            # self.tableData.setRowCount( self.tableData.rowCount() + 1)
            v_labels.append(str(ridx + 1))

            for cidx, heading in enumerate(self.ogtGroup.headings_list()):

                # item = QtGui.QTableWidgetItem()
                # item.setText(row[heading.head_code])
                # self.tableData.setItem(ridx + 1, cidx, item)

                if heading.type == "PA":
                    # Combo dropdown
                    self.tableData.setItemDelegateForColumn(cidx, ags4_widgets.PickListComboDelegate(self, heading))
                    # item.setBackgroundColor(QtGui.QColor("#FFFDBF"))

                if heading.type in ["2DP"]:
                    # Number editor
                    # item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                    self.tableData.setItemDelegateForColumn(cidx, ags4_widgets.NumberEditDelegate(self, heading))

                if heading.type == "ID":

                    if self.ogtGroup.group_code == heading.head_code.split("_")[0]:
                        # in same group as heading, so highlight the ID
                        pass  # item.setBackgroundColor(QtGui.QColor("#FFF96C"))
                    else:
                        # Dropdown for ID
                        optts = self.ogtGroup.parentDoc.get_column_data(heading.head_code)
                        self.tableData.setItemDelegateForColumn(cidx, ags4_widgets.IDComboDelegate(self, heading,
                                                                                                   options=optts))
                        # self.tableData.cellWidget(0, cidx).set_link(True)
                        # item.setBackgroundColor(QtGui.QColor("#FFFDBF"))

                self.tableData.setRowHeight(ridx + 1, 25)
        # resize columns, with max_width
        col_width = 200

        # self.tableHeadings.resizeColumnsToContents()
        for cidx in range(0, self.tableHeadings.columnCount()):
            self.tableHeadings.setColumnWidth(cidx, 120)
            if self.tableHeadings.columnWidth(cidx) > col_width:
                self.tableHeadings.setColumnWidth(cidx, col_width)
            self.tableData.setColumnWidth(cidx, self.tableHeadings.columnWidth(cidx))

        self.tableHeadings.verticalHeader().setFixedWidth(self.tableData.verticalHeader().width())


    def on_goto(self, code):
        self.sigGoto.emit(code)

class GroupWidget( QtGui.QWidget ):


    sigGoto = pyqtSignal(str)

    def __init__( self, parent=None, ogtGroup=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False
        self.ogtGroup = None

        self.mainLayout = xwidgets.vlayout()
        self.setLayout(self.mainLayout)

        ## titles and toolbar at top =========
        m = 3
        topLay = xwidgets.hlayout(margin=m)
        self.mainLayout.addLayout(topLay, 0)

        # View Mode
        self.tbgView = xwidgets.ToolBarGroup(title="View", is_group=True, toggle_icons=True, toggle_callback=self.on_view_change )
        topLay.addWidget(self.tbgView)

        self.tbgView.addButton(text="Data", idx=0, checkable=True)
        self.tbgView.addButton(text="Source", idx=1, checkable=True, checked=True)


        # description
        sty = "background-color: #333333; color: #dddddd; padding: 2px;"
        self.lblGroupDescription = QtGui.QLabel()
        self.lblGroupDescription.setStyleSheet(sty + "")
        topLay.addWidget(self.lblGroupDescription, 100)


        # The AGS group data
        self.buttGroupCode = xwidgets.XToolButton(text="-", ico=Ico.Ags4, bold=True, width=80, tooltip="View AGS data Dict")
        #self.buttGroupCode.setStyleSheet( "font-weight: bold;")
        topLay.addWidget(self.buttGroupCode, 0)
        self.buttGroupCode.clicked.connect(self.on_butt_group_code)

        # mid splitter with stack widget
        self.splitter = QtGui.QSplitter()
        self.mainLayout.addWidget(self.splitter)

        #self.stackWidget = QtGui.QStackedWidget()
        #self.splitter.addWidget(self.stackWidget)

        # Left LAyout
        if True:
            self.leftWidget = QtGui.QWidget()
            self.leftLay = xwidgets.vlayout()
            self.leftWidget.setLayout(self.leftLay)
            self.splitter.addWidget(self.leftWidget)

            self.groupDataTableWidget = GroupDataTableWidget(self)
            self.leftLay.addWidget(self.groupDataTableWidget)

            self.groupSourceTableWidget = GroupSourceGridTableWidget(self)
            self.leftLay.addWidget(self.groupSourceTableWidget)

        # Right LAyout
        self.rightWidget = QtGui.QWidget()
        self.rightLay = xwidgets.vlayout()
        self.rightWidget.setLayout(self.rightLay)
        self.splitter.addWidget(self.rightWidget)

        self.errorsWidget = ogtgui_widgets.OGTErrorsWidget(mode=ogtgui_widgets.VIEW_ERR_MODE.group)
        self.rightLay.addWidget(self.errorsWidget, 1)


        self.headersListWidget = HeadersListWidget()
        self.headersListWidget.setMinimumWidth(300)
        self.rightLay.addWidget(self.headersListWidget, 1)



        self.splitter.setStretchFactor(0, 10)
        self.splitter.setStretchFactor(1, 4)
        #self.splitter.setStretchFactor(0, 10)
        #self.splitter.setStretchFactor(1, 0)

        if ogtGroup:
            self.set_group(ogtGroup)

        self.groupSourceTableWidget.model.layoutChanged.connect(self.on_data_changed)
        self.groupDataTableWidget.headingsModel.layoutChanged.connect(self.on_data_changed)
        self.groupDataTableWidget.dataModel.layoutChanged.connect(self.on_data_changed)

        self.on_view_change(self.tbgView.get_id())

        #self.groupDataTableWidget.headingsModel.dataChanged.connect(self.on_headings_data_changed)

        self.on_data_changed()

    def on_headings_data_changed(self):
        print "on_headings_data_changed"

    def on_data_changed(self):
        print "on_data_changed", self, self.sender()


        for model in [
                    self.groupSourceTableWidget.model,
                    self.groupDataTableWidget.headingsModel,
                    self.groupDataTableWidget.dataModel    ]:
            if model == self.sender():
                print "ignore", model
            else:
                model.modelReset.emit()

        self.headersListWidget.model.layoutChanged.emit()
        self.errorsWidget.model.layoutChanged.emit()

        self.groupDataTableWidget.update_headings()

    def set_group(self, ogtGroup):

        self.ogtGroup = ogtGroup
        ## Set the labels
        self.buttGroupCode.setText( self.ogtGroup.group_code  )

        descr = None
        if ogtGroup.data_dict():
            descr = self.ogtGroup.group_description
        self.lblGroupDescription.setText( "-" if descr == None else descr )

        # load into widgets

        self.groupDataTableWidget.set_group(ogtGroup)
        self.groupSourceTableWidget.set_group(ogtGroup)
        self.headersListWidget.set_group(ogtGroup)
        self.errorsWidget.set_group(ogtGroup)
        return


    def on_goto(self, code):
        self.sigGoto.emit(code)

    def on_butt_group_code(self):
        d = ags4_widgets.AGS4GroupViewDialog(group_code=self.ogtGroup.group_code)
        d.exec_()

    def on_view_change(self, idx):
        return
        self.stackWidget.setCurrentIndex(idx)
