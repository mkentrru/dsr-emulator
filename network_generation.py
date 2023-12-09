from point import Point, p_dist, build_links
from numpy import random
import math
import statistics
from operator import attrgetter

# from pprint import pprint

# import matplotlib
# import matplotlib.pyplot as plt

class GooDGrapthGenerator:


    def distribute_positions (self, pos, r):
        points_count = len (pos)
                
        for sr in range (r, int (self.size / 2)):
            
            adjusted_points = [Point (
                pos [id][0] * sr,
                pos [id][1] * sr,
                id) for id in range (points_count)]
            
            if points_count > 3:    
                links = build_links (adjusted_points, r)
                
                min_links_count = min (
                    [len (links_list) 
                    for links_list in links.values ()])
                
                if min_links_count > int (points_count / 2) + 1:
                    continue
                if min_links_count < 2:
                    return None

            return adjusted_points
        
        return None

    def gen_cluster (self, size):

        while True:
            positions = []

            for _ in range (size):
                x = y = 1
                while   (x ** 2) >= 1 or \
                        (y ** 2) >= 1 or \
                        (x, y) in positions:
                    pos = random.normal (0, 0.4, 2)
                    x = pos [0]; y = pos [1]
                positions.append ((x, y))
            
            distributed = self.distribute_positions (
                positions, self.r)
            
            if distributed is not None:
                return distributed
        
        

    def destribute_sizes (self, n, clusters_count):
        locations = [0.1 * a for a in range (1, 5)]
        i_loc = -1
        while True:
            i_loc = i_loc + 1
            if i_loc >= len (locations): i_loc = 0
            
            sizes = [
                int(n * d) for d 
                in random.normal (locations [i_loc], 0.2, clusters_count)
                ]
            
            if min (sizes) <= 0: continue
            
            if sum (sizes) < n:
                while sum (sizes) < n:
                    rand_i = random.randint (0, clusters_count)
                    sizes [rand_i] += 1
                # rework sizes if contains cluster with 1 node
                if n >= clusters_count * 2 and \
                    1 in sizes: continue

                return sizes
            

            

    def center_cluster (self, c):
        m_x = statistics.mean ([p.x for p in c])
        m_y = statistics.mean ([p.y for p in c])
        return Point (m_x, m_y)

    def move_cluster (self, c, dx, dy):
        for p in c:
            p.x += dx
            p.y += dy

    def get_cluster_sizes (self, c):
        x_start = min (p.x for p in c)
        x_end = max (p.x for p in c)
        y_start = min (p.y for p in c)
        y_end = max (p.y for p in c)
        width = x_end - x_start
        height = y_end - y_start
        return width, height

    def move_cluster_closer_to_point (self, c, point: Point):
        c_center = self.center_cluster (c)
        dx = point.x - c_center.x
        dy = point.y - c_center.y
        c_w, c_h = self.get_cluster_sizes (c)

        overflow_x = round (self.size / 2 - (abs (point.x) + c_w / 2))
        if overflow_x > 0: overflow_x = 0
        overflow_y = round (self.size / 2 - (abs (point.y) + c_h / 2))
        if overflow_y > 0: overflow_y = 0
        
        if dx < 0: overflow_x = -overflow_x
        if dy < 0: overflow_y = -overflow_y

        dx += overflow_x; dy += overflow_y
        self.move_cluster (c, dx, dy)
        return c_center.x + dx, c_center.y + dy
        
    def accelirate_diff_point (self, src, dst, sr, step=1):
        d = step
        dx = dy = 0
        pdx = dst.x - src.x; pdy = dst.y - src.y
        if pdx == 0:
            if pdy > 0: return (sr - d, 0, -1)
            else: return (sr - d, 0, 1)
        angle = math.atan (pdy / pdx)
        if pdx > 0: angle += math.pi

        while sr > 0:
            while True:
                dx = round (d * math.cos (angle))
                dy = round (d * math.sin (angle))
                if dx != 0 or dy != 0:
                    sr -= d
                    return sr, dx, dy 
                d += step
        return None



    # we care only unique links
    def calculate_clusters_links (self, ca, cb, r):
        res = 0
        na = []; nb = []
        for a in ca:
            for b in cb:
                if p_dist (a, b) < r and \
                    a not in na and b not in nb:
                        res += 1
                        na.append (a); nb.append (b)
                        break
        return res


    def merge_clusters (self, ca, cb):
        if ca is None:
            return cb
        
        p_center_of_da_map = Point (0, 0)
        self.move_cluster_closer_to_point (ca, p_center_of_da_map)
        # keep ca at center
        # put cb to random edge of radius
        # and move closer to ca
        angle_degr = random.randint (0, 360)
        angle = math.radians (angle_degr)
        sr = self.size / 2

        # edge point
        next_point = Point (
            sr * math.cos (angle),
            sr * math.sin (angle))
        old_x, old_y = self.move_cluster_closer_to_point (cb, next_point)

        while True:
            # plt.scatter(
            #     [p.x for p in ca], [p.y for p in ca],
            #     color="#F00"
            # )
            # plt.scatter(
            #     [p.x for p in cb], [p.y for p in cb],
            #     color="#0F0"
            # )
            # plt.show ()
            # calculate links between clusters
            merging_links = self.calculate_clusters_links (ca, cb, self.r)
            if merging_links >= 2: 
                break
            # if not enought links: move cluster closer
            # find next closer point

            diff_calc_res = self.accelirate_diff_point (
                next_point, p_center_of_da_map, sr, self.r / 2)
            # pprint (diff_calc_res)
            if diff_calc_res is None: 
                break
            sr = diff_calc_res [0]; dx = diff_calc_res [1]; dy = diff_calc_res [2]

            next_point = Point (old_x - dx, old_y - dy)
            next_x, next_y = self.move_cluster_closer_to_point (cb, next_point)
            # failed to move fully: no space to move
            if next_x != next_point.x or next_y != next_point.y: 
                break
            old_x = next_x; old_y = next_y
        
        res = ca
        res.extend (cb)

        return res
            
    def shrink_r (self, points, r):
        old_links = build_links (points, r)
        d = r / 100
        nr = r - d
        while nr > 0:
            new_links = build_links (points, nr)
            if new_links == old_links:
                r = nr
            else:
                break
            nr = nr - d

        return r

    def gen (self, n, r, size=100):
        self.n = n; self.r = r
        self.size = size 

        clusters_count = 1 + int (self.n / 6)

        sizes = self.destribute_sizes (n, clusters_count)
        print (sizes)
        # clusters = list ()
        merged_clusters = None

        for cluster_size in sizes:
            new_cluster = self.gen_cluster (cluster_size)
            # pprint (new_cluster)
            # plt.ion ()
            
            merged_clusters = self.merge_clusters (merged_clusters, new_cluster)
            
            # clusters.append (new_cluster)

        for a in range (len (merged_clusters)):
            merged_clusters [a].id = a
        
        # r = self.shrink_r (merged_clusters, r)
        # pprint (clusters)
        self.move_cluster_closer_to_point (merged_clusters, Point (0, 0))
        
        return merged_clusters, r
        



