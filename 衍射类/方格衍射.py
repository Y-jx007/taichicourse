import taichi as ti
from 衍射类 import grid,screen,hole

ti.init()

Gridnum=600
gridnum=35
R=2
line_width=2
gui1 = ti.GUI("Hole", res=600)
gui2=ti.GUI("Screen",res=(Gridnum,Gridnum))

grid1=grid(gridnum,gridnum,line_width)
hole1=hole(gridnum,gridnum)
screen1=screen(Gridnum,gridnum,gridnum,R)

grid1.init_grid()
while True:
    grid1.show(gui1,radius=line_width)
    hole1.show(gui1)
    gui1.show()
    screen1.image(hole1.hole_)
    gui2.set_image(screen1.screen_)
    gui2.show()
    if gui1.get_event((ti.GUI.PRESS, ti.GUI.LMB)):
        o = gui1.get_cursor_pos()
        io, jo = int(o[0] * hole1.number1), int(o[1] * hole1.number2)
        change = hole1.hole_[io, jo]
        while True:
            h = gui1.get_cursor_pos()
            i, j = int(h[0] * hole1.number1), int(h[1] * hole1.number2)
            if hole1.hole_[i, j] == change:
                hole1.hole_[i, j] = not hole1.hole_[i, j]
            grid1.show(gui1, radius=line_width)
            hole1.show(gui1)
            gui1.show()
            if gui1.get_event((ti.GUI.RELEASE, ti.GUI.LMB)):
                break
    if gui1.is_pressed("c"):
        hole1.clear()
    screen1.clear()
