from npPirata import vectorNegative, dot, multVectorScalar, normVector, reflectVector, subtractVectors, vectorMagnitude


class Light(object):
    def __init__(self, intensity = 1, color = (1, 1, 1), lightType = "None"):
        self.intensity = intensity
        self.color = color
        self.lightType = lightType

    def getLightColor(self):
        return [self.color[0] * self.intensity,
                self.color[1] * self.intensity,
                self.color[2] * self.intensity]

    def getDifusseColor(self, intercept):
        return None

    def getSpecularColor(self, intercept, viewPos):
        return None

class AmbientLight(Light):
    def __init__(self, intensity = 1, color = (1, 1, 1)):
        super().__init__(intensity, color, "Ambient")


class DirectionalLight(Light):
    def __init__(self, direction = (0, -1, 0), intensity = 1, color = (1, 1, 1)):
        self.direction = normVector(direction)
        super().__init__(intensity, color, "Directional")

    def getDifusseColor(self, intercept):
        lightColor = super().getDifusseColor(intercept)

        dir = vectorNegative(self.direction)

        intensity = dot(intercept.normal, dir) * self.intensity
        intensity = max(0, min(1, intensity))

        intensity *= 1 - intercept.obj.material.ks

        diffuseColor = multVectorScalar(self.color, intensity)

        return diffuseColor

    def getSpecularColor(self, intercept, viewPos):
        dir = vectorNegative(self.direction)

        reflect = reflectVector(dir, intercept.normal)

        viewDir = subtractVectors(viewPos, intercept.point)
        viewDir = normVector(viewDir)

        specIntensity = max(0, dot(viewDir, reflect)) ** intercept.obj.material.specular
        specIntensity *= intercept.obj.material.ks
        specIntensity *= self.intensity

        specColor = multVectorScalar(self.color, specIntensity)

        return specColor


class PointLight(Light):
    def __init__(self, point = (0, 0, 0), intensity = 1, color = (1, 1, 1)):
        self.point = point
        super().__init__(intensity, color, "Point")

    def getDifusseColor(self, intercept):
        dir = subtractVectors(self.point, intercept.point)
        R = vectorMagnitude(dir)
        dir = normVector(dir)

        intensity = dot(intercept.normal, dir) * self.intensity
        intensity *= 1 - intercept.obj.material.ks

        if R != 0:
            intensity /= R ** 2

        intensity = max(0, min(1, intensity))

        diffuseColor = multVectorScalar(self.color, intensity)

        return diffuseColor

    def getSpecularColor(self, intercept, viewPos):
        dir = subtractVectors(self.point, intercept.point)
        R = vectorMagnitude(dir)
        dir = normVector(dir)

        reflect = reflectVector(dir, intercept.normal)

        viewDir = subtractVectors(viewPos, intercept.point)
        viewDir = normVector(viewDir)

        specIntensity = max(0, dot(viewDir, reflect)) ** intercept.obj.material.specular
        specIntensity *= intercept.obj.material.ks
        specIntensity *= self.intensity

        if R != 0:
            specIntensity /= R ** 2

        specIntensity = max(0, min(1, specIntensity))

        specColor = multVectorScalar(self.color, specIntensity)

        return specColor
