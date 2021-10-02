import taichi as ti
import numpy as np

ti.init()


@ti.data_oriented
class grid:
    def __init__(self, number1, number2, width) -> None:
        self.number1 = number1
        self.number2 = number2
        self.width = width
        self.start = ti.Vector.field(2, ti.f32, shape=number1 + number2 - 2)
        self.end = ti.Vector.field(2, ti.f32, shape=number1 + number2 - 2)
        self.grid_1 = 1 / number1
        self.grid_2 = 1 / number2

    def show(self, gui, radius=2):
        gui.lines(self.start.to_numpy(), self.end.to_numpy(), radius=radius, color=0xffffff)
        gui.line([0, 0.5], [1, 0.5], color=0xfbfc1a)
        gui.line([0.5, 0], [0.5, 1], color=0xfbfc1a)

    @ti.kernel
    def init_grid(self):
        for i in range(self.number1 - 1):
            self.start[i][1] = 0
            self.start[i][0] = self.grid_1 + i * self.grid_1
            self.end[i][1] = 1
            self.end[i][0] = self.grid_1 + i * self.grid_1
        for i in range(self.number1 - 1, self.number1 + self.number2 - 2):
            self.start[i][0] = 0
            self.start[i][1] = self.grid_2 + (i - self.number2 + 1) * self.grid_2
            self.end[i][0] = 1
            self.end[i][1] = self.grid_2 + (i - self.number2 + 1) * self.grid_2


@ti.data_oriented
class hole:
    def __init__(self, number1, number2) -> None:
        self.number1 = number1
        self.number2 = number2
        self.grid_1 = 1 / number1
        self.grid_2 = 1 / number2
        self.hole_ = ti.field(ti.i32, shape=(self.number1, self.number2))
        self.hole_.from_numpy(np.zeros(dtype=int, shape=(self.number1, self.number2)))

    def show(self, gui):
        for i, j in ti.ndrange(self.number1, self.number2):
            if self.hole_[i, j]:
                gui.triangle([i * self.grid_1, j * self.grid_2], [i * self.grid_1 + self.grid_1, j * self.grid_2],
                             [i * self.grid_1 + self.grid_1, j * self.grid_2 + self.grid_2], color=0xffffff)
                gui.triangle([i * self.grid_1, j * self.grid_2], [i * self.grid_1, j * self.grid_2 + self.grid_2],
                             [i * self.grid_1 + self.grid_1, j * self.grid_2 + self.grid_2], color=0xffffff)

    def clear(self):
        self.hole_.from_numpy(np.zeros(dtype=int, shape=(self.number1, self.number2)))


@ti.data_oriented
class screen:
    def __init__(self, number, originnum1, originnum2, R, division=10) -> None:
        self.R = R
        self.R_ = 1 / R
        self.number = number
        self.originnum1 = originnum1
        self.originnum2 = originnum2
        self.division = 1 / division
        self.screen_ = ti.field(ti.f32, shape=(self.number, self.number))
        self.comp = ti.Vector.field(2, ti.f32, shape=(self.number, self.number))
        self.comp.from_numpy(np.zeros(shape=(self.number, self.number, 2)))

    @ti.kernel
    def image(self, hole_: ti.template()):
        for i, j in ti.ndrange(self.number, self.number):
            X, Y = (i - self.number * 0.5 + 0.5) * 5e-4, (j - self.number * 0.5 + 0.5) * 5e-4
            for k, l in ti.ndrange(self.originnum1, self.originnum2):
                if hole_[k, l]:
                    x, y = (k - self.originnum1 * 0.5) * 1e-6, (l - self.originnum2 * 0.5) * 1e-6
                    self.comp[i, j][0] += ti.cos((Y * y + X * x) * self.R_ * 6.18 * 1e7) * self.division
                    self.comp[i, j][1] += ti.sin((Y * y + X * x) * self.R_ * 6.18 * 1e7) * self.division
            self.screen_[i, j] = (self.comp[i, j].norm()) ** 2

    def clear(self):
        self.comp.from_numpy(np.zeros(shape=(self.number, self.number, 2)))


@ti.data_oriented
class screen_single(screen):
    def __init__(self, number, slices1=50,slices2=1,R=2, division=2) -> None:
        super().__init__(number, slices1, slices2, R, division)
        self.slices1=slices1
        self.slices2=slices2
        pass

    @ti.kernel
    def image(self, hole_: ti.template()):
        for i, j in ti.ndrange(self.number, self.number):
            X, Y = (i - self.number * 0.5 + 0.5) * 5e-4, (j - self.number * 0.5 + 0.5) * 5e-4
            for k in range(self.slices1):
                x = (k - self.slices1 * 0.5) * 1e-6
                r_2 = (X - x) ** 2 + Y ** 2 + self.R ** 2
                self.comp[i, j][0] += ti.cos(X * x * self.R_ * 6.18 * 3e6)/r_2*self.division
                self.comp[i, j][1] += ti.sin(X * x * self.R_ * 6.18 * 3e6)/r_2*self.division
            self.screen_[i, j] = (self.comp[i, j].norm()) ** 2

@ti.data_oriented
class screen_lines(screen):
    def __init__(self, number, slices1=50, slices2=1,factor=10,lines=2, R=2, division=8) -> None:
        super().__init__(number, slices1, slices2, R, division)
        self.slices1 = slices1
        self.slices2 = slices2
        self.factor=factor
        self.lines=lines
        pass

    @ti.kernel
    def image(self, hole_: ti.template()):
        for i, j in ti.ndrange(self.number, self.number):
            X, Y = (i - self.number * 0.5 + 0.5) * 5e-4, (j - self.number * 0.5 + 0.5) * 5e-4
            for m in range(self.lines):
                for k in range(self.lines*self.slices1+(self.lines-1)*self.factor*self.slices1):
                    if k%(self.slices1*(self.factor+1))//self.slices1==0:
                        x = (k - (self.lines*self.slices1+(self.lines-1)*self.factor*self.slices1) * 0.5) * 1e-6
                        r_2 = (X - x) ** 2 + Y ** 2 + self.R ** 2
                        self.comp[i, j][0] += ti.cos(X * x * self.R_ * 6.18 * 3e6) / r_2 * self.division
                        self.comp[i, j][1] += ti.sin(X * x * self.R_ * 6.18 * 3e6) / r_2 * self.division
                self.screen_[i, j] += (self.comp[i, j].norm()) ** 2
                self.comp[i,j]=[0,0]

    def clear(self):
        self.comp.from_numpy(np.zeros(shape=(self.number, self.number, 2)))
        self.screen_.from_numpy(np.zeros(shape=(self.number, self.number)))
