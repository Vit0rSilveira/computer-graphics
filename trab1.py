#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qt + OpenGL polygon fill using Edge Table (ET) and Active Edge Table (AET)
-----------------------------------------------------------------------------
Requirements:
  - PyQt6
  - PyOpenGL

Install:
  pip install PyQt6 PyOpenGL

Run:
  python polygon_fill_et_aet.py

Usage:
  • Click on the canvas to add polygon vertices (in order).
  • Use "Close Polygon" to close the current polygon.
  • Choose Fill Color to change the fill.
  • Adjust Stroke Width to change outline thickness.
  • Click "Fill" to perform scanline fill (ET/AET).
  • "Clear" resets the canvas.
  • Menu → Examples for simple/complex test polygons.

Notes:
  • Works for simple (possibly concave) polygons. Self‑intersecting polygons are
    not guaranteed to be handled.
  • Filling is implemented by computing scanline spans and drawing them as GL_LINES.
  • Coordinate system: origin at top-left, y growing downward (orthographic).

Author: (fill with your group members)
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import List, Tuple, Optional

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QToolBar,
    QFileDialog, QColorDialog, QMessageBox, QLabel, QSpinBox, QComboBox
)
from PyQt6.QtGui import QColor, QAction

from PyQt6.QtOpenGLWidgets import QOpenGLWidget

# PyOpenGL
from OpenGL.GL import (
    glClearColor, glClear, GL_COLOR_BUFFER_BIT,
    glMatrixMode, GL_PROJECTION, GL_MODELVIEW, glLoadIdentity,
    glOrtho, glBegin, glEnd, glVertex2f, GL_LINES, GL_LINE_LOOP,
    glLineWidth, glColor4f, glEnable, GL_BLEND, glBlendFunc,
    GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_POINT_SMOOTH,
    GL_LINE_SMOOTH, glPointSize
)


@dataclass
class Edge:
    ymax: int
    x: float
    inv_slope: float


