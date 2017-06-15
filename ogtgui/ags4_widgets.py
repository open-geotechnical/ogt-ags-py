# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

import os
from Qt import QtGui, QtCore, Qt, pyqtSignal

import app_globals as G

#from ogt import utils
from .img import Ico
from . import xwidgets
from ags4_models import CG, CH,CA, SHOW_NONE, AGS_COLORS


class AGS4_DataDictBrowser( QtGui.QWidget ):

    def __init__( self, parent=None, mode=None ):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        ##=============================================================
        self.tabWidget = QtGui.QTabWidget()
        self.mainLayout.addWidget(self.tabWidget)




        ##=============================================================
        self.agsGroupsWidget = AGS4_GroupsBrowser(self)
        self.tabWidget.addTab(self.agsGroupsWidget, Ico.icon(Ico.AgsGroups), "Groups")

        ##=============================================================
        #self.agsAbbrevsWidget = AgsAbbrevsWidget.AgsAbbrevsWidget(self)
        #self.tabWidget.addTab(self.agsAbbrevsWidget,dIco.icon(dIco.AgsAbbrevs),  "Abbreviations / Pick lists")

        ##=============================================================
        #self.agsUnitsWidget = AgsUnitsWidget.AgsUnitsWidget(self)
        #self.tabWidget.addTab(self.agsUnitsWidget, dIco.icon(dIco.AgsUnits), "Units")


    def init(self):

        #self.fetch()
        #G.Ags.festch()

        self.tabWidget.setCurrentIndex(0)


