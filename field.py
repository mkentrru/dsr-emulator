
from threading import Condition as cv
from threading import Thread as thr

from point import Point, build_links

class Pkt:
    def __init__(self, type, src, dst, aux) -> None:
        self.type = type
        self.src = src
        self.dst = dst
        self.aux = aux

    def __str__(self) -> str:
        return f'{self.type}: {self.src} -> {self.dst}: {self.aux}'
    def __repr__(self) -> str:
        return self.__str__ ()

class Node:
    def __init__(self, x, y, id) -> None:
        self.x = x; self.y = y; self.id = id

        self.pkts_in = list ()
        self.pkts_out = list ()

        self.routes = dict ()

        self.idle = True
        self.dropped = False

        self.req_id = 0

        self.handled_reqs = dict ()

    def id (self):
        return self.point.id
    
    def get_reqid (self):
        self.req_id = self.req_id + 1
        return self.req_id

    def __str__(self) -> str:
        return self.point.__str__ ()
    def __repr__(self) -> str:
        return self.__str__ ()

    def pop_in (self):
        if not len (self.pkts_in): return None
        return self.pkts_in.pop (0)
    def pop_out(self):
        if not len (self.pkts_out): return None
        return self.pkts_out.pop (0)

    def mark_dropped (self, v=True):
        self.dropped = v



class Field:
    
    def __init__(self) -> None:
        self.nodes = list ()
        self.threads = list ()
        self.links = dict ()
        self.network_lock = cv ()
        self.inited = False
        

    def reset (self):
        self.inited = False
        self.notify_nodes ()
        self.nodes.clear ()
        self.links.clear ()
        self.threads.clear ()
    
    def is_ready (self) -> bool: return self.inited

    def notify_nodes (self):
        with self.network_lock:
            self.network_lock.notify_all ()

    def run (self, points, r, f_node_thread):
        self.reset ()

        self.r = r
        self.n = len (points)
        
        self.nodes = [
            Node (p.x, p.y, id) 
            for p, id in zip (points, range (self.n))]
        
        self.threads = [
            thr (target=f_node_thread, args=[self, n]) for n in self.nodes
        ]

        for t in self.threads: t.start ()
        self.inited = True
        
        
    def lock_for_network_step (self):
        with self.network_lock:
            # self.idle_nodes += 1
            self.network_lock.wait ()

    def network_step (self):
        self.notify_nodes ()

    def get_sizes (self):
        xs = [p.x for p in self.nodes]
        x_start = min (xs); x_end = max (xs)
        ys = [p.y for p in self.nodes]
        y_start = min (ys)
        y_end = max (ys)
        
        width = x_end - x_start
        height = y_end - y_start
        return width, height

    def get_links (self):
        return build_links (self.nodes, self.r)

    def mark_idle (self, id):
        if not self.is_ready (): return
        self.nodes [id].idle = True
    def mark_active (self, id):
        if not self.is_ready (): return
        self.nodes [id].idle = False

    def unicast_PKT (self, dst, p: Pkt):
        if not self.is_ready (): return
        self.nodes [dst].pkts_in.append (p)

    def broadcast_PKT (self, src, p: Pkt):
        links = self.get_links ()
        send_to = links [src]
        # print ('broadcast to:', send_to)
        for node_id in send_to:
            self.nodes [node_id].pkts_in.append (p)

    def start_RREQ (self, src, dst):
        ROUTE = Pkt (
            "ROUTE", None, None,
            {
                "target": dst
                })
        self.unicast_PKT (src, ROUTE)
        