class GLCanvas(QOpenGLWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.points: List[QPointF] = []  # current polygon points
        self.closed: bool = False
        self.fill_color: QColor = QColor(0, 128, 255, 180)
        self.stroke_color: QColor = QColor(30, 30, 30)
        self.stroke_width: int = 2
        self.filled_spans: List[Tuple[int, float, float]] = []  # (y, x_left, x_right)
        self.hover_pos: Optional[QPointF] = None
        self.bg_color = QColor(245, 246, 248)
        self.show_vertices: bool = True
        self.snap_preview: bool = True

    # ---------- OpenGL lifecycle ----------
    def initializeGL(self):
        glClearColor(self.bg_color.redF(), self.bg_color.greenF(), self.bg_color.blueF(), 1.0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_LINE_SMOOTH)

    def resizeGL(self, w: int, h: int):
        # 2D orthographic projection: origin top-left
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # Draw filled spans (if available)
        if self.filled_spans:
            r, g, b, a = self.fill_color.redF(), self.fill_color.greenF(), self.fill_color.blueF(), self.fill_color.alphaF()
            glColor4f(r, g, b, a)
            glLineWidth(1)
            glBegin(GL_LINES)
            for y, x1, x2 in self.filled_spans:
                glVertex2f(x1, float(y) + 0.5)
                glVertex2f(x2, float(y) + 0.5)
            glEnd()

        # Draw polygon outline
        if len(self.points) >= 2:
            glColor4f(self.stroke_color.redF(), self.stroke_color.greenF(), self.stroke_color.blueF(), 1.0)
            glLineWidth(float(self.stroke_width))
            glBegin(GL_LINE_LOOP if self.closed else GL_LINES)
            if self.closed:
                for p in self.points:
                    glVertex2f(p.x(), p.y())
            else:
                # draw path as segments in input order
                for i in range(len(self.points) - 1):
                    p1, p2 = self.points[i], self.points[i + 1]
                    glVertex2f(p1.x(), p1.y())
                    glVertex2f(p2.x(), p2.y())
            glEnd()

        # Draw vertices and hover preview
        if self.show_vertices and self.points:
            glPointSize(6)
            glColor4f(0.1, 0.1, 0.1, 1.0)
            glBegin(GL_LINES)  # we will draw little crosses using lines for each vertex
            s = 4
            for p in self.points:
                x, y = p.x(), p.y()
                glVertex2f(x - s, y)
                glVertex2f(x + s, y)
                glVertex2f(x, y - s)
                glVertex2f(x, y + s)
            glEnd()

        if self.hover_pos and (not self.closed) and self.points:
            # Preview segment from last point to cursor
            glColor4f(0.15, 0.15, 0.15, 0.35)
            glLineWidth(1.0)
            glBegin(GL_LINES)
            last = self.points[-1]
            glVertex2f(last.x(), last.y())
            glVertex2f(self.hover_pos.x(), self.hover_pos.y())
            glEnd()

    # ---------- Interaction ----------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.closed:
            self.points.append(QPointF(event.position().x(), event.position().y()))
            self.filled_spans.clear()
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            # right-click toggles vertex display for clarity
            self.show_vertices = not self.show_vertices
            self.update()

    def mouseMoveEvent(self, event):
        self.hover_pos = QPointF(event.position().x(), event.position().y())
        self.update()

    # ---------- Public operations ----------
    def set_stroke_width(self, w: int):
        self.stroke_width = max(1, int(w))
        self.update()

    def set_fill_color(self, c: QColor):
        self.fill_color = c
        self.update()

    def clear(self):
        self.points.clear()
        self.closed = False
        self.filled_spans.clear()
        self.update()

    def close_polygon(self):
        if len(self.points) >= 3:
            self.closed = True
            self.filled_spans.clear()
            self.update()
        else:
            QMessageBox.information(self, "Info", "Adicione pelo menos 3 pontos antes de fechar o polígono.")

    def fill(self):
        if not self.closed:
            QMessageBox.information(self, "Info", "Feche o polígono antes de preencher.")
            return
        spans = self.compute_scanline_spans([(p.x(), p.y()) for p in self.points], int(self.height()))
        self.filled_spans = spans
        self.update()

    # ---------- ET / AET implementation ----------
    @staticmethod
    def build_edge_table(vertices: List[Tuple[float, float]], height: int) -> List[List[Edge]]:
        """
        Build Edge Table (ET) as a list of buckets per integer scanline y.
        Each bucket stores edges starting at that y (ymin).
        """
        n = len(vertices)
        ET: List[List[Edge]] = [[] for _ in range(height + 1)]

        # iterate over edges (v_i, v_{i+1})
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % n]

            # Ignore horizontal edges
            if int(round(y1)) == int(round(y2)):
                continue

            if y1 < y2:
                ymin, ymax = y1, y2
                x_at_ymin = x1
                dy = y2 - y1
                dx = x2 - x1
            else:
                ymin, ymax = y2, y1
                x_at_ymin = x2
                dy = y1 - y2
                dx = x1 - x2

            inv_slope = dx / dy  # 1/m

            # Ceiling of ymin as first scanline
            y_start = int(max(0, int(round(min(ymin, height)))))
            y_end = int(min(height, int(round(max(0, ymax) - 1))))  # ymax is exclusive

            # Compute x at the first scanline (y = y_start)
            # Adjust x to the precise intersection with the first integer scanline
            if dy != 0:
                # Move from ymin to y_start
                y_offset = (y_start + 0.0) - ymin
                x_int = x_at_ymin + inv_slope * y_offset
            else:
                x_int = x_at_ymin

            if 0 <= y_start <= height and y_start <= y_end:
                ET[y_start].append(Edge(ymax=y_end, x=x_int, inv_slope=inv_slope))

        return ET

    @staticmethod
    def compute_scanline_spans(vertices: List[Tuple[float, float]], height: int) -> List[Tuple[int, float, float]]:
        """Compute spans (x1, x2) for each integer scanline y using ET/AET."""
        ET = GLCanvas.build_edge_table(vertices, height)
        AET: List[Edge] = []
        spans: List[Tuple[int, float, float]] = []

        for y in range(0, height + 1):
            # Add edges starting at this scanline
            for e in ET[y]:
                AET.append(e)
            # Remove edges for which y > ymax
            AET = [e for e in AET if y <= e.ymax]

            # Sort AET by current x, then by inv_slope
            AET.sort(key=lambda e: (e.x, e.inv_slope))

            # Pair up intersections to generate spans
            it = iter(AET)
            pairs = []
            try:
                while True:
                    e1 = next(it)
                    e2 = next(it)
                    x_left = e1.x
                    x_right = e2.x
                    if x_left > x_right:
                        x_left, x_right = x_right, x_left
                    pairs.append((x_left, x_right))
            except StopIteration:
                pass

            for x_left, x_right in pairs:
                if x_right - x_left > 1e-6:
                    spans.append((y, x_left, x_right))

            # Increment x for each active edge
            for e in AET:
                e.x += e.inv_slope

        return spans

    # ---------- Example polygons ----------
    def load_example(self, name: str):
        w, h = self.width(), self.height()
        examples = {
            "Convex pentagon": [
                QPointF(0.25 * w, 0.2 * h), QPointF(0.75 * w, 0.25 * h),
                QPointF(0.8 * w, 0.65 * h), QPointF(0.5 * w, 0.85 * h),
                QPointF(0.2 * w, 0.6 * h)
            ],
            "Concave arrow": [
                QPointF(0.2 * w, 0.2 * h), QPointF(0.7 * w, 0.2 * h),
                QPointF(0.7 * w, 0.05 * h), QPointF(0.95 * w, 0.35 * h),
                QPointF(0.7 * w, 0.65 * h), QPointF(0.7 * w, 0.5 * h),
                QPointF(0.2 * w, 0.5 * h)
            ],
            "Complex concave": [
                QPointF(0.1 * w, 0.2 * h), QPointF(0.4 * w, 0.1 * h),
                QPointF(0.7 * w, 0.2 * h), QPointF(0.9 * w, 0.5 * h),
                QPointF(0.7 * w, 0.8 * h), QPointF(0.4 * w, 0.9 * h),
                QPointF(0.1 * w, 0.8 * h), QPointF(0.05 * w, 0.5 * h)
            ],
        }
        if name in examples:
            self.points = examples[name]
            self.closed = True
            self.filled_spans.clear()
            self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Polygon Fill (ET/AET) — Qt + OpenGL")
        self.resize(1000, 700)

        self.canvas = GLCanvas()
        self.setCentralWidget(self.canvas)

        self._make_toolbar()
        self._make_menubar()

    def _make_toolbar(self):
        tb = QToolBar("Tools")
        tb.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)

        # Close polygon
        act_close = QAction("Close Polygon", self)
        act_close.triggered.connect(self.canvas.close_polygon)
        tb.addAction(act_close)

        # Fill
        act_fill = QAction("Fill", self)
        act_fill.triggered.connect(self.canvas.fill)
        tb.addAction(act_fill)

        # Clear
        act_clear = QAction("Clear", self)
        act_clear.triggered.connect(self.canvas.clear)
        tb.addAction(act_clear)

        tb.addSeparator()

        # Fill color
        act_color = QAction("Fill Color", self)
        act_color.triggered.connect(self.pick_color)
        tb.addAction(act_color)

        # Stroke width spinner
        tb.addSeparator()
        tb.addWidget(QLabel("Stroke Width:"))
        spin = QSpinBox()
        spin.setRange(1, 20)
        spin.setValue(self.canvas.stroke_width)
        spin.valueChanged.connect(self.canvas.set_stroke_width)
        tb.addWidget(spin)

        # Example dropdown
        tb.addSeparator()
        tb.addWidget(QLabel("Examples:"))
        combo = QComboBox()
        combo.addItems(["(choose)", "Convex pentagon", "Concave arrow", "Complex concave"])
        combo.currentTextChanged.connect(self._on_example)
        tb.addWidget(combo)

    def _make_menubar(self):
        mb = self.menuBar()
        file_m = mb.addMenu("&File")
        act_exit = QAction("Exit", self)
        act_exit.triggered.connect(self.close)
        file_m.addAction(act_exit)

        ex_m = mb.addMenu("&Examples")
        for name in ["Convex pentagon", "Concave arrow", "Complex concave"]:
            act = QAction(name, self)
            act.triggered.connect(lambda checked=False, n=name: self.canvas.load_example(n))
            ex_m.addAction(act)

        help_m = mb.addMenu("&Help")
        act_about = QAction("About", self)
        act_about.triggered.connect(self._about)
        help_m.addAction(act_about)

    def _about(self):
        QMessageBox.information(self, "About", (
            "Polygon filling using Edge Table (ET) and Active Edge Table (AET)\n\n"
            "• Add vertices with left-click. Right-click toggles vertex markers.\n"
            "• Close the polygon, then Fill.\n"
            "• This implementation draws spans per scanline using GL_LINES.\n"
            "• Designed for simple/concave polygons (non self-intersecting)."
        ))

    def pick_color(self):
        c = QColorDialog.getColor(self.canvas.fill_color, self, "Choose Fill Color",
                                  QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if c.isValid():
            self.canvas.set_fill_color(c)

    def _on_example(self, text: str):
        if text and text != "(choose)":
            self.canvas.load_example(text)


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
