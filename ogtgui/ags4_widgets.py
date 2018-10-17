# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

from Qt import QtGui, QtCore, Qt, pyqtSignal

from ogt import ags4

import app_globals as G

from img import Ico
import xwidgets
from ags4_models import CG, AGS4_COLORS, HeadingsModel, AbbrevItemsModel


class AGS4DataDictBrowser( QtGui.QWidget ):

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
        self.agsGroupsWidget = AGS4GroupsBrowser(self)
        self.tabWidget.addTab(self.agsGroupsWidget, Ico.icon(Ico.AgsGroups), "Groups")

        self.unitsTypesWidget = AGS4UnitsTypesWidget(self)
        self.tabWidget.addTab(self.unitsTypesWidget, Ico.icon(Ico.AgsField), "Units && Types")

        ##=============================================================
        #self.agsAbbrevsWidget = AgsAbbrevsWidget.AgsAbbrevsWidget(self)
        #self.tabWidget.addTab(self.agsAbbrevsWidget,dIco.icon(dIco.AgsAbbrevs),  "Abbreviations / Pick lists")

        ##=============================================================
        #self.agsUnitsWidget = AgsUnitsWidget.AgsUnitsWidget(self)
        #self.tabWidget.addTab(self.agsUnitsWidget, dIco.icon(dIco.AgsUnits), "Units")



    def init_load(self):

        # load data dict
        G.ags.init_load()
        #self.tabWidget.setCurrentIndex(1)

        self.agsGroupsWidget.set_focus()


