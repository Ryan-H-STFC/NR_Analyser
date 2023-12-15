from __future__ import annotations
from pyparsing import Literal


class BlittedCursor:
    """
    A cross-hair cursor using blitting for faster redraw.
    """

    def __init__(self, ax, axisType: Literal["x", "y", "both"] = "x", which: Literal['first', 'second'] = 'first'):
        self.ax = ax
        self.background = None
        self.axisType = axisType
        if self.axisType in ['y', 'both']:
            self.horizontal_line = ax.axhline(color='#AAA', lw=0.8, ls='--', gid='cursor_hline')
        if self.axisType in ['x', 'both']:
            self.vertical_line = ax.axvline(color='#AAA', lw=0.8, ls='--', gid='cursor_vline')
        # text location in axes coordinates
        self.text = ax.text(0.72, 0.9, '', transform=ax.transAxes, gid='cursor_text')
        self._creating_background = False
        self.drawEvent = ax.figure.canvas.mpl_connect('draw_event', self.on_draw)
        self.x = 0
        self.y = 0
        self.which = which

    def on_draw(self, event):
        self.create_new_background()

    def set_cross_hair_visible(self, visible):
        try:
            lineVisible = self.horizontal_line.get_visible()
        except AttributeError:
            lineVisible = self.vertical_line.get_visible()
        need_redraw = lineVisible != visible
        if self.axisType in ['y', 'both']:
            self.horizontal_line.set_visible(visible)
        if self.axisType in ['x', 'both']:
            self.vertical_line.set_visible(visible)
        self.text.set_visible(visible)
        return need_redraw

    def create_new_background(self):
        if self._creating_background:
            # discard calls triggered from within this function
            return
        self._creating_background = True
        self.set_cross_hair_visible(False)
        self.ax.figure.canvas.draw()
        self.background = self.ax.figure.canvas.copy_from_bbox(self.ax.bbox)
        self.set_cross_hair_visible(True)
        self._creating_background = False

    def on_mouse_move(self, event, maxima=None):
        if self.background is None:
            self.create_new_background()
        if not event.inaxes:
            need_redraw = self.set_cross_hair_visible(False)
            if need_redraw:
                self.ax.figure.canvas.restore_region(self.background)
                self.ax.figure.canvas.blit(self.ax.bbox)
        else:
            self.set_cross_hair_visible(True)
            self.valid = self.x < maxima if self.which == 'first' else self.x > maxima
            # update the line positions
            self.x, self.y = event.xdata, event.ydata
            if self.axisType in ['y', 'both']:
                self.horizontal_line.set_ydata([self.y])
                if maxima is not None:
                    self.horizontal_line.set_color(
                        "#0F0") if self.valid else self.horizontal_line.set_color("#F00")
            if self.axisType in ['x', 'both']:
                self.vertical_line.set_xdata([self.x])
                if maxima is not None:
                    self.vertical_line.set_color(
                        "#0F0") if self.valid else self.vertical_line.set_color("#F00")

            self.text.set_text(f'x={self.x:1.2f}, y={self.y:1.2f}')

            self.ax.figure.canvas.restore_region(self.background)

            if self.axisType in ['y', 'both']:
                self.ax.draw_artist(self.horizontal_line)
            if self.axisType in ['x', 'both']:
                self.ax.draw_artist(self.vertical_line)

            self.ax.draw_artist(self.text)
            self.ax.figure.canvas.blit(self.ax.bbox)

    def on_remove(self):
        self.set_cross_hair_visible(False)
        for artist in zip(self.ax.get_lines(), self.ax.texts):
            if 'cursor' in artist.get_gid():
                artist.remove()
        self.ax.figure.canvas.draw()
        self.ax.figure.canvas.mpl_disconnect(self.drawEvent)
        self.ax.figure.canvas.flush_events()
