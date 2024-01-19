from __future__ import annotations

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QMenu, QWidget
from PyQt6.QtGui import QAction, QIcon


class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, figure: Figure = None, widgetParent=None, contextConnect: bool = True):
        super(FigureCanvasQTAgg, self).__init__(figure)
        self.widgetParent = widgetParent
        self.contextConnect = contextConnect

    def contextMenuEvent(self, event):
        if not self.contextConnect:
            return
        menu = QMenu()

        actionDelete = menu.addMenu(QIcon(".\\src\\img\\delete-component.svg"), 'Remove Graph')
        try:
            axis = self.figure.get_axes()[0]
            graphs = list(zip(axis.get_lines(), axis.get_legend().get_lines()))
            graphDict = {graph[1].get_label(): graph for graph in graphs}
            actionDelete.addActions([QAction(name, actionDelete) for name in graphDict.keys()])
        except IndexError:
            return

        res = menu.exec(event.globalPos())
        if res is not None:
            graphLine = graphDict[res.text()][0]
            graphLine.remove()

            # graphDict[res.text()][1].remove()
            self.widgetParent.plottedSpectra.remove((graphDict[res.text()][0].get_gid(), 'ToF' in res.text()))

            for anno in self.widgetParent.spectraData[res.text()].annotations:
                anno.remove()
            self.widgetParent.elementDataNames.clear()
            self.widgetParent.spectraData.pop(res.text())
            for row in self.widgetParent.titleRows:
                self.widgetParent.table.setItemDelegateForRow(row, None)
            self.widgetParent.updateLegend()
            axis.figure.canvas.draw()
            self.widgetParent.addTableData()
            if len(self.widgetParent.plottedSpectra) == 0:
                self.widgetParent.clear()
                return
