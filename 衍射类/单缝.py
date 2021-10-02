import taichi as ti
from 衍射类 import hole,screen_single

ti.init()

Gridnum=600
gridnum1=1
gridnum2=50
gui=ti.GUI("Screen",res=(Gridnum,Gridnum))

hole1=hole(gridnum1,gridnum2)
screen1=screen_single(Gridnum)

while True:
    screen1.image(hole1.hole_)
    gui.set_image(screen1.screen_)
    gui.show()
    screen1.clear()
