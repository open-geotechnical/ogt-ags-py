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

    def __init__( self, parent=None, doc=None):
        QtGui.QWidget.__init__( self, parent )

        self.doc = doc
        self.debug = False
        self.head_code = None

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

    def set_data(self, hrec):

        self.head_code = hrec['head_code']

        descr = None
        if "data_dict" in hrec and isinstance(hrec['data_dict'], dict):
            descr = hrec['data_dict'].get('head_description')
        self.lblHeadDescription.setText("-" if descr == None else descr)

        self.lblUnit.setText("-" if hrec["unit"] else hrec["unit"])
        #typ = "<a href="""
        self.lblType.setText(hrec["type"])
        #self.lblType.setToolTip(hrec['type'])

        #print hrec['type'], self.doc.type(hrec['type'])
        typ = ags4.AGS4.data_type(hrec['type'])
        if typ:
            self.lblType.setToolTip(typ['description'])
        else:
            self.lblType.setToolTip(hrec['type'])

    def on_goto(self):
        self.sigGoto.emit(self.head_code)

class OGTGroupWidget( QtGui.QWidget ):
    """Shows a group with labels at top, and table underneath"""

    sigGoto = pyqtSignal(str)

    def __init__( self, parent, doc):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False
        self.doc = doc
        self.ogtGroup = None

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        ## titles
        topLay = QtGui.QHBoxLayout()
        topLay.setSpacing(0)
        topLay.setContentsMargins(0,0,0,0)
        self.mainLayout.addLayout(topLay, 0)

        sty = "background-color: #333333; color: #dddddd; padding: 2px;"

        self.lblGroupCode = QtGui.QLabel()
        self.lblGroupCode.setStyleSheet(sty + "font-weight: bold; font-size: 14pt; font-family: monospace;")
        topLay.addWidget(self.lblGroupCode, 0)

        self.lblGroupDescription = QtGui.QLabel()
        self.lblGroupDescription.setStyleSheet(sty + "")
        topLay.addWidget(self.lblGroupDescription, 100)

        self.table = QtGui.QTableWidget()
        self.mainLayout.addWidget(self.table, 200)


    def load_group(self, ogtGroup):

        self.ogtGroup = ogtGroup
        ## Set the labels
        self.lblGroupCode.setText( self.ogtGroup.group_code  )

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
        print self.ogtGroup.headings
        for hcode, hrec in self.ogtGroup.headings_list():
            print cidx, hrec
            hitem = xwidgets.XTableWidgetItem()
            hitem.set(hrec['head_code'], bold=True)
            self.table.setHorizontalHeaderItem(cidx, hitem)

            header_widget = OGTHeaderWidget(doc=self.doc)
            header_widget.set_data(hrec)

            self.table.setCellWidget(0, cidx, header_widget )
            header_widget.sigGoto.connect(self.on_goto)

        self.table.setRowHeight(0, HEADER_HEIGHT)
        v_labels.append("")

        # Load the data
        for ridx, row in enumerate(self.data()):

            self.table.setRowCount( self.table.rowCount() + 1)
            v_labels.append( str(ridx + 1) )

            for cidx, hrec in enumerate(headings):
                #print hrec, row
                item = QtGui.QTableWidgetItem()
                item.setText(row[hrec["head_code"]])
                self.table.setItem(ridx + 1, cidx, item)

                if hrec['type'] == "PA":
                    # Combo dropdown
                    self.table.setItemDelegateForColumn(cidx, ags4_widgets.PickListComboDelegate(self, hrec))
                    item.setBackgroundColor(QtGui.QColor("#FFFDBF"))

                if hrec['type'] in ["2DP"]:
                    # Number editor
                    item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                    self.table.setItemDelegateForColumn(cidx, ags4_widgets.NumberEditDelegate(self, hrec))


                if hrec['type'] == "ID":
                    #print hrec
                    if self.group_code  == hrec['head_code'].split("_")[0]:
                        # in same group as heading, so highlight the ID
                        item.setBackgroundColor(QtGui.QColor("#FFF96C"))
                    else:
                        # Dropdown for ID
                        data = self.doc.column_data(hrec['head_code'])
                        self.table.setItemDelegateForColumn(cidx, ags4_widgets.IDComboDelegate(self, hrec, options=data))
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

