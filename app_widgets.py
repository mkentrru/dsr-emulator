
import typing

from PyQt5.QtCore import Qt, QRect, QEvent, pyqtSignal, \
    QPoint, QPointF, QLine, QTimer
import PyQt5.QtWidgets as qtw
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QPixmap, QPainter

import math
from numpy import random

from app_pens import *

from globals import g_field, g_signals


class DrawingField (qtw.QLabel): 

    pen_node = gen_pen_node ()
    pen_link = gen_pen_link ()
    pen_default = gen_pen_default ()
    font_id = gen_font_id ()
    pen_radius = gen_pen_radius ()
    pen_broadcast = gen_pen_broadcast ()
    pen_RREQ = gen_pen_RREQ ()
    pen_RREP = gen_pen_RREP ()
    pen_notice = gen_pen_notice ()
    route_pen = gen_route_pen ()
    pen_requested_route = gen_pen_requested_route ()

    sig_show_pkts = pyqtSignal (int)

    def __init__ (self):
        super ().__init__ ()
        self.s = 1
        
        self.pos_nodes = dict ()
        self.requested_routes = list ()

        self.setMinimumSize (200, 200)
        
        self.canvas = QPixmap(200, 200)
        self.canvas.fill(Qt.white)
        self.setPixmap(self.canvas)
    
        g_signals.sig_after_field_regen.connect (self.regen_reset)
        g_signals.sig_field_static_changes.connect (self.redrawField)
        g_signals.sig_field_network_step.connect (self.redrawField)
        g_signals.sig_start_RREQ.connect (self.store_requests)

    def regen_reset (self):
        self.pos_nodes = dict ()
        self.requested_routes = list ()

    def store_requests (self, src, dst):
        self.requested_routes.append ((src, dst))

    def scale (self, v):
        return round (v * self.s)

    def paintEvent(self, a0) -> None:
        if g_field.is_ready ():
            self.redrawField ()
        return super().paintEvent(a0)

    def recalc_scales (self):

        self.fw, self.fh = g_field.get_sizes ()

        sx = (self.w - 100) / self.fw
        sy = (self.h - 100) / self.fh
        
        self.s = min (sx, sy)

    def do_resizing (self):
        self.w = self.width (); self.h = self.height ()
        self.canvas = self.canvas.scaled (self.w, self.h)
        self.setPixmap(self.canvas)
        if g_field.is_ready ():
            self.recalc_scales ()
            return True
        return False
            

    def resizeEvent(self, a0) -> None:
        if self.do_resizing ():
            self.redrawField ()
        return super().resizeEvent(a0)


    def redrawField (self):

        
        self.canvas.fill(Qt.white)

        if not self.do_resizing (): return
        self.painter = QPainter (self.pixmap ())

        
        self.center_offset_x = round (self.w / 2)
        self.center_offset_y = round (self.h / 2)
        
        self.calc_positions ()
        self.draw_requests ()
        self.draw_routes ()
        self.draw_nodes ()

        self.painter.end ()

    def calc_positions (self):
        self.pos_nodes = dict ()
        for n in g_field.nodes:
            nx = self.scale (n.x) + self.center_offset_x
            ny = self.scale (n.y) + self.center_offset_y
            self.pos_nodes [n.id] = (nx, ny)

    def draw_routes (self):
        if not g_field.is_ready (): return
        for n in g_field.nodes:
            if not len (n.routes): continue
            for r in n.routes.values ():
                if not len (r): continue
                if r [0] != n.id: as_dst = True
                else: as_dst = False

                for s in range (len (r) - 1):
                    s1 = r [s]; s2 = r [s + 1]
                    if as_dst:
                        offset = -5
                    else:
                        offset = 5

                    start = QPoint (self.pos_nodes [s1] [0], self.pos_nodes [s1] [1])
                    end = QPoint (self.pos_nodes [s2] [0], self.pos_nodes [s2] [1])
                    line = QLine (start, end)
                    arrowSize = 5

                    angle = math.atan2 (line.dy() / 2, line.dx() / 2)
                    dx = math.cos (angle + math.pi / 2) * offset
                    dy = math.sin (angle + math.pi / 2) * offset
                    pd = QPointF (dx, dy)
                    start = start + pd
                    end = end + pd

                    arrow_1 = end + QPointF (
                        math.sin(angle + math.pi / 3) * arrowSize,
                        math.cos(angle + math.pi / 3) * arrowSize
                    )
                    arrow_2 = end + QPointF (
                        math.sin(angle + math.pi - math.pi / 3) * arrowSize,
                        math.cos(angle + math.pi - math.pi / 3) * arrowSize
                    )
                    self.painter.setPen (self.route_pen)
                    self.painter.drawLine(start, end)
                    self.painter.drawLine(end, arrow_1)
                    self.painter.drawLine(end, arrow_2)


    def draw_requests (self):
        for r in self.requested_routes:
            src = r [0]; dst = r [1]
            self.painter.setPen (self.pen_requested_route)
            self.painter.drawLine (
                self.pos_nodes [src] [0], self.pos_nodes [src] [1],
                self.pos_nodes [dst] [0], self.pos_nodes [dst] [1],
            )
            
    def draw_nodes (self):

        

        links = g_field.get_links ()
        
        for n in g_field.nodes:
            nx = self.pos_nodes [n.id] [0]
            ny = self.pos_nodes [n.id] [1]

            if len (n.pkts_out): broadcastring = True
            else: broadcastring = False
            if broadcastring:
                
                if n.pkts_out [-1].type == "RREQ":
                    self.painter.setPen (self.pen_RREQ)
                elif n.pkts_out [-1].type == "RREP":
                    self.painter.setPen (self.pen_RREP)
                else: 
                    self.painter.setPen (self.pen_broadcast)
                
                self.painter.drawEllipse (nx - 10, ny - 10, 20, 20)

            else: self.painter.setPen (self.pen_radius)

            r = self.scale (g_field.r)
            self.painter.drawEllipse (nx - r, ny - r, r * 2, r * 2)
        
        for n in g_field.nodes:
            
            nx = self.pos_nodes [n.id] [0]
            ny = self.pos_nodes [n.id] [1]
            
            self.painter.setPen (self.pen_link)
            for b_id in links.pop (n.id):
                if b_id not in links.keys (): continue
                b = g_field.nodes [b_id]
                bx = self.scale (b.x) + self.center_offset_x
                by = self.scale (b.y) + self.center_offset_y
                self.painter.drawLine (nx, ny, bx, by)
            

            
            # if broadcastring: self.painter.setPen (self.pen_broadcast)
            # else: self.painter.setPen (self.pen_node)
            self.painter.setPen (self.pen_node)
            self.painter.drawEllipse (nx - 3, ny - 3, 6, 6)

            arc_rect = QRect (nx - 15, ny - 15, 30, 30)
            if len (n.pkts_in): 
                self.painter.setPen (self.pen_default)
                # self.painter.drawEllipse (nx - 10, ny - 10, 20, 20)
                self.painter.drawArc (arc_rect, 30 * 16, 120 * 16)
            # if len (n.pkts_out):
            #     self.painter.setPen (self.pen_default)
            #     self.painter.drawArc (arc_rect, 210 * 16, 120 * 16)

            if n.dropped:
                self.painter.setPen (self.pen_default)
                self.painter.drawLine (nx - 10, ny - 10, nx + 10, ny + 10)
                self.painter.drawLine (nx - 10, ny + 10, nx + 10, ny - 10)


            self.painter.setPen (self.pen_default)
            self.painter.setFont (self.font_id)
            self.painter.drawText (nx - 3, ny + 3, str (n.id))
    
    def handle_click (self, x, y, r=10):

        for a in self.pos_nodes:
            p = self.pos_nodes [a]
            x1 = p[0] - r; x2 = p[0] + r
            y1 = p[1] - r; y2 = p[1] + r
            if x1 < x < x2 and y1 < y < y2:
                self.sig_show_pkts.emit (a)
                
        
        

    def mousePressEvent(self, ev):
        pos = ev.pos ()
        self.handle_click (pos.x (), pos.y ())
        
        # super ().mousePressEvent (ev)

        