class AGS4GroupsBrowser( QtGui.QWidget ):
    """The left panel with the classes, filter and groups table underneath"""

    sigGroupSelected = pyqtSignal(object)

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False
        self.setObjectName("AGS4GroupsBrowser")

        self.proxy = QtGui.QSortFilterProxyModel()
        self.proxy.setSourceModel(G.ags.modelGroups)
        self.proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)


        ##===============================================
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        self.splitter = QtGui.QSplitter(self)
        self.splitter.setObjectName(self.objectName() + "groups_splitter")
        self.mainLayout.addWidget(self.splitter)

        ##############################################################################
        leftWidget = QtGui.QWidget()
        leftLayout = xwidgets.vlayout()
        leftWidget.setLayout(leftLayout)
        self.splitter.addWidget(leftWidget)


        self.tabFilter = QtGui.QTabWidget()
        leftLayout.addWidget(self.tabFilter)

        ##================================
        ## Filter
        grpFilter = xwidgets.GroupGridBox()
        mmm = 5
        grpFilter.setContentsMargins(mmm, mmm, mmm, mmm)
        # grpFilter.grid.setSpacing(5)
        # grpFilter.setFixedWidth(150)
        self.tabFilter.addTab(grpFilter, "Filter")


        # filter combo
        self.buttGroupFilter = QtGui.QButtonGroup()
        self.buttGroupFilter.setExclusive(True)

        #self.comboSearchFor = QtGui.QComboBox()
        #grpFilter.addWidget(self.comboSearchFor)
        for ridx, s in enumerate(["Code", "Description", "Code + Description"]):
            rad = QtGui.QRadioButton()
            rad.setText(s)
            grpFilter.grid.addWidget(rad, ridx, 0, 1, 2)
            self.buttGroupFilter.addButton(rad, 3 if ridx == 2 else ridx)

        self.buttGroupFilter.button(0).setChecked(True)
        self.buttGroupFilter.buttonClicked.connect(self.on_filter_col)

        #self.comboSearchFor.addItem("Code", CG.code)
        #self.comboSearchFor.addItem("Description", CG.description)
        #self.comboSearchFor.addItem("Code + Description", CG.search)
        #self.comboSearchFor.setMaximumWidth(150)
        # clear button
        self.buttClear = xwidgets.ClearButton(self, callback=self.on_clear_filter)
        grpFilter.grid.addWidget(self.buttClear, 3, 0)

        ## filter text
        self.txtFilter = QtGui.QLineEdit()
        self.txtFilter.setMaximumWidth(100)
        grpFilter.grid.addWidget(self.txtFilter, 3, 1)
        self.txtFilter.textChanged.connect(self.on_txt_changed)


        grpFilter.grid.addWidget(QtGui.QLabel(), 4, 2)

        #grpFilter.layout.addStretch(3)
        grpFilter.grid.setColumnStretch(0, 0)
        grpFilter.grid.setColumnStretch(1, 10)

        ##================================
        ## Classification Tree
        topLayout = QtGui.QVBoxLayout()
        leftLayout.addLayout(topLayout, 0)

        self.treeClass = QtGui.QTreeView()
        self.tabFilter.addTab(self.treeClass, "By classification")
        self.treeClass.setModel(G.ags.modelClasses)
        self.treeClass.setRootIsDecorated(False)

        self.treeClass.setExpandsOnDoubleClick(False)

        self.treeClass.setFixedHeight(220)

        self.treeClass.selectionModel().selectionChanged.connect(self.on_class_tree_selected)




        ##== Groups Tree
        self.treeGroups = QtGui.QTreeView()
        leftLayout.addWidget(self.treeGroups, 10)
        self.treeGroups.setModel(self.proxy)


        self.treeGroups.setUniformRowHeights(True)
        self.treeGroups.setRootIsDecorated(False)
        self.treeGroups.setAlternatingRowColors(True)

        self.treeGroups.header().setStretchLastSection(True)
        self.treeGroups.setColumnHidden(CG.search, True)
        self.treeGroups.setColumnWidth(CG.code, 120)
        self.treeGroups.setColumnWidth(CG.description, 250)

        self.treeGroups.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeGroups.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        self.treeGroups.setSortingEnabled(True)
        self.treeGroups.sortByColumn(CG.code)

        self.treeGroups.selectionModel().selectionChanged.connect(self.on_groups_tree_selected)

        self.agsGroupViewWidget = AGS4GroupViewWidget(self)
        self.splitter.addWidget(self.agsGroupViewWidget)

        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 5)
        G.settings.restore_splitter(self.splitter)
        self.splitter.splitterMoved.connect(self.on_splitter_moved)

        #self.statusBar = QtGui.QStatusBar()
        #self.mainLayout.addWidget(self.statusBar, 0)


        ##############################################################################
        rightWidget = QtGui.QWidget()
        rightLayout = xwidgets.vlayout()
        rightWidget.setLayout(rightLayout)
        self.splitter.addWidget(rightWidget)


        #self.agsHeadingDetailWidget = AGS4HeadingDetailWidget()
        #rightLayout.addWidget(self.agsHeadingDetailWidget)

        #self.init_setup()
        G.ags.sigLoaded.connect(self.on_loaded)

        self.txtFilter.setText("DETL")

    def on_splitter_moved(self, i, pos):
        G.settings.save_splitter(self.splitter)

    def set_focus(self):
        self.txtFilter.setFocus()


    def init(self):
        print "init", selfs

    def on_proxy_changed(self, tl, br):
        print "changes", tl, bsr

    #=========================================
    def on_groups_tree_selected(self, sel=None, desel=None):

        if not self.treeGroups.selectionModel().hasSelection():
             self.agsGroupViewWidget.set_group( None )
             self.sigGroupSelected.emit( None )
             return

        tIdx = self.proxy.mapToSource( sel.indexes()[0] )
        grp_dic = self.proxy.sourceModel().rec_from_midx( tIdx )
        self.agsGroupViewWidget.set_group(grp_dic)
        self.sigGroupSelected.emit( grp_dic )


    def on_filter_col(self, idx):
        self.update_filter()
        self.txtFilter.setFocus()

    def on_txt_changed(self, x):
        self.update_filter()

    def update_filter(self):
        self.treeClass.blockSignals(True)
        self.treeClass.clearSelection()
        self.treeClass.blockSignals(False)

        cidx = self.buttGroupFilter.checkedId()
        self.proxy.setFilterKeyColumn(cidx)

        txt = str(self.txtFilter.text()).strip()
        if "_" in txt:
            grp_code, _ = txt.split("_")
        else:
            grp_code = txt
        self.proxy.setFilterFixedString(grp_code)

        if self.proxy.rowCount() == 1:

            # TODO
            # #self.tree.selectionModel().select(self.proxy.index(0,0))
            pass


    def on_clear_filter(self):
        self.txtFilter.setText("")
        self.txtFilter.setFocus()



    def on_class_tree_selected(self, selected, deselected):
        if not self.treeClass.selectionModel().hasSelection():
            self.txtFilter.setFocus()
            #self.on_group_tree_selected()
            return

        self.proxy.setFilterKeyColumn(CG.cls)

        item = self.treeClass.model().itemFromIndex(selected.indexes()[0])
        if item.text() == "All":
            self.proxy.setFilterFixedString("")
        else:
            self.proxy.setFilterFixedString(item.text())
        self.txtFilter.setFocus()


    def init_load(self):
        pass

    def on_loaded(self):

        ## expand first row
        self.treeClass.setExpanded( self.treeClass.model().item(0,0).index(), True)
        self.treeClass.sortByColumn(0, Qt.AscendingOrder)

        ## set sort orders
        self.treeGroups.sortByColumn(CG.code, Qt.AscendingOrder)
        self.treeGroups.resizeColumnToContents(CG.code)




