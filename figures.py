from math import tan, pi, atan2, acos
from npPirata import *


class Intercept(object):
    def __init__(self, distance, point, normal, texCoords, obj):
        self.distance = distance
        self.point = point
        self.normal = normal
        self.obj = obj
        self.texCoords = texCoords


class Shape(object):
    def __init__(self, position, material):
        self.position = position
        self.material = material

    def ray_intersect(self, orig, dir):
        return None


class Sphere(Shape):
    def __init__(self, position, radius, material):
        self.radius = radius
        super().__init__(position, material)

    def ray_intersect(self, orig, dir):
        L = subtractVectors(self.position, orig)
        magnitudL = vectorMagnitude(L)
        tca = dot(L, dir)
        d = (magnitudL ** 2 - tca ** 2) ** 0.5

        if type(d) is complex:
            d = float(d.real)

        if d > self.radius:
            return None

        thc = (self.radius ** 2 - d ** 2) ** 0.5
        t0 = tca - thc
        t1 = tca + thc

        if t0 < 0:
            t0 = t1
        if t0 < 0:
            return None
        
        dir = multVectorScalar(dir, t0)
        point = [orig[i] + dir[i] for i in range(3)]
        normal = subtractVectors(point, self.position)
        normal = normVector(normal)

        u = (atan2(normal[2], normal[0]) / (2 * pi)) + 0.5
        v = acos(normal[1]) / pi


        return Intercept(t0, point, normal, (u, v), self)


class Plane(Shape):
    def __init__(self, position, normal, material):
        self.normal = normVector(normal)
        super().__init__(position=position, material=material)

    def ray_intersect(self, orig, dir):
        denom = dot(dir, self.normal)

        if (abs(denom) <= 0.0001):
            return None
            
        num = dot((subtractVectors(self.position, orig)), self.normal)
        t = num / denom

        if (t < 0):
            return None

        point = addVectors(orig, multVectorScalar(dir, t))
        
        return Intercept(t, point, self.normal, None, self)

class Disk(Plane):
    def __init__(self, position, normal, radius, material):
        self.radius = radius
        super().__init__(position=position, normal=normal, material=material)

    def ray_intersect(self, orig, dir):
        planeIntersect = super().ray_intersect(orig, dir)

        if planeIntersect is None:
            return None
        
        contactDistance = subtractVectors(planeIntersect.point, self.position)

        contactDistance = vectorMagnitude(contactDistance)

        if (contactDistance > self.radius):
            return None
        
        return Intercept(planeIntersect.distance, planeIntersect.point, self.normal, None, self)


class AABB(Shape):
    def __init__(self, position, size, material):
        super().__init__(position=position, material=material)

        self.size = size
        self.planes = []

        leftPlane = Plane(position=addVectors(position, [-size[0] / 2, 0, 0]), normal=(-1, 0, 0), material=material)
        rightPlane = Plane(position=addVectors(position, [size[0] / 2, 0, 0]), normal=(1, 0, 0), material=material)

        bottomPlane = Plane(position=addVectors(position, [0, -size[1] / 2, 0]), normal=(0, -1, 0), material=material)
        topPlane = Plane(position=addVectors(position, [0, size[1] / 2, 0]), normal=(0, 1, 0), material=material)

        forigntPlane = Plane(position=addVectors(position, [0, 0, -size[2] / 2]), normal=(0, 0, -1), material=material)
        backPlane = Plane(position=addVectors(position, [0, 0, size[2] / 2]), normal=(0, 0, 1), material=material)

        self.planes.append(leftPlane)
        self.planes.append(rightPlane)
        self.planes.append(bottomPlane)
        self.planes.append(topPlane)
        self.planes.append(forigntPlane)
        self.planes.append(backPlane)

        self.boundsMin = [0, 0, 0]
        self.boundsMax = [0, 0, 0]

        self.bias = 0.001

        for i in range(3):
            self.boundsMin[i] = self.position[i] - (self.bias + size[i] / 2)
            self.boundsMax[i] = self.position[i] + (self.bias + size[i] / 2)

    def ray_intersect(self, orig, dir):
        intercept = None

        t = float('inf')
        u = v = 0

        for plane in self.planes:
            planeIntersect = plane.ray_intersect(orig=orig, dir=dir)

            if planeIntersect is not None:
                planePoint = planeIntersect.point

                if self.boundsMin[0] < planePoint[0] < self.boundsMax[0]:
                    if self.boundsMin[1] < planePoint[1] < self.boundsMax[1]:
                        if self.boundsMin[2] < planePoint[2] < self.boundsMax[2]:
                            if planeIntersect.distance < t:
                                t = planeIntersect.distance
                                intercept = planeIntersect

                                if abs(plane.normal[0]) > 0:
                                    u = (planePoint[1] - self.boundsMin[1]) / (self.size[1] + self.bias * 2)
                                    v = (planePoint[2] - self.boundsMin[2]) / (self.size[2] + self.bias * 2)
                                elif abs(plane.normal[1]) > 0:
                                    u = (planePoint[0] - self.boundsMin[0]) / (self.size[0] + self.bias * 2)
                                    v = (planePoint[2] - self.boundsMin[2]) / (self.size[2] + self.bias * 2)
                                elif abs(plane.normal[2]) > 0:
                                    u = (planePoint[0] - self.boundsMin[0]) / (self.size[0] + self.bias * 2)
                                    v = (planePoint[1] - self.boundsMin[1]) / (self.size[1] + self.bias * 2)

        if intercept is None:
            return None
        
        return Intercept(t, intercept.point, intercept.normal, (u, v), self)

