from PyQt5.QtWidgets import QListView


class CustomListView(QListView):
    def mousePressEvent(self, e):
        super().mousePressEvent(e)

        index = self.indexAt(e.pos())

        if not index.isValid():
            self.clearSelection()
