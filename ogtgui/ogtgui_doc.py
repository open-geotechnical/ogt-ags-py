# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

from Qt import QtGui, QtCore, Qt, pyqtSignal

import app_globals as G

from ogt import ogt_doc
import ogtgui_group
from img import Ico

class OGTDocumentWidget( QtGui.QWidget ):

    sigUpdated = pyqtSignal(object)

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False

        self.file_path = None
        self.doc = None

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        self.tabBar = QtGui.QTabBar()
        self.mainLayout.addWidget(self.tabBar)

        self.stackWidget = QtGui.QStackedWidget()
        self.mainLayout.addWidget(self.stackWidget)

        self.tabBar.currentChanged.connect(self.on_tab_changed)


    def init_load(self):
        #self.fetch()
        pass

    # def fetch(self, example=None):
    #     """Send request to server"""
    #     url = "/ags/4/parse"
    #     params = None
    #
    #     if example:
    #         params = dict(example=example)
    #
    #     G.server.get(origin=self, url=url, params=params)
    #
    #
    #
    # def load_reply(self, xreply):
    #     """Got a reply from server.."""
    #     #print self, xreply
    #
    #     if xreply.origin != self:
    #         return
    #
    #     if not "document" in xreply.data:
    #         return # SHould not happen
    #
    #     # loop the groups and add the tabs,...
    #     for dic in xreply.data["document"]["groups"]:
    #
    #         widget = self.load_group(dic)


    def load_ags4_file(self, file_path):

        self.file_path = None

        doc = ogt_doc.OGTDocument()
        #doc.opts.edit_mode = True
        err = doc.load_ags4_file(file_path)


        self.load_document(doc)


    def load_document(self, ogtdoc):

        self.ogtDoc = ogtdoc
        #print "doc=", doc
        #data = doc.to_dict()
        for gkey in self.ogtDoc.groups_sort():
            self.load_group( self.ogtDoc.group(gkey) )


    def load_group(self, ogtGrp):
        print "load_group", ogtGrp, self
        widget = ogtgui_group.OGTGroupWidget(self, doc=self.doc)
        idx = self.tabBar.addTab( ogtGrp.group_code)
        if ogtGrp.data_dict():
            self.tabBar.setTabToolTip(idx, ogtGrp.data_dict().group_description())

        self.stackWidget.addWidget(widget)
        widget.load_group(ogtGrp)
        widget.sigGoto.connect(self.on_goto)

        return widget


    def on_tab_changed(self, idx):
        # TODO check is theres an edit. ebore tab change maybe
        #print "idx", idx
        self.stackWidget.setCurrentIndex(idx)


    def on_goto(self, code):
        grp_code = code.split("_")[0]
        for idx in range(0, self.stackWidget.count()):
            if self.stackWidget.widget(idx).ogtGroup.group_code == grp_code:
                self.tabBar.setCurrentIndex(idx)
                #self.stackWidget.widget(idx).select_heading(code)
                return