class AGS4GroupViewWidget( QtGui.QWidget ):
    """The GroupView contains the vertically the Group Label at top, headings and notes"""

    sigHeadingSelected = pyqtSignal(object)

    def __init__( self, parent=None, mode=None ):
        QtGui.QWidget.__init__( self, parent )

        self.group_code = None

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
        self.lblGroupCode.setStyleSheet("background-color: white; color: %s; font-weight: bold; font-family: monospace; padding: 3px;" % AGS4_COLORS.group)
        self.toolbar.addWidget(self.lblGroupCode, 1)
        self.lblGroupCode.setFixedWidth(50)

        self.lblDescription = QtGui.QLabel(" ")
        self.lblDescription.setStyleSheet("background-color: white; color: #444444;")
        self.toolbar.addWidget(self.lblDescription, 3)

        self.mainLayout.addSpacing(10)

        ## Headings Table
        self.agsHeadingsTable = AGS4HeadingsTable(self)
        self.mainLayout.addWidget(self.agsHeadingsTable, 10)



        ##== Bottom Splitter
        self.splitBott = QtGui.QSplitter()
        self.splitBott.setObjectName("ags_group_view_notes_picklist")
        self.mainLayout.addWidget(self.splitBott)

        ## Notes
        self.agsGroupNotesWidget = AGS4GroupNotesWidget(self)
        self.agsGroupNotesWidget.setFixedHeight(200)
        self.splitBott.addWidget(self.agsGroupNotesWidget)

        ## Abbrs Picklist
        self.agsAbbrevsWidget = AGS4AbbrevsWidget()
        self.splitBott.addWidget(self.agsAbbrevsWidget)


        ## setup splitter
        self.splitBott.setStretchFactor(0, 1)
        self.splitBott.setStretchFactor(1, 1)
        G.settings.restore_splitter(self.splitBott)
        self.splitBott.splitterMoved.connect(self.on_splitter_bott_moved)

        self.agsHeadingsTable.sigHeadingSelected.connect(self.on_heading_selection_changed)
        self.agsGroupNotesWidget.sigWordClicked.connect(self.on_word_clicked)

    def on_word_clicked(self, code):
        code = str(code) # WTF!, its a QString not str as sent !
        rec = ags4.AGS4.words.get(code)
        if rec:

            if rec['type'] == "heading":
                # its a heading, so select it if its in within this group eg SAMP_ID is almost everywhere
                found = self.agsHeadingsTable.select_heading(code)
                if not found:
                    # so its not in this group, so open other group
                    parts = code.split("_")
                    d = AGS4GroupViewDialog(group_code=parts[0], head_code=code)
                    d.exec_()

            if rec['type'] == "group":
                if code != self.group_code:
                    # Dialog only if its not this group
                    d = AGS4GroupViewDialog(group_code=self.group_code)
                    d.exec_()



    def on_splitter_bott_moved(self):
        G.settings.save_splitter(self.splitBott)

    def on_heading_selection_changed(self, head_code):
        self.sigHeadingSelected.emit(head_code)
        self.agsAbbrevsWidget.set_heading(head_code)

    def select_heading(self, head_code):
        self.agsHeadingsTable.select_heading(head_code)


    def clear(self):
        self.lblGroupCode.setText("")
        self.lblDescription.setText("")
        self.agsGroupNotesTable.clear()
        self.agsAbbrevsWidget.clear()

    def set_group(self, grp):

        ## load subwidgets, even if grp==None
        self.agsHeadingsTable.set_group(grp)
        self.agsGroupNotesWidget.set_group(grp)

        if grp == None:
            self.group_code = None
            self.lblGroupCode.setText("")
            self.lblDescription.setText("")
            return
        self.group_code = grp['group_code']
        self.lblGroupCode.setText(grp['group_code'])
        self.lblDescription.setText(grp['group_description'])



