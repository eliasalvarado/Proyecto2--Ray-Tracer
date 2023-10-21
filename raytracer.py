import pygame as pg
from pygame.locals import *
from rt import Raytracer, Model
from figures import *
from materials import *
from lights import *

width = 720
height = 512

pg.init()

screen = pg.display.set_mode((width, height), pg.DOUBLEBUF | pg.HWACCEL | pg.HWSURFACE)
screen.set_alpha(None)

# FONDO
raytracer = Raytracer(screen=screen)
raytracer.envMap = pg.image.load("fondo3.png")

# MATERIALES
prueba = Material(diffuse=(0, 0, 0))
glass = Material(diffuse=(0.9, 0.9, 0.9), specular=64, ks=0.2, ior=1.5, matType=REFLECTIVE)
diamon = Material(diffuse=(0.7, 0.7, 0.9), specular=64, ks=0.2, ior=2.417, matType=TRANSPARENT)
tablero = pg.image.load("tablero.jpg")
tablero = Material(texture=tablero)
roca = pg.image.load("roca.png")
roca = Material(texture=roca)
smothStone = pg.image.load("smothStone.png")
smothStone = Material(texture=smothStone)

""" # OBJ que no funciona xd
dardo = Model(filename = "gilmi.obj", material=orange, position=(0,0,-20))
raytracer.loadModel(model=dardo) """

#Tablero de ajedrez - Un cubo AABB
raytracer.scene.append(AABB(position=(0,-5,-10), size=(8,0.4,8), material=tablero))

#Pilares - 3 cilindros
raytracer.scene.append(Cylinder(material=roca, v0=(-6,0,-10), v1=(-6,10,-10), radius=0.5))
raytracer.scene.append(Cylinder(material=roca, v0=(-3.5,1,-10), v1=(-3.5,5,-10), radius=0.5))
raytracer.scene.append(Cylinder(material=roca, v0=(-2,2,-10), v1=(-2,4,-10), radius=0.3))

#Techos - 4 cubos AABB
raytracer.scene.append(AABB(position=(-4,5,-10), size=(2,0.5,4), material=smothStone))
raytracer.scene.append(AABB(position=(-3,4.5,-13), size=(2,0.5,4), material=smothStone))
raytracer.scene.append(AABB(position=(-2.5,4,-16), size=(2,0.5,4), material=smothStone))
raytracer.scene.append(AABB(position=(-2,3.5,-19), size=(2,0.5,4), material=smothStone))
raytracer.scene.append(AABB(position=(-1.5,3,-22), size=(2,0.5,4), material=smothStone))

#Agua - 1 plano
raytracer.scene.append(Plane(position=(0,-20,0), normal=(0,1,0), material=glass))

#Triángulo de fondo - 1 Triángulo
raytracer.scene.append(Triangle(material=diamon, v0=(0,0.2,-5), v1=(3.5,0.2,-5), v2=(2.5,4,-8)))





#Lights
raytracer.lights.append(AmbientLight(0.9))
raytracer.lights.append(DirectionalLight(direction=(0,0,-1), intensity=0.7))
raytracer.lights.append(DirectionalLight(direction=(-1,0,-1), intensity=0.5, color=(1,0,0)))
raytracer.lights.append(DirectionalLight(direction=(1,0,-1), intensity=0.5, color=(0,0,1)))
raytracer.lights.append(PointLight(point=(0,-1,0), intensity=1, color=(0,1,0)))


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
