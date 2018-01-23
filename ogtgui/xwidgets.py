# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""



from Qt import Qt, QtCore, QtGui,  pyqtSignal

from img import Ico

DEFAULT_SPACING = 0
DEFAULT_MARGIN = 0
DEFAULT_BUTTON_WIDTH = 80

#=====================================================
# Layouts

def hlayout(spacing=DEFAULT_SPACING, margin=DEFAULT_MARGIN):
    """Convenience function to create a QHBoxLayout"""
    lay = QtGui.QHBoxLayout()
    if isinstance(margin, bool):
        margin = DEFAULT_SPACING
    if isinstance(spacing, bool):
        spacing = DEFAULT_SPACING
    lay.setContentsMargins(margin, margin, margin, margin)
    lay.setSpacing(spacing)
    return lay

def vlayout(spacing=DEFAULT_SPACING, margin=DEFAULT_MARGIN):
    """Convenience function to create a QVBoxLayout"""
    lay = QtGui.QVBoxLayout()
    if isinstance(margin, bool):
        margin = DEFAULT_SPACING
    if isinstance(spacing, bool):
        spacing = DEFAULT_SPACING
    lay.setContentsMargins(margin, margin, margin, margin)
    lay.setSpacing(spacing)
    return lay


def label(txt, align=Qt.AlignLeft, bold=False, style=None):
    """Convenience function to create a QLabel"""
    lbl = QtGui.QLabel()
    lbl.setText(txt)
    lbl.setAlignment(align)
    if bold:
        f = lbl.font()
        f.setBold(True)
        lbl.setFont(f)
    if style:
        lbl.setStyleSheet(style)
    return lbl


class XTableWidgetItem(QtGui.QTableWidgetItem):
    """Extended QTableWidgetItem with convenience functions"""
    def __init__(self):
        QtGui.QTableWidgetItem.__init__(self)



    def set(self, text=None, bold=False, bg=None, fg=None, align=None, check=None):

        if text:
            self.setText(text)

        if bold:
            self.set_bold(True)

        if bg:
            self.set_bg(bg)
        if fg:
            self.set_bg(fg)

        if align:
            self.setTextAlignment(align)

        if check != None:
            self.setCheckState(check)


    def set_bold(self, state):
        f = self.font()
        f.setBold(state)
        self.setFont(f)

    def set_bg(self, bg_color):
        colo = QtGui.QColor()
        colo.setNamedColor(bg_color)
        self.setBackgroundColor(colo)

    def set_fg(self, bg_color):
        colo = QtGui.QColor()
        colo.setNamedColor(bg_color)
        self.setForeground(colo)


class GroupHBox(QtGui.QGroupBox):


    def __init__(self, parent=None):
        QtGui.QGroupBox.__init__(self, parent)


        self.layout = QtGui.QHBoxLayout()
        self.setLayout(self.layout)

    def setContentsMargins(self, a,b,c,d):
        self.layout.setContentsMargins(a,b,c,d)

    def addWidget(self, widget, stretch=0):
        self.layout.addWidget(widget, stretch)

    def addLayout(self, widget, stretch=0):
        self.layout.addLayout(widget, stretch)

    def addStretch(self, stretch):
        self.layout.addStretch(stretch)



class GroupVBox(QtGui.QGroupBox):


    def __init__(self, parent=None, bold=False):
        QtGui.QGroupBox.__init__(self, parent)

        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

    def setContentsMargins(self, a,b,c,d):
        self.layout.setContentsMargins(a,b,c,d)

    def addLabel(self, txt):
        lbl = QtGui.QLabel()
        lbl.setText(txt)
        lbl.setStyleSheet("font-family: monospace; font-size: 8pt; color: #666666; background-color: #efefef; padding: 3px;")
        self.layout.addWidget(lbl)


    def addWidget(self, widget, stretch=0):
        self.layout.addWidget(widget, stretch)

    def addLayout(self, widget, stretch=0):
        self.layout.addLayout(widget, stretch)

    def addSpacing(self, s):
        self.layout.addSpacing( s)

    def addStretch(self, stretch):
        self.layout.addStretch(stretch)


    def setSpacing(self, x):
        self.layout.setSpacing(x)

class GroupGridBox(QtGui.QGroupBox):


    def __init__(self, parent=None):
        QtGui.QGroupBox.__init__(self, parent)


        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)



class StandardItem( QtGui.QStandardItem ):

    def __init__( self):
        QtGui.QStandardItem.__init__( self )
        #super(QtGui.QStandardItem, self).__init__()

        self.setEditable(False)

    def set_bg(self, color):
        self.setBackground(  G.colors.to_object( color ) )

    def set_fg(self, color):
        self.setForeground(  G.colors.to_object( color ) )

    def set_bold( self, bold):
        font = self.font()
        font.setBold( bold )
        self.setFont( font )

    def set_font_size( self, size):
        font = self.font()
        font.setPointSize(size)
        self.setFont( font )

    def setIco(self, ico):
        self.setIcon(Ico.icon(ico))

    def setText(self, txt, align=None, ico=None, icon=None, bold=False):
        self.set(txt, align=align, ico=ico, icon=icon, bold=bold)

    def set(self, txt, align=None, ico=None, icon=None, bold=False, font=None, bg=None):

        QtGui.QStandardItem.setText(self, str(txt))
        if align:
            self.setTextAlignment( align)
        if ico:
            self.setIco(ico)
        if icon:
            self.setIcon(icon)

        self.set_bold(bold)

        if font:
            self.set_font_family(font)
        if bg:
            self.set_bg(bg)

    def set_font_family( self, fam):
        font = self.font( )
        font.setFamily( fam )
        self.setFont( font )

    def s(self):
        return str(self.text())

    def i(self):
        x, ok = self.text().toInt()
        if not ok:
            return None
        return x


    def b(self):
        return  str(self.text()) == "1"

    def ds(self):
        return str(self.data().toString())

    def lbl_checked(self,  val, bg_color=None ):
        self.setTextAlignment( QtCore.Qt.AlignCenter)
        if bg_color == None:
            bg_color = "#FFECAA"
        if bool(val):
            self.setText( "Yes")
            self.setData("1")
            self.set_bg( bg_color )
        else:
            self.setText( "-")
            self.setData("")
            self.set_bg( "#efefef")