class Routes (qtw.QFrame):
    
    def __init__(self) -> None:
        super().__init__()
        self.lay = qtw.QVBoxLayout ()
        self.lay.setAlignment (Qt.AlignTop)
        
        self.scroll_area = qtw.QScrollArea ()
        # self.scroll_area.setWidget (self.holder)
        self.scroll_area.setLayout (self.lay)

        self.setLayout (qtw.QVBoxLayout ())
        self.layout ().addWidget (self.scroll_area)
        # self.layout ().addWidget (self.holder)

        self.layout ().setSpacing (5)
        self.layout ().setContentsMargins (10, 10, 10, 10)
        self.setStyleSheet (
            "#route_row"
            "{"
            "border-radius: 5px;"
            "background-color: #c0c0ff;"
            "}"
        )


    def GenRow (self):
        r = qtw.QFrame ()
        r.setObjectName ("route_row")
        r.setLayout (qtw.QVBoxLayout ())
        r.layout ().setSpacing (0)
        r.layout ().setContentsMargins (5, 5, 5, 5)
        l_id = qtw.QLabel ("id")
        l_id.setWordWrap (True)
        l_id.setSizePolicy (QSizePolicy.Expanding, QSizePolicy.Minimum)
        r.layout ().addWidget (l_id)
        l_route = qtw.QLabel ("route")
        l_route.setWordWrap (True)
        r.layout ().addWidget (l_route)
        return r

    def showRoutes (self):
        to_show = 0
        ids_with_route = [n.id for n in g_field.nodes if len (n.routes)]
        
        if g_field.is_ready ():
            to_show = len (ids_with_route)
        
        if self.lay.count () < to_show:
            for _ in range (to_show - self.lay.count ()):
                self.lay.addWidget (self.GenRow ())

        a = 0
        for a in range (to_show):
            w = self.lay.itemAt (a).widget ()
            id = ids_with_route [a]

            w.layout ().itemAt (0).widget ().setText (str (id))
            str_route = ""
            for dst in g_field.nodes [id].routes:
                str_route += f' -> {dst}: '
                str_route += f'{g_field.nodes [id].routes[dst]}<br>'
            w.layout ().itemAt (1).widget ().setText (str_route)

            w.show ()
        
        if to_show: a = a + 1
        for b in range (a, self.lay.count ()):
            self.lay.itemAt (b).widget ().hide ()

        
    