# Intento muy fallido de hacer una cápsula :')
class Capsule(Shape):
    def __init__(self, position, material, pA, pB, radius):
        # pA y pB son los puntos de inicio y fin de la cápsula
        self.pA = pA
        self.pB = pB
        # radius es el radio de las esferas, o también se puede ver como el radio del cilindro (cuerpo)
        self.radius = radius
        super().__init__(position=position, material=material)

    def ray_intersect(self, orig, dir):
        # ba = pb - pa
        ba = subtractVectors(self.pB, self.pA)
        # oa = orig - pa
        oa = subtractVectors(orig, self.pA)

        baba = dot(ba, ba)
        badir = dot(ba, dir)
        baoa = dot(ba,oa)
        diroa = dot(dir,oa)
        oaoa = dot(oa,oa)

        a = baba - badir * badir
        b = baba * diroa - baoa * badir
        c = baba * oaoa - baoa * baoa - self.radius ** 2 * baba
        h = b * b - a * c

        if (h < 0):
            return None
        
        t = (-b - h ** 0.5) / a
        y = baoa + t * badir

        # Es parte de una de las esferas de los extremos
        oc = oa
        if (y > 0):
            oc = subtractVectors(orig, self.pB)
        b = dot(dir,oc)
        c = dot(oc,oc) - self.radius ** 2
        h = b ** 2 - c
        
        if (h == 0):
            return None
        d = - b - h ** 0.5

        # Es parte del cuerpo (el cilindro)
        if (y > 0 and y < baba):
            d = t

        if type(d) is complex:
            d = float(d.real)

        pa = subtractVectors(addVectors(orig, multVectorScalar(dir,d)), self.pA)
        temp = dot(pa,ba)
        if type(temp) is complex:
            temp = float(temp.real)
        h = min(max(temp / baba, 0), 1)
        # normal = (pa - h*ba)/r;
        normal = divVectorScalar(subtractVectors(pa,multVectorScalar(ba,h)), self.radius)

        point = addVectors(orig,multVectorScalar(dir,d))

        return Intercept(d, point, normal, None, self)

class Triangle(Shape):
    def __init__(self, material, v0, v1, v2):
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2

        position = [(v0[0] + v1[0] + v2[0]) / 3,
                    (v0[1] + v1[1] + v2[1]) / 3,
                    (v0[2] + v1[2] + v2[2]) / 3] 
        super().__init__(position=position,material=material)

    def ray_intersect(self, orig, dir):
        edge0 = subtractVectors(self.v1, self.v0)
        edge1 = subtractVectors(self.v2, self.v1)
        edge2 = subtractVectors(self.v0, self.v2)
        normal = cross(edge0, subtractVectors(self.v2,self.v0))
        normal = normVector(normal)

        denom = dot(normal, dir)
        if (abs(denom) <= 0.0001):
            return None

        d = -1 * dot(normal, self.v0)
        
        num = - 1 * (dot(normal,orig) + d)
        t = num / denom

        if t < 0:
            return None

        p = addVectors(orig, multVectorScalar(dir,t))
        
        vp0 = subtractVectors(p, self.v0)
        vp1 = subtractVectors(p, self.v1)
        vp2 = subtractVectors(p, self.v2)
        
        c0 = cross(edge0, vp0)
        c1 = cross(edge1, vp1)
        c2 = cross(edge2, vp2)

        if( (dot(normal,c0) < 0) or (dot(normal,c1) < 0) or (dot(normal,c2) < 0) ):
            return None

        uv = bcCoords(self.v0, self.v1, self.v2, p)

        return Intercept(t, p, normal, uv, self)

class Cylinder(Shape):
    def __init__(self, material, v0, v1, radius):
        self.v0 = v0
        self.v1 = v1
        self.radius = radius

        self.height = ((v1[0] - v0[0])**2 + (v1[1] - v0[1])**2 + (v1[2] - v0[2])**2) ** 0.5
        self.v = [v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]]

        position = [(v0[0] + v1[0]) / 2,
                    (v0[1] + v1[1]) / 2,
                    (v0[2] + v1[2]) / 2]

        super().__init__(position=position, material=material)

    def ray_intersect(self, orig, dir):
        a = dir[0] ** 2 + dir[2] ** 2
        #a = dot(dir, dir) - dot(dir,self.v) ** 2
        b = 2 * (orig[0] *  dir[0] + orig[2] * dir[2])
        #b = 2 * dot(dir,)
        c = orig[0] ** 2 + orig[2] ** 2 - self.radius

        discr = b ** 2 - 4 * a * c
        if (discr < 0):
            return None

        x1 = (-b + discr ** 0.5) / (2 * a)
        x2 = (-b - discr ** 0.5) / (2 * a)
        if (x1 > x2):
            t = x2
        
        if (t < 0):
            if (x1 < 0):
                return None
            t = x1

        point = addVectors(orig, multVectorScalar(dir, t))
        normal = [2 * point[0], 0, 2 * point[2]]

        if (point[1] < 0 or point[1] < self.height):
            return None

        if (dir[1] != 0.0):
            t3 = (0 - orig[1]) / dir[1]
            t4 = (self.height - orig[1]) / dir[1]
            t2 = min(t3, t4)
            if (t2 < 0):
                t2 = max(t3, t4)

            if (t2 >= 0):
                point = addVectors(orig, multVectorScalar(dir, t2))

                if (point[0] ** 2 + point[2] ** 2 <= self.radius ** 2 + 0.9):
                    t = min(t, t2)
                    if (t == t3):
                        normal = [0,-1,0]
                        return Intercept(t, point, normal, None, self)
                    elif (t == t4):
                        normal = [0,1,0]
                        return Intercept(t, point, normal, None, self)
        
        return Intercept(t, point, normal, None, self)
        