class AGS4_GroupsBrowser( QtGui.QWidget ):

    sigCodeSelected = pyqtSignal(object)

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = True

        self.proxy = QtGui.QSortFilterProxyModel()
        self.proxy.setSourceModel(G.Ags.modelGroups)
        self.proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        ##===============================================
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)



        self.splitter = QtGui.QSplitter()
        self.mainLayout.addWidget(self.splitter)

        ##############################################################################
        leftWidget = QtGui.QWidget()
        leftLayout = xwidgets.vlayout()
        leftWidget.setLayout(leftLayout)
        self.splitter.addWidget(leftWidget)

        ##================================
        ## Classification
        topLayout = QtGui.QHBoxLayout()
        leftLayout.addLayout(topLayout, 0)
        self.treeClass = QtGui.QTreeView()
        topLayout.addWidget(self.treeClass, 3)
        self.treeClass.setModel(G.Ags.modelClasses)
        self.treeClass.setRootIsDecorated(False)

        self.treeClass.setExpandsOnDoubleClick(False)

        self.treeClass.setFixedHeight(250)

        self.treeClass.selectionModel().selectionChanged.connect(self.on_class_selection)


        ##================================
        ## Filter Widget
        rLay = QtGui.QVBoxLayout()
        topLayout.addLayout(rLay)

        grpFilter = xwidgets.GroupGridBox("Filter by")
        #mmm = 20
        #grpFilter.setContentsMargins(mmm,mmm,mmm,mmm)
        grpFilter.grid.setSpacing(5)
        grpFilter.setFixedWidth(150)
        rLay.addWidget(grpFilter, 1)

        ## Buttons
        self.buttGrp = QtGui.QButtonGroup()
        self.buttGrp.setExclusive(True)
        self.connect(self.buttGrp, QtCore.SIGNAL("buttonClicked(int)"), self.on_filter_col)

        row = 0
        self.buttFilterCode = QtGui.QRadioButton()
        grpFilter.grid.addWidget(self.buttFilterCode, row , 1)
        self.buttFilterCode.setText("Code")
        self.buttGrp.addButton(self.buttFilterCode, CG.code)

        row += 1
        self.buttFilterDesc = QtGui.QRadioButton()
        grpFilter.grid.addWidget(self.buttFilterDesc, row , 1)
        self.buttFilterDesc.setText("Description")
        self.buttGrp.addButton(self.buttFilterDesc, CG.description)


        row += 1
        self.buttFilterAll = QtGui.QRadioButton()
        grpFilter.grid.addWidget(self.buttFilterAll, row , 1)
        self.buttFilterAll.setText("Both")
        self.buttFilterAll.setChecked(True)
        self.buttGrp.addButton(self.buttFilterAll, CG.search)



        row += 1
        self.buttClear = xwidgets.ClearButton(self, callback=self.on_clear_filter)
        grpFilter.grid.addWidget(self.buttClear, row , 0)

        self.txtCode = QtGui.QLineEdit()
        self.txtCode.setMaximumWidth(100)
        grpFilter.grid.addWidget(self.txtCode, row, 1)
        self.txtCode.textChanged.connect(self.on_txt_changed)

        grpFilter.grid.setColumnStretch(0, 0)
        grpFilter.grid.setColumnStretch(1, 10)
        rLay.addStretch(1)

        ##===============================================
        self.tree = QtGui.QTreeView()
        leftLayout.addWidget(self.tree, 10)
        self.tree.setUniformRowHeights(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(True)
        self.tree.setModel(self.proxy)
        self.tree.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        self.tree.header().setStretchLastSection(True)
        self.tree.setColumnHidden(CG.search, True)
        self.tree.setColumnHidden(CG.x_id, True)
        #self.tree.setColumnHidden(C.abbrev_id, True)

        self.tree.setColumnWidth(CG.code, 120)
        self.tree.setColumnWidth(CG.description, 250)
        #self.tree.setColumnWidth(CG.cls, 150)


        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.selectionModel().selectionChanged.connect(self.on_tree_selected)

        self.tree.sortByColumn(CG.code)


        self.agsGroupViewWidget = AGS4_GroupViewWidget(self)
        self.splitter.addWidget(self.agsGroupViewWidget)

        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 5)
        #self.statusBar = StatusBar(self, False)
        #self.mainLayout.addWidget(self.statusBar, 0)


        ##############################################################################
        rightWidget = QtGui.QWidget()
        rightLayout = xwidgets.vlayout()
        rightWidget.setLayout(rightLayout)
        self.splitter.addWidget(rightWidget)


        self.agsHeadingDetailWidget = AGS4_HeadingDetailWidget()
        rightLayout.addWidget(self.agsHeadingDetailWidget)

        #self.init_setup()
        G.Ags.sigLoaded.connect(self.on_loaded)
        self.agsGroupViewWidget.sigHeadCodeSelected.connect(self.agsHeadingDetailWidget.load_heading)




    def init(self):
        pass



    #=========================================
    def on_tree_selected(self, sel, desel):

        if not self.tree.selectionModel().hasSelection():
             self.sigCodeSelected.emit( None )
             return

        selidx = sel.indexes()[0]
        srcidx = self.proxy.mapToSource(selidx)

        model = self.proxy.sourceModel()
        tIdx = model.index(srcidx.row(), CG.code, srcidx.parent())
        item = model.itemFromIndex( tIdx )

        group_code = str(item.text())
        self.agsGroupViewWidget.load_group(group_code)
        self.sigCodeSelected.emit( group_code )




    def on_filter_col(self, idx):
        self.update_filter()
        self.txtCode.setFocus()

    def on_txt_changed(self, x):
        self.update_filter()

    def update_filter(self):
        #print "update_filter", self.tabWidget.currentIndex(), self
        self.treeClass.blockSignals(True)
        self.treeClass.clearSelection()
        self.treeClass.blockSignals(False)

        self.proxy.setFilterKeyColumn(self.buttGrp.checkedId())
        self.proxy.setFilterFixedString(self.txtCode.text())



    def on_clear_filter(self):
        self.txtCode.setText("")
        self.txtCode.setFocus()



    def on_class_selection(self, selected, deselected):
        if not self.treeClass.selectionModel().hasSelection():
            return

        self.proxy.setFilterKeyColumn(CG.cls)

        item = self.treeClass.model().itemFromIndex(selected.indexes()[0])
        if item.text() == "All":
            self.proxy.setFilterFixedString("")
        else:
            self.proxy.setFilterFixedString(item.text())

    def deadon_tree_context_menu(self, point):

        if not self.tree.selectionModel().hasSelection():
            return#

    def init(self):
        pass

    def on_loaded(self):
        # expand first row, set sort orders
        self.treeClass.setExpanded( self.treeClass.model().item(0,0).index(), True)
        self.treeClass.sortByColumn(0, Qt.AscendingOrder)
        self.tree.sortByColumn(CG.code, Qt.AscendingOrder)

        self.tree.resizeColumnToContents(CG.code)


