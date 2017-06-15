# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

from Qt import QtGui, QtCore, Qt, pyqtSignal

import app_globals as G

import ogt.ags4
from . import ogtgui_group
from .img import Ico

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


    def init(self):
        #self.fetch()
        pass

    def fetch(self, example=None):
        """Send request to server"""
        url = "/ags/4/parse"
        params = None

        if example:
            params = dict(example=example)

        G.server.get(origin=self, url=url, params=params)



    def load_reply(self, xreply):
        """Got a reply from server.."""
        #print self, xreply

        if xreply.origin != self:
            return

        if not "document" in xreply.data:
            return # SHould not happen

        # loop the groups and add the tabs,...
        for dic in xreply.data["document"]["groups"]:

            widget = self.load_group(dic)


    def load_ags4_file(self, file_path):

        self.file_path = None

        doc = ags4.AGS4Document()
        doc.opts.edit_mode = True
        err = doc.load_from_file(file_path)
        print "err=", err

        self.load_document(doc)


    def load_document(self, doc):

        self.doc = doc

        data = doc.to_dict()
        for gkey in data['groups']:
            self.load_group( data['groups'].get(gkey) )


    def load_group(self, group_dic):
        print group_dic
        widget = ogtgui_group.OGTGroupWidget(self)
        self.tabBar.addTab(Ico.icon(Ico.Group), group_dic['group_code'])

        self.stackWidget.addWidget(widget)
        widget.load_group(group_dic)

        #self.tabBar.setCurrentIndex(self.tabBar.count() - 1)

        return widget


    def on_tab_changed(self, idx):
        # TODO check is theres an edit. ebore tab change maybe
        #print "idx", idx
        self.stackWidget.setCurrentIndex(idx)


