import taichi as ti
from 衍射类 import screen,hole

ti.init()

Gridnum=600
gridnum=50
R=2
gui=ti.GUI("Screen",res=(Gridnum,Gridnum))

hole1=hole(gridnum,gridnum)
screen1=screen(Gridnum,gridnum,gridnum,R,division=60)

@ti.kernel
def MakeCircle():
    for i,j in ti.ndrange(gridnum,gridnum):
        if (i-gridnum/2)**2+(j-gridnum/2)**2<=400:
            hole1.hole_[i,j]=1


MakeCircle()
while True:
    screen1.image(hole1.hole_)
    gui.set_image(screen1.screen_)
    gui.show()
    screen1.clear()