class AGS4_GroupViewWidget( QtGui.QWidget ):
    """The GroupView contains the vertically the Group Label at top, headings and notes"""

    sigHeadCodeSelected = pyqtSignal(object)

    def __init__( self, parent, mode=None ):
        QtGui.QWidget.__init__( self, parent )

        self.debug = True

        self.cache = None

        self.group_by = "none"

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        self.toolbar = xwidgets.hlayout()
        self.mainLayout.addLayout(self.toolbar, 0)

        self.icoLabel = xwidgets.IconLabel(self, ico=Ico.AgsGroup)
        self.icoLabel.setStyleSheet("background-color: white; color: #444444;")
        self.toolbar.addWidget(self.icoLabel)

        self.lblGroupCode = QtGui.QLabel(" ")
        self.lblGroupCode.setStyleSheet("background-color: white; color: %s; font-weight: bold; font-family: monospace; padding: 3px;" % AGS_COLORS.group)
        self.toolbar.addWidget(self.lblGroupCode, 1)
        self.lblGroupCode.setFixedWidth(50)

        self.lblDescription = QtGui.QLabel(" ")
        self.lblDescription.setStyleSheet("background-color: white; color: #444444;")
        self.toolbar.addWidget(self.lblDescription, 3)

        self.mainLayout.addSpacing(10)

        #self.tabWidget = QtGui.QTabWidget()
        #self.mainLayout.addWidget(self.tabWidget)

        #self.lblHeadings = Widgets.Label(text="Headings")
        #self.mainLayout.addWidget(self.lblHeadings, 0)



        self.agsHeadingsTable = AGS4_HeadingsTable(self)
        self.mainLayout.addWidget(self.agsHeadingsTable, 10)

        #self.tabWidget.addTab(self.agsHeadingsTable, dIco.icon(dIco.AgsField), "Headings")
        #self.lblNotes = Widgets.Label(text="Notes")
        #self.mainLayout.addWidget(self.lblNotes, 0)


        self.agsGroupNotesTable = AGS4_GroupNotesTable(self)
        self.agsGroupNotesTable.setFixedHeight(200)
        self.mainLayout.addWidget(self.agsGroupNotesTable)
        #self.tabWidget.addTab(self.agsGroupNotesTable, dIco.icon(dIco.AgsNotes), "Notes")
        #self.connect(self.agsGroupNotesTable, QtCore.SIGNAL("loaded"), self.on_notes_loaded)

        self.agsHeadingsTable.sigHeadCodeSelected.connect(self.on_head_code)

    def on_head_code(self, head_code):
        self.sigHeadCodeSelected.emit(head_code)

    def on_notes_loaded(self, c):
        self.tabWidget.setTabText(1, "Notes - %s" % (c if c > 0 else "None") )

    def clear(self):
        self.lblGroupCode.setText("")
        self.lblDescription.setText("")
        self.agsGroupNotesTable.clear()

    def load_group(self, group_code):

        if group_code == None:
            self.agsHeadingsTable.filter_headings()
            return


        g = G.Ags.get_group(group_code)
        #print group_code, g



        self.lblGroupCode.setText(g['group_code'])
        self.lblDescription.setText(g['group_description'])

        if False:
            self.tabWidget.setTabText(0, "Headings - %s" % len(g['headings']))
            if len(g['notes']) == 0:
                s = "None"
            else:
                s = len(g['notes'])
            self.tabWidget.setTabText(1, "Notes - %s" % s)

        self.agsHeadingsTable.filter_headings(g['group_code'])
        self.agsGroupNotesTable.load_notes(g['group_code'])