class ClearButton( QtGui.QToolButton ):
    def __init__( self, parent, callback=None ):
        QtGui.QToolButton.__init__( self )
        self.setIcon( Ico.icon( Ico.Clear ) )
        self.setToolTip("Clear")
        self.setToolButtonStyle( QtCore.Qt.ToolButtonIconOnly )
        self.setAutoRaise(True)
        self.setFixedWidth(16)

        if callback:
            self.connect(self, QtCore.SIGNAL("clicked()"), callback)

class IconLabel(QtGui.QLabel):

    def __init__( self, parent=None, ico=None):
        QtGui.QLabel.__init__( self, parent)

        self.setContentsMargins(5,0,0,0)
        #img_file_path = G.settings.image_path( "/missc/arrow_left_down.gif" )
        icon = Ico.icon(ico)
        self.setPixmap( icon.pixmap(QtCore.QSize( 16, 16 )) )
        self.setFixedWidth(20)




class LNTextEdit(QtGui.QFrame):
    """Text widget with support for line numbers
    https://nachtimwald.com/2009/08/19/better-qplaintextedit-with-line-numbers/
    """
    class NumberBar(QtGui.QWidget):

        def __init__(self, edit):
            QtGui.QWidget.__init__(self, edit)

            self.edit = edit
            self.adjustWidth(1)

        def paintEvent(self, event):
            self.edit.numberbarPaint(self, event)
            QtGui.QWidget.paintEvent(self, event)

        def adjustWidth(self, count):
            width = self.fontMetrics().width(unicode(count))
            if self.width() != width:
                self.setFixedWidth(width)

        def updateContents(self, rect, scroll):
            if scroll:
                self.scroll(0, scroll)
            else:
                # It would be nice to do
                # self.update(0, rect.y(), self.width(), rect.height())
                # But we can't because it will not remove the bold on the
                # current line if word wrap is enabled and a new block is
                # selected.
                self.update()

    class PlainTextEdit(QtGui.QPlainTextEdit):

        def __init__(self, *args):
            QtGui.QPlainTextEdit.__init__(self, *args)

            # self.setFrameStyle(QFrame.NoFrame)

            self.setFrameStyle(QtGui.QFrame.NoFrame)
            self.highlight()
            # self.setLineWrapMode(QPlainTextEdit.NoWrap)
            self.setWordWrapMode(QtGui.QTextOption.NoWrap)
            self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
            self.setStyleSheet("font-family: monospace")

            self.cursorPositionChanged.connect(self.highlight)

        def highlight(self):
            hi_selection = QtGui.QTextEdit.ExtraSelection()

            hi_selection.format.setBackground(self.palette().alternateBase())
            hi_selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, QtCore.QVariant(True))
            hi_selection.cursor = self.textCursor()
            hi_selection.cursor.clearSelection()

            self.setExtraSelections([hi_selection])

        def numberbarPaint(self, number_bar, event):
            font_metrics = self.fontMetrics()
            current_line = self.document().findBlock(self.textCursor().position()).blockNumber() + 1

            block = self.firstVisibleBlock()
            line_count = block.blockNumber()
            painter = QtGui.QPainter(number_bar)
            painter.fillRect(event.rect(), self.palette().base())

            # Iterate over all visible text blocks in the document.
            while block.isValid():
                line_count += 1
                block_top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()

                # Check if the position of the block is out side of the visible
                # area.
                if not block.isVisible() or block_top >= event.rect().bottom():
                    break

                # We want the line number for the selected line to be bold.
                if line_count == current_line:
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
                else:
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)

                # Draw the line number right justified at the position of the line.
                paint_rect = QtCore.QRect(0, block_top, number_bar.width(), font_metrics.height())
                painter.drawText(paint_rect, Qt.AlignRight, unicode(line_count))

                block = block.next()

            painter.end()

    def __init__(self, *args):
        QtGui.QFrame.__init__(self, *args)

        self.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken)

        self.edit = self.PlainTextEdit()
        self.number_bar = self.NumberBar(self.edit)

        hbox = QtGui.QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setMargin(0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(self.edit)

        self.edit.blockCountChanged.connect(self.number_bar.adjustWidth)
        self.edit.updateRequest.connect(self.number_bar.updateContents)

    def getText(self):
        return unicode(self.edit.toPlainText())

    def setText(self, text):
        self.edit.setPlainText(text)

    def isModified(self):
        return self.edit.document().isModified()

    def setModified(self, modified):
        self.edit.document().setModified(modified)

    def setLineWrapMode(self, mode):
        self.edit.setLineWrapMode(mode)