class AGS4GroupViewDialog(QtGui.QDialog):


    def __init__(self, parent=None, group_code=None, head_code=None):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle(group_code)
        self.setWindowIcon(Ico.icon(Ico.Ags4))

        self.setMinimumWidth(1100)
        self.setMinimumHeight(500)


        self.mainLayout = QtGui.QHBoxLayout()
        self.mainLayout.setSpacing(0)
        margarine = 0
        self.mainLayout.setContentsMargins(margarine, margarine, margarine, margarine)
        self.setLayout(self.mainLayout)



        self.groupViewWidget = AGS4GroupViewWidget(self)
        self.mainLayout.addWidget(self.groupViewWidget)

        grp = ags4.AGS4.group(group_code)
        self.groupViewWidget.set_group(grp)
        if head_code:
            self.groupViewWidget.select_heading(head_code)



class AGS4HeadingsTable( QtGui.QWidget ):

    sigHeadingSelected = pyqtSignal(object)

    def __init__( self, parent ):
        QtGui.QWidget.__init__( self, parent )

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

        self.model = HeadingsModel()
        self.tree.setModel(self.model)

        CH = HeadingsModel.CH
        self.tree.setColumnWidth(CH.strip, 3)
        self.tree.setColumnWidth(CH.head_code, 100)
        self.tree.setColumnWidth(CH.description, 250)
        self.tree.setColumnWidth(CH.unit, 50)
        self.tree.setColumnWidth(CH.status, 40)
        self.tree.setColumnWidth(CH.data_type, 50)
        self.tree.setColumnWidth(CH.sort_order, 20)
        self.tree.header().setStretchLastSection(True)

        self.tree.setSortingEnabled(False)

        self.tree.setContextMenuPolicy( Qt.CustomContextMenu )
        self.tree.customContextMenuRequested.connect(self.on_tree_context_menu )
        self.tree.selectionModel().selectionChanged.connect(self.on_tree_selected)

        self.popMenu = QtGui.QMenu()
        self.actOpenGroup = self.popMenu.addAction(Ico.icon(Ico.AgsGroup), "CODEEEEE", self.on_act_open_group)

    def on_tree_context_menu(self, qPoint):
        idx = self.tree.indexAt(qPoint)

        rec = self.model.rec_from_midx(idx)
        gc = rec['head_code'].split("_")[0]
        self.actOpenGroup.setDisabled(gc == self.model.grpDD['group_code'])
        self.actOpenGroup.setText("Open: %s" % gc)
        self.popMenu.exec_(self.tree.mapToGlobal(qPoint))

    def on_act_open_group(self):
        selidx = self.tree.selectionModel().selectedIndexes()
        rec = self.model.rec_from_midx(selidx[0])
        hc = rec.get("head_code")
        gc = hc.split("_")[0]
        d = AGS4GroupViewDialog(self, group_code=gc, head_code=hc)
        d.exec_()


    def set_group(self, grp):
        self.model.set_group(grp)

    def on_tree_selected(self, sel, desel):

        if not self.tree.selectionModel().hasSelection():
             self.sigHeadingSelected.emit( None )
             return

        rec = self.model.rec_from_midx( sel.indexes()[0] )
        self.sigHeadingSelected.emit(rec)



    def deadon_tree_context_menu(self, point):

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


    def select_heading(self, head_code):

        midx = self.model.get_heading_index(head_code)
        if midx != None:
            self.tree.selectionModel().setCurrentIndex(midx,
                                                   QtGui.QItemSelectionModel.SelectCurrent|QtGui.QItemSelectionModel.Rows)