class AGS4_HeadingsTable( QtGui.QWidget ):

    sigHeadCodeSelected = pyqtSignal(object)
    """A row has been selected or delelected

    :return: HeadCode or `None`
    """



    def __init__( self, parent ):
        QtGui.QWidget.__init__( self, parent )

        self.debug = True

        self.cache = None

        self.proxy = QtGui.QSortFilterProxyModel()
        self.proxy.setSourceModel(G.Ags.modelHeadings)
        self.proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(CH.group_code)
        self.proxy.setFilterFixedString(SHOW_NONE)


        self.group_code = None


        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        ##===============================================================
        self.tree = QtGui.QTreeView()
        self.mainLayout.addWidget(self.tree)
        self.tree.setUniformRowHeights(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(False)

        self.tree.setModel(self.proxy)


        for c in [CH.example, CH.group_code,  CH.sort]:
            pass #self.tree.setColumnHidden(c, True)
        self.tree.setColumnWidth(CH.head_code, 100)
        self.tree.setColumnWidth(CH.unit, 50)
        self.tree.setColumnWidth(CH.status, 40)
        self.tree.setColumnWidth(CH.data_type, 50)

        self.tree.header().setStretchLastSection(True)

        self.tree.setSortingEnabled(True)

        self.tree.selectionModel().selectionChanged.connect(self.on_tree_selected)

        #self.statusBar = StatusBar(self, True)
        #self.mainLayout.addWidget(self.statusBar, 0)
        #self.statusBar.hide()




    def filter_headings(self, gc=None):

        self.group_code = SHOW_NONE if gc == None else gc


        self.proxy.setFilterFixedString(self.group_code)

    #=========================================
    def on_tree_selected(self, sel, desel):

        if not self.tree.selectionModel().hasSelection():
             self.sigHeadCodeSelected.emit( None )
             return

        selidx = sel.indexes()[0]
        srcidx = self.proxy.mapToSource(selidx)

        model = self.proxy.sourceModel()
        tIdx = model.index(srcidx.row(), CH.head_code, srcidx.parent())
        item = model.itemFromIndex( tIdx )

        head_code = str(item.text())
        self.sigHeadCodeSelected.emit(head_code)



    def on_tree_context_menu(self, point):

        if not self.tree.selectionModel().hasSelection():
            return

    def deadon_butt_pop(self, butt):
        code =  str(butt.property("code").toString())

        p = self.mapFromGlobal(QtGui.QCursor.pos())
        #print p
        p = QtGui.QCursor.pos()
        d = ags.AgsAbbrevPopDialog.AgsAbbrevPopDialog(self, abrev_code=code)

        d.move(p.x() - 50, 100)
        d.exec_()


class CN:
    node = 0
    note_id = 1
    so = 2


class AGS4_GroupNotesTable( QtGui.QWidget ):

    sigLoaded = pyqtSignal(int, object)

    def __init__( self, parent, mode=None ):
        QtGui.QWidget.__init__( self, parent )

        self.debug = True

        self.cache = None

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        ##==============================
        scrollArea = QtGui.QScrollArea()
        scrollArea.setWidgetResizable(True)
        self.mainLayout.addWidget(scrollArea, 100)

        self.scrollWidget = QtGui.QWidget()
        #self.mainLayout.addWidget(self.noticesListWidget, 100)
        scrollArea.setWidget(self.scrollWidget)

        self.scrollLayout = QtGui.QVBoxLayout()
        self.scrollLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollLayout.setSpacing(0)
        self.scrollWidget.setLayout(self.scrollLayout)



    def clear(self):
        """Removes all QLabel entries"""
        ## pain.. all this shite just to nuke a list
        self.setUpdatesEnabled(False)
        while self.scrollLayout.count() > 0:
            vari = self.scrollLayout.itemAt(0)
            w = vari.widget()
            if w:
                self.scrollLayout.removeWidget( w )
                w.setParent(None)
                w = None
            else:
                self.scrollLayout.removeItem( vari )

        self.setUpdatesEnabled(True)
        self.update()



    def load_notes(self, group_code):
        """Loads group notes

        :param group_code: The four character group code

        """
        lookup = G.Ags.get_words()


        self.clear()
        notes = G.Ags.get_notes(group_code)
        #print notes

        if notes == None:
            return

        self.setUpdatesEnabled(False)
        for note in notes:

            w = widget = QtGui.QLabel()

            words = note.split(" ")
            res = []
            for word in words:
                #print word
                if word in lookup:
                    res.append("<a href='#%s-%s'>%s</a>" % (lookup[word]['type'], word, word))
                else:
                    res.append(word)

            widget.setText(" ".join(res))
            widget.setTextFormat(QtCore.Qt.RichText)
            widget.setWordWrap(True)
            widget.setMargin(0)
            widget.setStyleSheet("background-color: #C3F6A9; padding: 2px; margin: 0; border-bottom:1px solid #dddddd;")
            widget.setAlignment(QtCore.Qt.AlignTop)

            self.scrollLayout.addWidget(w, 0)
            self.connect(widget, QtCore.SIGNAL("linkHovered(const QString)"), self.on_link_hover)

        #if len(notes) < 4:
        self.scrollLayout.addStretch(10)
        self.setUpdatesEnabled(True)

        self.sigLoaded.emit(len(notes), self)
        #self.emit(QtCore.SIGNAL("loaded"), len(notes), self)

    def on_link_hover(self, lnk):
        #print "link=", lnk
        #self.statusBar.showMessage(lnk)
        print "TODO"

    def on_tree_context_menu(self, point):

        if not self.tree.selectionModel().hasSelection():
            return




class AGS4_HeadingDetailWidget( QtGui.QWidget ):
    """Shows details about a heading, including example, etc"""

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = True

        self.proxy = QtGui.QSortFilterProxyModel()
        self.proxy.setSourceModel(G.Ags.modelAbbrItems)
        self.proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(CA.head_code)
        self.proxy.setFilterFixedString(SHOW_NONE)

        ##===============================================
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        self.toolbar = xwidgets.hlayout()
        self.mainLayout.addLayout(self.toolbar, 0)

        self.icoLabel = xwidgets.IconLabel(self, ico=Ico.AgsGroup)
        self.icoLabel.setStyleSheet("background-color: white; color: #444444;")
        self.toolbar.addWidget(self.icoLabel)

        self.lblAbbrCode = QtGui.QLabel(" ")
        self.lblAbbrCode.setStyleSheet("background-color: white; color: %s; font-weight: bold; font-family: monospace; padding: 3px;" % AGS_COLORS.group)
        self.toolbar.addWidget(self.lblAbbrCode, 1)
        self.lblAbbrCode.setFixedWidth(50)


        self.splitter = QtGui.QSplitter()
        self.mainLayout.addWidget(self.splitter)

        ##===============================================================
        self.tree = QtGui.QTreeView()
        self.mainLayout.addWidget(self.tree)
        self.tree.setUniformRowHeights(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(False)

        self.tree.setModel(self.proxy)


        for c in [CA.head_code]:
            pass #self.tree.setColumnHidden(c, True)
        self.tree.setColumnWidth(CA.code, 100)
        self.tree.setColumnWidth(CA.description, 50)
        self.tree.setColumnWidth(CA.head_code, 40)


        self.tree.header().setStretchLastSection(True)

        # TODO fix sort to ags
        self.tree.setSortingEnabled(True)




    def load_heading(self, head_code):

        self.proxy.setFilterFixedString(SHOW_NONE if head_code == None else head_code)