class ControlField (qtw.QFrame):
    def __init__(self) -> None:
        super().__init__()

        self.running_auto = False
        self.auto_timer = QTimer ()

        
        self.setLayout (qtw.QVBoxLayout ())

        holder_Regen = qtw.QFrame ()
        holder_Regen.setLayout (qtw.QHBoxLayout ())
        self.spin_NodesCount = qtw.QSpinBox ()
        self.spin_NodesCount.setMinimum (2)
        self.spin_NodesCount.setMaximum (50)
        self.spin_NodesCount.setValue (20)
        self.btn_Reget = qtw.QPushButton ("regen")
        holder_Regen.layout ().addWidget (qtw.QLabel ("nodes count"))
        holder_Regen.layout ().addWidget (self.spin_NodesCount)
        holder_Regen.layout ().addWidget (self.btn_Reget)

        holder_ReqBuilder = qtw.QFrame ()
        holder_ReqBuilder.setLayout (qtw.QHBoxLayout ())
        self.spin_ReqSrc = qtw.QSpinBox ()
        self.spin_ReqSrc.setEnabled (False)
        self.spin_ReqSrc.setMinimum (0)
        self.spin_ReqDst = qtw.QSpinBox ()
        self.spin_ReqDst.setEnabled (False)
        self.spin_ReqDst.setMinimum (0)
        self.btn_ReqSend = qtw.QPushButton ("RREQ")
        self.btn_ReqSend.clicked.connect (self.slot_ask_to_RREQ)
        self.btn_ReqSend.setEnabled (False)
        self.btn_Rnd = qtw.QPushButton ("rnd")
        self.btn_Rnd.setEnabled (False)
        self.btn_Rnd.clicked.connect (self.slot_do_rnd_addresses)
        holder_ReqBuilder.layout ().addWidget (self.spin_ReqSrc)
        holder_ReqBuilder.layout ().addWidget (self.spin_ReqDst)
        holder_ReqBuilder.layout ().addWidget (self.btn_ReqSend)
        holder_ReqBuilder.layout ().addWidget (self.btn_Rnd)
        self.spin_ReqSrc.valueChanged.connect (self.slot_check_RREQ_addresses)
        self.spin_ReqDst.valueChanged.connect (self.slot_check_RREQ_addresses)

        
        holder_NetworkStep = qtw.QFrame ()
        holder_NetworkStep.setLayout (qtw.QHBoxLayout ())
        l_network_step = qtw.QLabel ("network step")
        l_network_step.setAlignment (Qt.AlignCenter)

        self.btn_network_step = qtw.QPushButton (">>>")
        self.spin_AutoDelay = qtw.QSpinBox ()
        self.spin_AutoDelay.setMinimum (100)
        self.spin_AutoDelay.setMaximum (5000)
        self.spin_AutoDelay.setValue (1000)
        self.btn_Auto = qtw.QPushButton ("play")
        self.btn_Auto.clicked.connect (self.slot_handle_auto)
        holder_NetworkStep.layout ().addWidget (l_network_step)
        holder_NetworkStep.layout ().addWidget (self.btn_network_step)
        holder_NetworkStep.layout ().addWidget (self.spin_AutoDelay)
        holder_NetworkStep.layout ().addWidget (self.btn_Auto)


        self.w_routes = Routes ()
        self.layout ().addWidget (self.w_routes)

        l_regen_network = qtw.QLabel ("regen network")
        l_regen_network.setAlignment (Qt.AlignCenter)

        self.layout ().addWidget (l_regen_network)
        self.layout ().addWidget (holder_Regen)
        self.layout ().addWidget (holder_ReqBuilder)
        self.layout ().addWidget (holder_NetworkStep)
        
        
        self.btn_network_step.clicked.connect (g_signals.sig_field_trigget_step)
        self.auto_timer.timeout.connect (g_signals.sig_field_trigget_step)
        

        self.btn_Reget.clicked.connect (self.slot_trigger_regen)
        
        g_signals.sig_field_static_changes.connect (self.slot_handle_regen)

        g_signals.sig_after_field_regen.connect (self.w_routes.showRoutes)
        g_signals.sig_field_static_changes.connect (self.w_routes.showRoutes)
        g_signals.sig_field_network_step.connect (self.w_routes.showRoutes)

    def slot_handle_auto (self):
        if not self.running_auto:
            self.running_auto = True
            self.auto_timer.start (
                self.spin_AutoDelay.value ()
            )
            self.btn_Auto.setText ("stop")
        else:
            self.auto_timer.stop ()
            self.running_auto = False
            self.btn_Auto.setText ("play")

    def slot_trigger_regen (self):
        nodes_count = self.spin_NodesCount.value ()
        g_signals.sig_regen.emit (nodes_count, 10)

    def slot_handle_regen (self):
        nodes_count = len (g_field.nodes)
        self.spin_ReqSrc.setMaximum (nodes_count)
        self.spin_ReqSrc.setEnabled (True)
        self.spin_ReqDst.setMaximum (nodes_count)
        self.spin_ReqDst.setEnabled (True)
        self.btn_Rnd.setEnabled (True)
        self.slot_check_RREQ_addresses ()

    def get_RREQ_addresses (self):
        src = self.spin_ReqSrc.value ()
        dst = self.spin_ReqDst.value ()
        return src, dst

    def slot_ask_to_RREQ (self):
        src, dst = self.get_RREQ_addresses ()
        if src == dst: return
        g_signals.sig_start_RREQ.emit (src, dst)

    def slot_check_RREQ_addresses (self):
        src, dst = self.get_RREQ_addresses ()
        
        if src == dst: self.btn_ReqSend.setEnabled (False)
        else: self.btn_ReqSend.setEnabled (True)


    def slot_do_rnd_addresses (self):
        src, dst = random.randint (0, len (g_field.nodes), 2)
        self.spin_ReqSrc.setValue (src)
        self.spin_ReqDst.setValue (dst)

