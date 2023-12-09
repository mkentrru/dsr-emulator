from math import sqrt

class Point:
    def __init__(self, x, y, id=0) -> None:
        self.x = round (x); self.y = round (y)
        self.id = id

    def __str__(self) -> str:
        return f'({self.id}: {self.x}, {self.y})'

    def __repr__(self) -> str:
        return self.__str__ ()

def p_dist (a: Point, b: Point):
    return sqrt ((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

def build_links (positions, r):
        
    links = dict ()
    
    for p in positions:
        links [p.id] = list ()

    l = len (positions)
    for a in range (l):
        for b in range (a + 1, l):
            d = p_dist (positions [a], positions [b])
            if d < r:
                if b not in links [a]:
                    links [a].append (b)
                if a not in links [b]:
                    links [b].append (a)       
    return links

