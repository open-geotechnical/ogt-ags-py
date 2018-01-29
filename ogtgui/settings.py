# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

#import os
#import sys
import json

from Qt import Qt, QtCore


import app_globals as G

class Srv(object):

    def __init__(self, name=None, ki=None, url=None):
        self.name = name
        self.ki = ki
        self.url = url


    def __repr__(self):
        return "<Src url=%s>"

class XSettings( QtCore.QObject ):

    CURR_SERVER_KI = "current/server_ki"

    def __init__( self, parent=None ):
        QtCore.QObject.__init__( self, parent )

        self.qsettings = QtCore.QSettings("AGS", "ags-desktop-pyqt")

        self.servers = {}

        self.servers['online'] = Srv(**{'name': 'Online', "ki": "live",
                                    'url': 'http://ags.daffodil.uk.com'})

        self.servers['dev'] = Srv(**{'name': 'Developer', "ki": "dev",
                                    'url': 'http://localhost:13777'})

    def set_current_server( self, ki ):
        self.qsettings.setValue( self.CURR_SERVER_KI, ki )
        self.qsettings.sync()
        if ki in self.servers:
            self._current_server = self.servers[ki]
        return self._current_server

    def current_server( self ):
        ki = str( self.qsettings.value( self.CURR_SERVER_KI ) )
        if ki in self.servers:
            return self.server[ki]
        return self.servers["dev"]

    ##==============================
    ## Window Save/Restore
    def save_window( self, window ):
        name = window.objectName()
        if len(name) == 0:
            return
        self.qsettings.setValue( "window/%s/geometry" % name, QtCore.QVariant( window.saveGeometry() ) )

    def restore_window( self, window ):
        name = str(window.objectName())
        if len(name) == 0:
            return
        window.restoreGeometry( self.qsettings.value( "window/%s/geometry" % name ).toByteArray() )


    def save_splitter(self, splitter):
        wname = str(splitter.objectName())
        if not wname:
            print "Splitter has no name", splitter
        self.qsettings.setValue("splitter/%s" % wname, splitter.saveState())

    def restore_splitter(self, splitter):
        wname = str(splitter.objectName())
        if not wname :
            print "Splitter has no name"
        splitter.restoreState(self.qsettings.value("splitter/%s" % wname).toByteArray())

    def save_list(self, key, lst):
        self.qsettings.setValue(key, json.dumps(lst))
        self.qsettings.sync()

    def get_list(self, key):
        s = str(self.qsettings.value(key).toString())
        if s == None or s == "":
            return []
        return json.loads(s)