class CN:
    node = 0
    note_id = 1
    so = 2


class AGS4GroupNotesWidget( QtGui.QWidget ):

    sigWordClicked = pyqtSignal(str)

    def __init__( self, parent, mode=None ):
        QtGui.QWidget.__init__( self, parent )


        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        ##==============================
        scrollArea = QtGui.QScrollArea()
        scrollArea.setWidgetResizable(True)
        self.mainLayout.addWidget(scrollArea, 100)

        self.scrollWidget = QtGui.QWidget()
        scrollArea.setWidget(self.scrollWidget)

        self.scrollLayout = QtGui.QVBoxLayout()
        self.scrollLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollLayout.setSpacing(0)
        self.scrollWidget.setLayout(self.scrollLayout)



    def clear(self):
        """Removes all entries"""

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

    def set_group(self, grp):

        self.clear()
        if grp == None:
            return

        notes = grp.get("notes")
        if notes == None:
            return

        self.setUpdatesEnabled(False)
        lookup = ags4.AGS4.words

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
            sty = "background-color: #EEF1F8; padding: 2px; margin:0; border-bottom:1px solid #dddddd;"
            widget.setStyleSheet(sty)
            widget.setAlignment(QtCore.Qt.AlignTop)

            self.scrollLayout.addWidget(w, 0)
            #self.connect(widget, QtCore.SIGNAL("linkHovered(const QString)"), self.on_link_hover)
            widget.linkActivated.connect(self.on_link_activated)

        #if len(notes) < 4:
        self.scrollLayout.addStretch(10)
        self.setUpdatesEnabled(True)


    def on_link_activated(self, lnkq):

        lnk = str(lnkq)
        parts = lnk[1:].split("-", 1 )
        print "act", lnk, parts, type(parts[1])
        self.sigWordClicked.emit( parts[1] )



