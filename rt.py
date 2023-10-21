from math import tan, pi, atan2, acos
from materials import OPAQUE, REFLECTIVE, TRANSPARENT
from npPirata import normVector, dot, vectorNegative, subtractVectors, reflectVector, addVectors, addVectorScalar, subtractVectorScalar, multVectorScalar, refractVector, totalInternalReflection, fresnel, vectorMagnitude, multMV
from obj import Obj
from figures import Triangle

maxRecursionDepth = 3

class Model(object):
    def __init__(self, filename, position = (0, 0, 0), material = None):
        model = Obj(filename)

        self.vertices = model.vertices
        self.texCoords = model.texCoords
        self.normals = model.normals
        self.faces = model.faces
        
        self.position = position
        self.material = material            

class Raytracer(object):
    def __init__(self, screen):
        self.screen = screen
        _,_, self.width, self.height = screen.get_rect()

        self.scene = []
        self.lights = []

        self.camPosition = [0, 0, 0]

        self.rtViewPort(0, 0, self.width, self.height)
        self.rtProjection()

        self.rtClearColor(0, 0, 0)
        self.rtColor(1, 1, 1)
        self.rtClear()

        self.envMap = None
        
    def rtClearColor(self, r, g, b):
        self.clearColor = (r * 255, g * 255, b * 255)

    def rtClear(self):
        self.screen.fill(self.clearColor)

    def rtColor(self, r, g, b):
        self.currColor = (r * 255, g * 255, b * 255)

    def rtPoint(self, x, y, color = None):
        y = self.height - y
        if (0 <= x <= self.width) and (0 <= y <= self.height):
            if color != None:
                color = (int(color[0] * 255), 
                        int(color[1] * 255),
                        int(color[2] * 255))
                self.screen.set_at((x, y), color)
            else:
                self.screen.set_at((x, y), self.currColor)

    def rtCastRay(self, orig, dir, sceneObj = None, recursion = 0):
        if recursion >= maxRecursionDepth:
            return None
            
        intersect = None
        hit = None
        depth = float('inf')
        for obj in self.scene:
            if sceneObj != obj:
                intersect = obj.ray_intersect(orig, dir)
                
                if intersect != None:
                    if intersect.distance < depth:
                        hit = intersect
                        depth = intersect.distance

        return hit

    def rtRayColor(self, intercept, rayDirection, recursion = 0):
        if intercept == None:
            if self.envMap:
                x = (atan2(rayDirection[2], rayDirection[0]) / (2 * pi) + 0.5) * self.envMap.get_width()# - 1
                y = acos(rayDirection[1]) / pi * self.envMap.get_height()# - 1

                envColor =  self.envMap.get_at((int(x), int(y)))

                return [i / 255 for i in envColor]
            else:
                return None
        
        material = intercept.obj.material

        finalColor = [0, 0, 0]
        surfaceColor = material.diffuse

        if material.texture and intercept.texCoords:
            tx = intercept.texCoords[0] * material.texture.get_width() - 1
            ty = intercept.texCoords[1] * material.texture.get_height() - 1
            
            texColor = material.texture.get_at((int(tx), int(ty)))
            texColor = [i / 255 for i in texColor]
            surfaceColor = [surfaceColor[i] * texColor[i] for i in range(3)]

        ambientColor = [0, 0, 0]
        diffuseColor = [0, 0, 0]
        specularColor = [0, 0, 0]
        reflectColor = [0, 0, 0]
        refractColor = [0, 0, 0]

        if material.matType == OPAQUE:
            for light in self.lights:
                if light.lightType == "Ambient":
                    lightColor = light.getLightColor()
                    ambientColor[0] += lightColor[0]
                    ambientColor[1] += lightColor[1]
                    ambientColor[2] += lightColor[2]

                else:
                    shadowIntersect = None
                    lightDir = None
                    if light.lightType == "Directional":
                        lightDir = vectorNegative(light.direction)
                    elif light.lightType == "Point":
                        lightDir = subtractVectors(light.point, intercept.point)
                        lightDistance = vectorMagnitude(lightDir)
                        lightDir = normVector(lightDir)

                    shadowIntersect = self.rtCastRay(intercept.point, lightDir, intercept.obj)
                    
                    if shadowIntersect == None or (light.lightType == "Point" and shadowIntersect != None and shadowIntersect.distance > lightDistance):
                        diffuseLightColor = light.getDifusseColor(intercept)
                        diffuseColor[0] += diffuseLightColor[0]
                        diffuseColor[1] += diffuseLightColor[1]
                        diffuseColor[2] += diffuseLightColor[2]
                        specularLightColor = light.getSpecularColor(intercept, self.camPosition)
                        specularColor[0] += specularLightColor[0]
                        specularColor[1] += specularLightColor[1]
                        specularColor[2] += specularLightColor[2]

        elif material.matType == REFLECTIVE:
            reflect = reflectVector(vectorNegative(rayDirection), intercept.normal)
            reflectIntercept = self.rtCastRay(intercept.point, reflect, intercept.obj, recursion + 1)
            reflectColor = self.rtRayColor(reflectIntercept, reflect, recursion + 1)

            for light in self.lights:
                if light.lightType != "Ambient":
                    lightDir = None
                    if light.lightType == "Directional":
                        lightDir = vectorNegative(light.direction)
                    elif light.lightType == "Point":
                        lightDir = subtractVectors(light.point, intercept.point)
                        lightDistance = vectorMagnitude(lightDir)
                        lightDir = normVector(lightDir)

                    shadowIntersect = self.rtCastRay(intercept.point, lightDir, intercept.obj)

                    if shadowIntersect == None or (light.lightType == "Point" and shadowIntersect != None and shadowIntersect.distance > lightDistance):
                        specularLightColor = light.getSpecularColor(intercept, self.camPosition)
                        specularColor[0] += specularLightColor[0]
                        specularColor[1] += specularLightColor[1]
                        specularColor[2] += specularLightColor[2]

        elif material.matType == TRANSPARENT:
            outside = dot(rayDirection, intercept.normal) < 0
            bias = multVectorScalar(intercept.normal, 0.001)

            reflect = reflectVector(vectorNegative(rayDirection), intercept.normal)
            reflectOrigin = addVectors(reflect, bias) if outside else subtractVectors(reflect, bias)
            reflectIntercept = self.rtCastRay(reflectOrigin, reflect, None, recursion + 1)
            reflectColor = self.rtRayColor(reflectIntercept, reflect, recursion + 1)

            for light in self.lights:
                if light.lightType != "Ambient":
                    lightDir = None
                    if light.lightType == "Directional":
                        lightDir = vectorNegative(light.direction)
                    elif light.lightType == "Point":
                        lightDir = subtractVectors(light.point, intercept.point)
                        lightDistance = vectorMagnitude(lightDir)
                        lightDir = normVector(lightDir)

                    shadowIntersect = self.rtCastRay(intercept.point, lightDir, intercept.obj)

                    if shadowIntersect == None or (light.lightType == "Point" and shadowIntersect != None and shadowIntersect.distance > lightDistance):
                        specularLightColor = light.getSpecularColor(intercept, self.camPosition)
                        specularColor[0] += specularLightColor[0]
                        specularColor[1] += specularLightColor[1]
                        specularColor[2] += specularLightColor[2]

            if not totalInternalReflection(intercept.normal, rayDirection, 1.0, material.ior):
                refract = refractVector(intercept.normal, rayDirection, 1, material.ior)
                refractOrigin = subtractVectors(intercept.point, bias) if outside else addVectors(intercept.point, bias)
                refractIntercept = self.rtCastRay(refractOrigin, refract, None, recursion + 1)
                refractColor = self.rtRayColor(refractIntercept, refract, recursion + 1)

                kr, kt = fresnel(intercept.normal, rayDirection, 1, material.ior)
                reflectColor = multVectorScalar(reflectColor, kr)
                refractColor = multVectorScalar(refractColor, kt)
        
        lightColor = [(ambientColor[i] + diffuseColor[i] + specularColor[i] + reflectColor[i] + refractColor[i]) for i in range(3)]
        finalColor = [min(1,(surfaceColor[i] * lightColor[i])) for i in range(3)]

        return finalColor
    
    def loadModel(self, model):
        modelMatrix = [[1, 0, 0, model.position[0]],
                        [0, 1, 0, model.position[1]],
                        [0, 0, 1, model.position[2]],
                        [0, 0, 0, 1]]

        
        for face in model.faces:
            vertCount = len(face)
            v0 = model.vertices[face[0][0] - 1] + [1]
            v1 = model.vertices[face[1][0] - 1] + [1]
            v2 = model.vertices[face[2][0] - 1] + [1]

            v0 = multMV(modelMatrix, v0)[:-1]
            v1 = multMV(modelMatrix, v1)[:-1]
            v2 = multMV(modelMatrix, v2)[:-1]

            self.scene.append(Triangle(material=model.material, v0=v0, v1=v1, v2=v2))

            if vertCount == 4:
                v3 = model.vertices[face[3][0] - 1] + [1]
                v3 = multMV(modelMatrix, v3)[:-1]
                self.scene.append(Triangle(material=model.material, v0=v0, v1=v2, v2=v3))

    def rtRender(self):
        for x in range(self.vpX, self.vpX + self.vpWidth + 1):
            for y in range(self.vpY, self.vpY + self.vpHeight + 1):
                if (0 <= x <= self.width) and (0 <= y <= self.height):
                    px = ((x + 0.5 - self.vpX) / self.vpWidth) * 2 - 1
                    py = ((y + 0.5 - self.vpY) / self.vpHeight) * 2 - 1

                    px *= self.rightEdge
                    py *= self.topEdge

                    direction = (px, py, - self.nearPlane)
                    direction = normVector(direction)

                    intercept =  self.rtCastRay(self.camPosition, direction)
                    
                    rayColor = self.rtRayColor(intercept, direction)

                    if rayColor:
                        self.rtPoint(x, y, rayColor)
                        

    def rtViewPort(self, posX, posY, width, height):
        self.vpX = posX
        self.vpY = posY
        self.vpWidth = width
        self.vpHeight = height

    def rtProjection(self, fov = 60, n = 0.1):
        aspectRatio = self.vpWidth / self.vpHeight
        self.nearPlane = n
        self.topEdge = tan((fov * pi / 180) / 2) * self.nearPlane
        self.rightEdge = self.topEdge * aspectRatio

