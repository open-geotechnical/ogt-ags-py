# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

import os

from Qt import QtGui, QtCore

from ogtgui import ICONS_PATH


class Ico:
    """Icons Definition and Loader

      - All icons used are listed as class constants.
      - Static methods create icons loaded from the file system

      .. todo:: try and intercept __getattr__ to return qIcon
    """



    @staticmethod
    def icon( file_name, pixmap=False, size=None):
        """Creates a QIcon

        @param file_name: Icon filename to load
        @type file_name: str or L{dIco} attribute
        @param pixmap: Return a pixmap instead of icon object
        @type pixmap: bool
        @return: new Icon
        @rtype: QIcon or pixmap
        """
        if file_name == None:
            qicon = QtGui.QIcon()
        else:
            qicon = QtGui.QIcon( os.path.join(ICONS_PATH, file_name) )

        if pixmap:
            return qicon.pixmap( QtCore.QSize( 16, 16 ) )

        if size:
            pass #icon2 = QtGui.QIcon( icon.pixmap( QtCore.QSize(size, size) ) )
            #return icon2

        return qicon

    Add = "add.png"

    Ags3 = "ags3.svg.png"
    Ags4 = "ags4.svg.png"

    AgsAbbrev = "font.png"
    AgsAbbrevItem = "textfield_rename.png"

    AgsField = "textfield.png"

    AgsGroup = "layout.png"
    AgsGroups = "layers.png"
    AgsHeading = "layout_header.png"
    AgsNotes = "note.png"

    Busy = "arrow_in.png"

    Clear = "control.png"

    Document = "blue-folder-open-document.png"

    Export = "fill.png"

    FavIcon = "user-worker-boss.png"

    Folder = 'folder.png'
    FolderAdd = 'folder_add.png'
    FolderCopy = 'folder_page.png'
    FolderDelete = 'folder_delete.png'
    FolderOpen = 'folder_go.png'
    FolderRename = 'folder_edit.png'

    Groups = "tables-stacks.png"
    Group = "table.png"

    Import = "arrow-join-270.png"

    Project = "blue-document-list.png"

    Map = "map.png"

    Quit = 'control_eject.png'

    Refresh = "arrow_refresh.png"

    Schedule = "table-heatmap.png"
    Source = "document-text.png"
    Summary = "page_white_swoosh.png"

    TypeCheckBox = "ui-checkbox.png"
    TypeDate = "ui-combo-box-calendar.png"
    TypeDecimal = "ui-text-field-password-green.png"
    TypeID = "type_id.svg.png"
    TypePicklist = "ui-combo-box-blue.png"
    TypeSci = "ui-text-field-password-yellow.png"
    TypeStandard = "ui-.png"
    TypeText = "ui-text-field.png"
    TypeUnknown = "ui-text-field-hidden.png"


