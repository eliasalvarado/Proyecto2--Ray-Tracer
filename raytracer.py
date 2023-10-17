import pygame as pg
from pygame.locals import *
from rt import Raytracer
from figures import *
from materials import *
from lights import *

width = 720
height = 720

pg.init()

screen = pg.display.set_mode((width, height), pg.DOUBLEBUF | pg.HWACCEL | pg.HWSURFACE)
screen.set_alpha(None)

raytracer = Raytracer(screen=screen)
raytracer.envMap = pg.image.load("environmentMap.jpg")

#Opaca
orange = Material(diffuse=(0.9, 0.3, 0.08), specular=8, ks=0.01)
#Reflectiva
glass = Material(diffuse=(0.9, 0.9, 0.9), specular=64, ks=0.2, ior=1.5, matType=REFLECTIVE)
#Transparente
diamon = Material(diffuse=(0.9, 0.9, 0.9), specular=64, ks=0.2, ior=2.417, matType=TRANSPARENT)


#raytracer.scene.append(Capsule(position=(0,0,-15), pA=(0,0,-15), pB=(1,1,-15), radius=0.1, material=red))
raytracer.scene.append(Cylinder(material=orange, v0=(-1,3,-5), v1=(1,-3,-5), radius=3))
""" raytracer.scene.append(Triangle(material=orange, v0=(1,2,-5), v1=(3,2,-5), v2=(2,2,-8)))
raytracer.scene.append(Triangle(material=glass, v0=(-1,0,-5), v1=(-3,0,-5), v2=(-2,4,-8)))
raytracer.scene.append(Triangle(material=diamon, v0=(-1,-2,-5), v1=(1,-2,-5), v2=(2,1,-8))) """



#Lights
raytracer.lights.append(AmbientLight(0.9))


isRunning = True
while(isRunning):
    for event in pg.event.get():
        if event.type == pg.QUIT:
            isRunning = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                isRunning = False
            elif event.key == pg.K_s:
                pg.image.save(screen, "image.bmp")
    raytracer.rtClear()
    raytracer.rtRender()
    pg.display.flip()



pg.quit()