class AGS4AbbrevsWidget( QtGui.QWidget ):
    """Shows pickist and accrevs etc"""

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )


        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        self.toolbar = xwidgets.hlayout()
        self.mainLayout.addLayout(self.toolbar, 0)

        self.icoLabel = xwidgets.IconLabel(self, ico=Ico.AgsGroup)
        self.icoLabel.setStyleSheet("background-color: white; color: #444444;")
        self.toolbar.addWidget(self.icoLabel, 0)

        self.lblAbbrCode = QtGui.QLabel(" ")
        self.lblAbbrCode.setStyleSheet("background-color: white; color: %s; font-weight: bold; font-family: monospace; padding: 3px;" % AGS4_COLORS.group)
        self.toolbar.addWidget(self.lblAbbrCode, 20)


        ##=== Tree
        self.tree = QtGui.QTreeView()
        self.mainLayout.addWidget(self.tree)
        self.tree.setUniformRowHeights(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(False)

        self.model = AbbrevItemsModel()
        self.tree.setModel(self.model)

        CA = AbbrevItemsModel.CA
        self.tree.setColumnWidth(CA.code, 100)
        self.tree.setColumnWidth(CA.description, 50)

        self.tree.header().setStretchLastSection(True)

        # TODO fix sort to ags
        self.tree.setSortingEnabled(True)

        self.set_heading(None)


    def set_heading(self, heading):
        self.model.set_heading(heading)



class PickListComboDelegate(QtGui.QItemDelegate):
    """A combobox for a table that whos the abrreviations picklist"""
    def __init__(self, parent, heading):
        QtGui.QItemDelegate.__init__(self, parent)

        self.ogtHeading = heading

    def createEditor(self, parent, option, index):

        editor = QtGui.QComboBox(parent)
        editor.addItem("--unknown--", "")

        # populate combobox from abbreviations
        for typ in ags4.AGS4.picklist(self.ogtHeading.head_code):
            editor.addItem( "%s: %s " % (typ['code'], typ['description']), typ['code'])

        return editor

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        curr = index.model().data(index).toString()
        idx = editor.findData(curr)
        if idx != -1:
            editor.setCurrentIndex(idx)
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        txt = editor.itemData(editor.currentIndex()).toString()
        model.setData(index, txt)

class NumberEditDelegate(QtGui.QItemDelegate):
    """Number editor to n decimal places"""
    def __init__(self, parent, heading):
        QtGui.QItemDelegate.__init__(self, parent)

        self.ogtHeading = heading

        ##self.data_type = heading['type']
        #self.data_type = heading['type']
        self.dp = None
        if self.ogtHeading.type.endswith("DP"):
            self.dp = int(self.ogtHeading.type[:-2])

    def createEditor(self, parent, option, index):

        editor = QtGui.QLineEdit(parent)
        if self.ogtHeading.type.endswith("DP"):
            validator = QtGui.QDoubleValidator()
            validator.setDecimals(self.dp)
            editor.setValidator(validator)

        return editor

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        curr = index.model().data(index) #.toString()
        editor.setText(curr)
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        no = float(editor.text())
        f = "%01."
        f += "%sf" % self.dp
        #print f
        txt = f % (no,)
        model.setData(index, txt)

class IDComboDelegate(QtGui.QItemDelegate):
    """A combobox for the ID"""
    def __init__(self, parent, heading, options):
        QtGui.QItemDelegate.__init__(self, parent)

        self.ogtHeading = heading
        self.options = options

    def createEditor(self, parent, option, index):

        editor = QtGui.QComboBox(parent)
        editor.addItem("--unknown--", "")

        # populate combobox from abbreviations
        for v in self.options:
            editor.addItem( "%s" % v, "%s" % v)

        return editor

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        curr = index.model().data(index).toString()
        idx = editor.findData(curr)
        if idx != -1:
            editor.setCurrentIndex(idx)
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        txt = editor.itemData(editor.currentIndex()).toString()
        model.setData(index, txt)

class AGS4UnitsTypesWidget( QtGui.QWidget ):
    """The Units and Types tab"""

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False
        self.setObjectName("AGS4UnitTypesWidget")


        self.proxyUnits = QtGui.QSortFilterProxyModel()
        self.proxyUnits.setSourceModel(G.ags.modelUnits)
        self.proxyUnits.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.proxyTypes = QtGui.QSortFilterProxyModel()
        self.proxyTypes.setSourceModel(G.ags.modelTypes)
        self.proxyTypes.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        ##===============================================
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        self.splitter = QtGui.QSplitter()
        self.mainLayout.addWidget(self.splitter)

        self.treeUnits = self.make_tree(self.proxyUnits, "Unit", "Description")
        self.splitter.addWidget(self.treeUnits)

        self.treeTypes = self.make_tree(self.proxyTypes, "Type", "Description")
        self.splitter.addWidget(self.treeTypes)


    def make_tree(self, model, tit1, tit2):
        tree = QtGui.QTreeView()
        tree.setRootIsDecorated(False)
        tree.setSortingEnabled(True)
        tree.setModel(model)
        return tree
        hi = tree.headerItem()
        hi.setText(0, tit1)
        hi.setText(1, tit2)
        return tree
