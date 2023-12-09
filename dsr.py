
from network_generation import GooDGrapthGenerator as NetGen
from network_thread import dsr_node_thread
from globals import g_field, g_signals

from PyQt5.QtWidgets import QApplication

from app_widgets import Main


def regen_field (network_size, network_radius=10):
    gen = NetGen ()
    points, shrinked_network_radius = gen.gen (network_size, network_radius)
    g_field.run (
        points,
        shrinked_network_radius,
        dsr_node_thread
    )

    g_signals.sig_field_static_changes.emit ()
    g_signals.sig_after_field_regen.emit ()
    g_field.network_step ()

def step_field ():
    g_field.network_step ()
    g_signals.sig_field_network_step.emit ()
    g_signals.sig_field_static_changes.emit ()


def start_RREQ (src, dst):
    g_field.start_RREQ (src, dst)
    g_signals.sig_field_static_changes.emit ()


if __name__ == "__main__":

    app = QApplication ([])
    df = Main ()
    

    # network_size = 50
    # network_radius = 10

    # gen = NetGen ()

    # g_field.run (
    #     gen.gen (network_size, network_radius),
    #     network_radius,
    #     dsr_node_thread
    # )

    df.showMaximized ()

    g_signals.sig_regen.connect (regen_field)
    g_signals.sig_field_trigget_step.connect (step_field)
    g_signals.sig_start_RREQ.connect (start_RREQ)
    

    # g_signals.sig_field_update.emit ()
    # g_field.network_step ()

    app.exec ()



    # import matplotlib
    # import matplotlib.pyplot as plt
    # import numpy as np
    # import matplotlib.cm as cm    
    # colors = cm.rainbow(np.linspace(0, 1, len(clusters)))
    # fig = plt.figure()
    # for cl, color in zip (clusters, colors):
    #     plt.scatter(
    #         [p.x for p in cl],
    #         [p.y for p in cl],
    #         color=color
    #     )
    # plt.ylim(-50, 50)
    # plt.xlim(-50, 50)
    # plt.show ()



