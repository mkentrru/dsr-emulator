from field import Field, Node, Pkt

import copy

from globals import g_field


def handle_ROUTE (f: Field, node: Node, p: Pkt):
    # skip routes from cache
    if p.dst in node.routes: return
    RREQ = Pkt (
        "RREQ", node.id, None,
        {
            "origin"    : node.id,
            "target"    : p.aux ["target"],
            "path"      : [node.id],
            "req_id": node.get_reqid ()
        }
    )
    node.pkts_out.append (RREQ)
    return True



def handle_RREQ (f: Field, node: Node, p: Pkt):
    # skip if we already handled this fuck))
    origin = p.aux ["origin"]
    target = p.aux ["target"]
    path = p.aux ["path"]
    
    if target in path: return False

    if node.id in p.aux ["path"]:
        return False
    if node.id == p.aux ["target"]:
        src = p.aux ["origin"]
        dst = node.id

        path.append (dst)
        if src in node.routes:
            if len (path) >= len (node.routes [src]):
                return False
            
        
        node.routes [src] = path
        
        path.reverse ()
        RREP = Pkt (
            "RREP", dst, path [1],
            {
                "path" : path
                })
        node.pkts_out.append (RREP)

        return True
    
    req_id = p.aux ["req_id"]
    if origin in node.handled_reqs:
        if req_id in node.handled_reqs [origin]:
            return False
        else:
            node.handled_reqs [origin].append (req_id)
    else:
        node.handled_reqs [origin] = [req_id]

    """
    Node appends its own address to the route record in the
    ROUTE R EQUEST message and propagates it by transmitting 
    it as a local broadcast packet 
    """

    answer = copy.deepcopy (p)
    answer.src = node.id
    answer.aux ["path"].append (node.id)
    node.pkts_out.append (answer)

    return True

def handle_RREP (f: Field, node: Node, p: Pkt):
    path = p.aux ["path"]
    if node.id not in path: return False

    if node.id == path [-1]:
        src = p.aux ["path"][0]

        if src in node.routes:
            if len (path) >= len (node.routes [src]):
                return False
        
        path.reverse ()
        node.routes [src] = path
        return True

    this_pos = path.index (node.id)
    src_pos = path.index (p.src)
    
    if this_pos > src_pos:
        p.src = node.id
        p.dst = path [this_pos + 1]

        node.pkts_out.append (p)
        return True
    return False
    

def handle_pkt (f: Field, node: Node, p: Pkt):
    if p is None: return
    
    if p.dst is None or p.dst == node.id:
        if p.type == "ROUTE": res = handle_ROUTE (f, node, p)
        elif p.type == "RREQ": res = handle_RREQ (f, node, p)
        elif p.type == "RREP": res = handle_RREP (f, node, p)
    else: res = False

    if not res: 
        node.mark_dropped ()

def broadcast (f: Field, node: Node, p: Pkt):
    if p is None: return
    f.broadcast_PKT (node.id, p)

def dsr_node_thread (f: Field, node: Node, lock_at_startup=True):
    id = node.id

    while True:
        try:
            f.mark_idle (id)
            f.lock_for_network_step ()
            if not f.is_ready (): return
            f.mark_active (id)
            node.mark_dropped (False)
        
        
            p_in = node.pop_in (); p_out = node.pop_out ()
            handle_pkt (f, node, p_in)
            broadcast (f, node, p_out)
        except Exception as e:
            print (e)

        