class PktsView (qtw.QFrame):
    
    def __init__(self, id) -> None:
        super().__init__()

        self.id = id

        self.setWindowTitle (f'p: {self.id}')

        self.setLayout(qtw.QVBoxLayout())
        self.setSizePolicy (QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        self.t_in = qtw.QTextEdit ()
        self.t_in.setReadOnly (True)
        self.t_in.resize (300, 50)
        self.t_out = qtw.QTextEdit ()
        self.t_out.setReadOnly (True)
        self.t_out.resize (300, 50)
        self.layout ().addWidget (self.t_in)
        self.layout ().addWidget (self.t_out)
        
        # self.setMinimumHeight (300)
        self.setMinimumWidth (500)
        self.reshow_pkts ()

        g_signals.sig_field_static_changes.connect (self.reshow_pkts)
        g_signals.sig_field_network_step.connect (self.reshow_pkts)

    def reshow_pkts (self):
        if not g_field.is_ready ():
            self.hide (); return
        str_in = ""; str_out = ""

        for p in g_field.nodes [self.id].pkts_in:
            str_in += f'{p}<br>'
        for p in g_field.nodes [self.id].pkts_out:
            str_out += f'{p}<br>'
        
        self.t_in.setText (str_in)
        self.t_out.setText (str_out)

    def event (self, e: QEvent):
        t = e.type ()
        if t == QEvent.WindowActivate:
            self.setWindowOpacity(1) 
        elif t == QEvent.WindowDeactivate:
            self.setWindowOpacity(0.5)
        return super ().event (e)


class WorkArea (qtw.QFrame):
    def __init__(self) -> None:
        super().__init__()

        self.ws_pkts = dict ()

        lay = qtw.QHBoxLayout ()
        lay.setSizeConstraint (qtw.QLayout.SetMaximumSize)
        lay.setSpacing (20)
        self.setContentsMargins (20, 20, 20, 20)
        

        holder_DrawingField = qtw.QFrame ()
        holder_DrawingField.setContentsMargins (10, 10, 10, 10)
        holder_DrawingField.setObjectName ("holder_DrawingField")
        holder_DrawingField.setLayout (qtw.QVBoxLayout ())
        self.drawing_field = DrawingField ()
        holder_DrawingField.layout ().addWidget (self.drawing_field)
        
        holder_ControlField = qtw.QFrame ()
        holder_ControlField.setContentsMargins (10, 10, 10, 10)
        holder_ControlField.setObjectName ("holder_ControlField")
        holder_ControlField.setLayout (qtw.QVBoxLayout ())
        holder_ControlField.layout ().addWidget (ControlField ())
        holder_ControlField.setMaximumWidth (400)
        
        lay.addWidget (holder_DrawingField)
        lay.addWidget (holder_ControlField)

        self.drawing_field.sig_show_pkts.connect (self.slot_show_pkts)
                
    
        self.setLayout (lay)

        self.setStyleSheet (
            "#holder_DrawingField, #holder_ControlField"
            "{"
            "border-radius: 20px;"
            "}"
            "#holder_ControlField"
            "{"
            "background-color: #EEE;"
            "}"
            "#holder_DrawingField"
            "{"
            "background-color: #FFF;"
            "}"
            "QLabel"
            "{"
            "color: #000;"
            "}"
        )

    def slot_show_pkts (self, a):
        print (f'show: {a}')
        if a not in self.ws_pkts:
            self.ws_pkts [a] = PktsView (a)
            old_flags = self.ws_pkts [a].windowFlags()
            self.ws_pkts [a].setWindowFlags(
                old_flags | Qt.WindowStaysOnTopHint)
        self.ws_pkts [a].show ()




class Main (qtw.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle ("DSR )))0")
        self.setLayout (qtw.QVBoxLayout ())
        self.layout ().addWidget (WorkArea ())
        # self.setCentralWidget (WorkArea ())








