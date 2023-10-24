from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtGui import QIcon


class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, figure: Figure = None, parent=None):
        super(FigureCanvasQTAgg, self).__init__(figure)
        self.parent = parent

    def contextMenuEvent(self, event):

        menu = QMenu()

        actionDelete = menu.addMenu(QIcon(".\\src\\img\\delete-component.svg"), 'Remove Graph')
        try:
            axis = self.figure.get_axes()[0]
            graphs = list(zip(axis.get_lines(), axis.get_legend().get_lines()))
            graphDict = {graph[1].get_label(): graph for graph in graphs}
            actionDelete.addActions([QAction(name, actionDelete) for name in graphDict.keys()])
        except IndexError:
            return

        res = menu.exec_(event.globalPos())
        if res is not None:
            graphLine = graphDict[res.text()][0]
            graphLine.remove()

            # graphDict[res.text()][1].remove()
            self.parent.plottedSubstances.remove((graphDict[res.text()][0].get_gid(), 'ToF' in res.text()))

            for anno in self.parent.elementData[res.text()].annotations:
                anno.remove()
            self.parent.elementDataNames.clear()
            self.parent.elementData.pop(res.text())
            for row in self.parent.titleRows:
                self.parent.table.setItemDelegateForRow(row, None)
            self.parent.updateLegend()
            self.parent.addTableData()
