import sys, os
from PySide.QtCore import *
from PySide.QtGui import *

class TreeTest(QTreeWidget):

    def __init__(self, parent = None):
        super(TreeTest, self).__init__(parent)
        self.setColumnCount(1)
        self.setHeaderLabel("Folders")

        # actionEdit = QAction("New Folder", self)
        # actionEdit.triggered.connect(self.addItemAction)
        # self.setContextMenuPolicy(Qt.ActionsContextMenu)
        # self.addAction(actionEdit)
        #
        # actionDelete = QAction("Delete", self)
        # actionDelete.triggered.connect(self.deleteItem)
        # self.addAction(actionDelete)

        self.style()

    def addItem(self, name, parent):
        self.expandItem(parent)
        item = QTreeWidgetItem(parent)
        item.setText(0, name)
        #It is important to set the Flag Qt.ItemIsEditable
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)

        # item.setIcon(0,self.style().standardIcon(QStyle.SP_DirIcon))
        return item
    #
    # def addItemAction(self):
    #     parent = self.currentItem()
    #     if parent is None:
    #         parent = self.invisibleRootItem()
    #     new_item = self.addItem("New Folder", parent)
    #     self.editItem(new_item)
    #
    # def deleteItem(self):
    #     root = self.invisibleRootItem()
    #     for item in self.selectedItems():
    #         (item.parent() or root).removeChild(item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    test = QWidget()
    treeWidget = TreeTest()
    layout = QHBoxLayout()
    layout.addWidget(treeWidget)

    test.setLayout(layout)
    test.show()

    treeWidget.addItem("top", treeWidget.invisibleRootItem())
    item = treeWidget.addItem("item", treeWidget.invisibleRootItem())
    treeWidget.addItem("subitem", item)

    app.exec_()