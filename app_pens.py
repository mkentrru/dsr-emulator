
from PyQt5.QtGui import QPen, QColor, QFont
from PyQt5.QtCore import Qt


def gen_pen_node ():
    p = QPen (QColor ("#1F1"))
    p.setWidth (6)
    return p

def gen_font_id ():
    f = QFont ()
    f.setPointSize (7)
    return f

def gen_pen_default ():
    p = QPen (QColor ("#000"))
    p.setWidth (1)
    return p

def gen_pen_radius ():
    p = QPen (QColor ("#88f"))
    p.setWidth (1)
    p.setStyle (Qt.DotLine)
    return p

def gen_pen_broadcast ():
    p = QPen (QColor ("#000"))
    p.setWidth (2)
    p.setStyle (Qt.DotLine)
    return p

def gen_pen_RREQ ():
    p = gen_pen_broadcast ()
    p.setColor (QColor ("#f2b100"))
    return p

def gen_pen_RREP ():
    p = gen_pen_broadcast ()
    p.setColor (QColor ("#15f200"))
    return p

def gen_pen_requested_route ():
    p = QPen (QColor ("#F00"))
    p.setWidth (2)
    p.setStyle (Qt.DotLine)
    return p

def gen_pen_link ():
    p = QPen (QColor ("#888"))
    p.setWidth (1)
    p.setStyle (Qt.DashLine)
    return p

def gen_route_pen ():
    p = QPen (QColor ("#00F"))
    p.setWidth (2)
    p.setStyle (Qt.DotLine)
    return p

def gen_pen_notice ():
    p = QPen (QColor ("#00f22a"))
    p.setWidth (2)
    # p.setStyle (Qt.DashLine)
    return p
