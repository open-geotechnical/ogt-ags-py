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

        sty = "background-color: #dddddd; color: black; padding: 2px; font-size: 8pt;"

        # description
        row = 0
        self.lblHeadDescription = QtGui.QLabel()
        self.lblHeadDescription.setStyleSheet(sty)
        self.lblHeadDescription.setFixedHeight(60)
        self.lblHeadDescription.setWordWrap(True)
        self.lblHeadDescription.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.mainLayout.addWidget(self.lblHeadDescription, row, 0, 1, 3)


        # unit
        row += 1
        lbl = xwidgets.label("Unit:", align=Qt.AlignRight, style=sty)
        self.mainLayout.addWidget(lbl, row, 0)

        self.lblUnit = xwidgets.label("-", bold=True, style=sty + "color: #000099;")
        self.mainLayout.addWidget(self.lblUnit, row, 1, 1, 2)

        # Type
        row += 1
        lbl = xwidgets.label("Type:", align=Qt.AlignRight, style=sty )
        self.mainLayout.addWidget(lbl, row, 0)

        self.lblType = xwidgets.label("-", bold=True, style=sty + "color: #000099;" )
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

    def set_data(self, ogtHeading):

        self.ogtHeading = ogtHeading

        descr = self.ogtHeading.head_description
        self.lblHeadDescription.setText("-" if descr == None else descr)

        self.lblUnit.setText("-" if self.ogtHeading.unit == None else self.ogtHeading.unit)
        #typ = "<a href="""
        self.lblType.setText(self.ogtHeading.type)
        #self.lblType.setToolTip(hrec['type'])

        #print hrec['type'], self.doc.type(hrec['type'])
        typ = ags4.AGS4.data_type(self.ogtHeading.type)
        if typ:
            self.lblType.setToolTip(typ['description'])
        else:
            self.lblType.setToolTip(self.ogtHeading.type)

    def on_goto(self):
        self.sigGoto.emit(self.ogtHeading.head_code)

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

        self.table = QtGui.QTableWidget()
        self.mainLayout.addWidget(self.table, 200)


    def load_group(self, ogtGroup):

        self.ogtGroup = ogtGroup
        ## Set the labels
        self.buttGroupCode.setText( self.ogtGroup.group_code  )

        descr = None
        if ogtGroup.data_dict():
            descr = self.ogtGroup.data_dict().group_description()
        self.lblGroupDescription.setText( "-" if descr == None else descr )



        # Init table, first row = 0 is headings (cos we cant embed widgets in a header on pyqt4)
        #headings = self.ogtGroup.headings()
        self.table.setRowCount(1)
        self.table.setColumnCount( self.ogtGroup.headings_count() )

        v_labels = QtCore.QStringList() # vertical labels

        ## Populate header
        HEADER_HEIGHT = 80
        #print self.ogtGroup.headings
        for cidx, heading in enumerate(self.ogtGroup.headings_list()):

            hitem = xwidgets.XTableWidgetItem()
            hitem.set(heading.head_code, bold=True)
            self.table.setHorizontalHeaderItem(cidx, hitem)

            header_widget = OGTHeaderWidget(ogtDoc=self.ogtGroup.parentDoc)
            header_widget.set_data(heading)

            self.table.setCellWidget(0, cidx, header_widget )
            header_widget.sigGoto.connect(self.on_goto)

        self.table.setRowHeight(0, HEADER_HEIGHT)
        v_labels.append("")

        # Load the data
        for ridx, row in enumerate(self.ogtGroup.data):

            self.table.setRowCount( self.table.rowCount() + 1)
            v_labels.append( str(ridx + 1) )

            for cidx, heading in enumerate(self.ogtGroup.headings_list()):
                #print hrec, row
                item = QtGui.QTableWidgetItem()
                item.setText(row[heading.head_code])
                self.table.setItem(ridx + 1, cidx, item)

                if heading.type == "PA":
                    # Combo dropdown
                    self.table.setItemDelegateForColumn(cidx, ags4_widgets.PickListComboDelegate(self, heading))
                    item.setBackgroundColor(QtGui.QColor("#FFFDBF"))

                if heading.type in ["2DP"]:
                    # Number editor
                    item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                    self.table.setItemDelegateForColumn(cidx, ags4_widgets.NumberEditDelegate(self, heading))


                if heading.type == "ID":
                    #print hrec
                    if self.ogtGroup.group_code  == heading.head_code.split("_")[0]:
                        # in same group as heading, so highlight the ID
                        item.setBackgroundColor(QtGui.QColor("#FFF96C"))
                    else:
                        # Dropdown for ID
                        optts = self.ogtGroup.parentDoc.column_data(heading.head_code)
                        self.table.setItemDelegateForColumn(cidx, ags4_widgets.IDComboDelegate(self, heading, options=optts))
                        self.table.cellWidget(0, cidx).set_link(True)
                        item.setBackgroundColor(QtGui.QColor("#FFFDBF"))


        # resize columns, with max_width
        col_width = 200

        self.table.resizeColumnsToContents()
        for cidx in range(0, self.table.columnCount()):
            if self.table.columnWidth(cidx) > col_width:
                self.table.setColumnWidth(cidx, col_width)

        self.table.setVerticalHeaderLabels(v_labels)

    def on_goto(self, code):
        print "on_goto", code, self
        self.sigGoto.emit(code)

    def on_butt_group_code(self):
        d = ags4_widgets.AGS4GroupViewDialog(group_code=self.ogtGroup.group_code)
        d.exec_()
