# Imports
# ------------------------------------------------------------------------------
import sys
from PyQt4 import QtGui, QtCore, QtSvg


class TreeNodeItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent, name=""):
        super(TreeNodeItem, self).__init__(parent)
        self.setText(0, name)
        self.stuff = "Custom Names - " + str(name)


class TreeWidget(QtGui.QTreeWidget):
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setItemsExpandable(True)
        self.setAnimated(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)

        self.setAlternatingRowColors(True)

    # def rowsAboutToBeRemoved(self, *args, **kwargs):
    #     print('aaaaaaaa == ', args, kwargs)
    #
    #     model_index = args[0]
    #
    #     print('SS', self.model().data(model_index), model_index)
    #
    #
    #     super(TreeWidget, self).rowsAboutToBeRemoved(*args, **kwargs)

    def dragEnterEvent(self, e):

        print('asda', self.sender(), e.mimeData().hasText(), e.mimeData().formats(), e.mimeData().isWidgetType())
        print('aaa', e.mimeData().objectName(), e.mimeData().metaObject(), e.mimeData().parent(), e.mimeData().sender())
        print('vv', e.pos())
        for i in e.mimeData().formats():
            print(i)
        # QtCore.QMimeData.metaObject()
        if e.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            data = e.mimeData().data('application/x-qabstractitemmodeldatalist')
            print(str(data), type(data))
            print(data)
            # data = e.mimeData().retrieveData('application/x-qabstractitemmodeldatalist')
            # print(str(data), type(data))
            # print(data)
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        print(e.mimeData().text())

        #
        # print('aaaa', event, event.type(), QtCore.QEvent.Drop)
        # for item in self.selectedItems():
        #     print('source: ', str(item.text(0)))
        #
        # if str(item.text(0)) == '3':
        #     print('item 3 can not be moved')
        #
        # else:
        #     return_val = super( TreeWidget, self ).dropEvent( event )
        #     print ("Drop finished")
        #     d = event.mimeData()
        #     print d, event.source()
        #     print('return_val', return_val)
        #     return return_val

        # def dragLeaveEvent(self, *args, **kwargs):
        #     print('sss', args)
        #     print('kwargs', kwargs)
        #     super( TreeWidget, self ).dragLeaveEvent(  *args, **kwargs )

        #
        # def dropEvent(self, event):
        #     return_val = super( TreeWidget, self ).dropEvent( event )
        #     print ("Drop finished")
        #     d = event.mimeData()
        #     print d, event.source()
        #     return return_val
        #
        #
        #
        # def dropEvent(self, event):
        #     return_val = super( TreeWidget, self ).dropEvent( event )
        #     print ("Drop finished")
        #     d = event.mimeData()
        #     print d, event.source()
        #     return return_val
        #
        #
        # def dropEvent(self, event):
        #     return_val = super( TreeWidget, self ).dropEvent( event )
        #     print ("Drop finished")
        #     d = event.mimeData()
        #     print d, event.source()
        #     return return_val


# Main
# ------------------------------------------------------------------------------
class ExampleWidget(QtGui.QWidget):
    def __init__(self, ):
        super(ExampleWidget, self).__init__()

        self.initUI()
        print('=========================================================')

    def initUI(self):

        # formatting
        self.resize(250, 400)
        self.setWindowTitle("Example")

        # widget - passes treewidget
        # self.itemList = QtGui.QTreeWidget()
        # self.itemList.setDragEnabled(True)
        # self.itemList.setDropIndicatorShown(True)
        # self.itemList.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        # self.itemList.setAlternatingRowColors(True)

        self.itemList = TreeWidget()

        # self.itemList.model().rowsAboutToBeInserted.connect(self.insert)
        # self.itemList.model().rowsAboutToBeRemoved.connect(self.remove)
        #

        headers = ["Items"]
        self.itemList.setColumnCount(len(headers))
        self.itemList.setHeaderLabels(headers)

        # layout Grid - row/column/verticalpan/horizontalspan
        self.mainLayout = QtGui.QGridLayout(self)
        self.mainLayout.setContentsMargins(5, 5, 5, 5)
        self.mainLayout.addWidget(self.itemList, 0, 0, 1, 1)
        # self.itemList.installEventFilter(self)

        # self.itemList.mouseReleaseEvent.connect(self.release)
        # display
        self.show()

    # def insert(self, *args, **kwargs):
    #
    #     if isinstance(self.sender(), QtCore.QAbstractItemModel):
    #         model = self.sender()
    #         index, start_row, end_row = args
    #
    #         # should only be one row
    #         assert start_row == end_row
    #         target = index.row()
    #         level = index.row()
    #         # model(index)
    #         # QtCore.QAbstractItemModel.
    #         # print('insert', level, '->', target)
    #
    # def remove(self, *args, **kwargs):
    #     model = self.sender()
    #     index, start_row, end_row = args
    #     print('------')
    #     # should only be one row
    #     assert start_row == end_row
    #     source = start_row
    #     level = index.row()
    #     print('remove', source, '->', 'level', level)
    #
    #     model.revert()

    def release(self):
        print('DROPPED')

    def eventFilter(self, object, event):
        """
        to stop the event from being excuted return true
        Args:
            object:
            event:

        Returns:

        """
        if (object is self.itemList):
            tree = self.itemList

            if (event.type() == QtCore.QEvent.ChildRemoved):
                print('XZXX=== ChildRemoved', tree.selectedItems()[0].text(0))
            if (event.type() == QtCore.QEvent.ChildAdded):
                print('-------------------------------------')
                print('XZXX=== ChildAdded', tree.selectedItems()[0].text(0))
        else:
            print(object)
        return False

    # Functions
    # --------------------------------------------------------------------------   
    def closeEvent(self, event):
        print "closed"

    def showEvent(self, event):
        print "open"

        names = ['a', 'b', 'c', 'd', 'e']
        for i in xrange(5):
            TreeNodeItem(parent=self.itemList, name=names[i])


# Main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ex = ExampleWidget()
    sys.exit(app.exec_())
