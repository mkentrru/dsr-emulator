
from PyQt5.QtCore import QObject, pyqtSignal

class AppSignals (QObject):
    sig_field_static_changes = pyqtSignal ()
    sig_field_network_step = pyqtSignal ()
    sig_field_trigget_step = pyqtSignal ()

    sig_regen = pyqtSignal (int, int)
    sig_after_field_regen = pyqtSignal ()

    sig_start_RREQ = pyqtSignal (int, int)

    
