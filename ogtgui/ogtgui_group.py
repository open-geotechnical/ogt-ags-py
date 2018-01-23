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
        


class OGTTableHeaderWidget( QtGui.QWidget ):
    """The HEADER info which in row 0 """

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
        self.mainLayout.addWidget(self.lblHeadDescription, row, 0, 1, 2)


        # unit
        row += 1
        lbl = xwidgets.label("Unit:", align=Qt.AlignRight, style=sty)
        self.mainLayout.addWidget(lbl, row, 0)

        self.lblUnit = xwidgets.label("-", bold=True, style=sty + "color: #000099;")
        self.mainLayout.addWidget(self.lblUnit, row, 1)

        # Type
        row += 1
        lbl = xwidgets.label("Type:", align=Qt.AlignRight, style=sty )
        self.mainLayout.addWidget(lbl, row, 0)

        self.lblType = xwidgets.label("-", bold=True, style=sty + "color: #000099;" )
        self.mainLayout.addWidget(self.lblType, row, 1)


        self.mainLayout.setColumnStretch(0, 1)
        self.mainLayout.setColumnStretch(1, 5)


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
        typ = ags4.data_type(hrec['type'])
        if typ:
            self.lblType.setToolTip(typ['description'])
        else:
            self.lblType.setToolTip(hrec['type'])



class OGTGroupWidget( QtGui.QWidget ):
    """Shows a group with labels at top, and table underneath"""

    def __init__( self, parent, doc):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False
        self.doc = doc

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



    def init(self):
        pass

    def load_group(self, group_dic):

        ## Set the labels
        self.lblGroupCode.setText( group_dic['group_code'] )

        descr = None
        if "data_dict" in group_dic and isinstance(group_dic['data_dict'], dict):
            descr = group_dic['data_dict'].get('group_description')
        self.lblGroupDescription.setText( "-" if descr == None else descr )



        # Init table, first row = 0 is headings (cos we cant embed widgets in a header on pyqt4)
        headings = group_dic['headings']
        self.table.setRowCount(1)
        self.table.setColumnCount( len(headings) )

        v_labels = QtCore.QStringList() # vertical labels

        ## Populate header
        HEADER_HEIGHT = 80
        for cidx, hrec in enumerate(headings):

            hitem = xwidgets.XTableWidgetItem()
            hitem.set(hrec['head_code'], bold=True)
            self.table.setHorizontalHeaderItem(cidx, hitem)

            header_widget = OGTTableHeaderWidget(doc=self.doc)
            header_widget.set_data(hrec)

            self.table.setCellWidget(0, cidx, header_widget )

            ## quick hack for size
            #header_widget.setFixedHeight(HEADER_HEIGHT)
        self.table.setRowHeight(0, HEADER_HEIGHT)
        v_labels.append("")

        # Load the data
        for ridx, row in enumerate(group_dic['data']):

            self.table.setRowCount( self.table.rowCount() + 1)
            v_labels.append( str(ridx + 1) )

            for cidx, hrec in enumerate(headings):
                #print hrec, row
                item = QtGui.QTableWidgetItem()
                item.setText(row[hrec["head_code"]])
                self.table.setItem(ridx + 1, cidx, item)

                if hrec['type'] == "PA":
                    self.table.setItemDelegateForColumn(cidx, ags4_widgets.PickListComboDelegate(self, hrec["head_code"]))


        # resize columns, with max_width
        col_width = 200

        self.table.resizeColumnsToContents()
        for cidx in range(0, self.table.columnCount()):
            if self.table.columnWidth(cidx) > col_width:
                self.table.setColumnWidth(cidx, col_width)

        self.table.setVerticalHeaderLabels(v_labels)
