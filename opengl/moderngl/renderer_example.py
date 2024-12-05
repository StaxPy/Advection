import moderngl


class HelloWorld2D:
    def __init__(self, ctx, reserve='4MB'):
        """
        Create a 2D rendering object.

        :param ctx: moderngl.Context
        :param reserve: Amount of memory to reserve for the vertex buffer. Default is '4MB'.
        """
        self.ctx = ctx
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330

                uniform vec2 Pan;

                in vec2 in_vert;
                in vec4 in_color;

                out vec4 v_color;   

                void main() {
                    v_color = in_color;
                    gl_Position = vec4(in_vert - Pan, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330

                in vec4 v_color;

                out vec4 f_color;

                void main() {
                    f_color = v_color;
                }
            ''',
        )

        self.vbo = ctx.buffer(reserve='4MB', dynamic=True)
        self.vao = ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_color')

    def pan(self, pos):
        self.prog['Pan'].value = pos

    def clear(self, color=(0, 0, 0, 0)):
        self.ctx.clear(*color)

    def plot(self, points, type='line'):
        """
        Renders a set of 2D points using the specified drawing type.

        :param points: A numpy array of 2D points to be plotted.
        :param type: The type of plot to render. Options are 'line' for a line strip or 'points' for individual points.
        """

        data = points.astype('f4').tobytes()
        self.vbo.orphan()
        self.vbo.write(data)
        if type == 'line':
            self.ctx.line_width = 1.0
            self.vao.render(moderngl.LINE_STRIP, vertices=len(data) // 24)
        if type == 'points':
            self.ctx.point_size = 3.0
            self.vao.render(moderngl.POINTS, vertices=len(data) // 24)


class PanTool:
    def __init__(self):
        self.total_x = 0.0
        self.total_y = 0.0
        self.start_x = 0.0
        self.start_y = 0.0
        self.delta_x = 0.0
        self.delta_y = 0.0
        self.drag = False

    def start_drag(self, x, y):
        self.start_x = x
        self.start_y = y
        self.drag = True

    def dragging(self, x, y):
        if self.drag:
            self.delta_x = (x - self.start_x) * 2.0
            self.delta_y = (y - self.start_y) * 2.0

    def stop_drag(self, x, y):
        if self.drag:
            self.dragging(x, y)
            self.total_x -= self.delta_x
            self.total_y += self.delta_y
            self.delta_x = 0.0
            self.delta_y = 0.0
            self.drag = False

    @property
    def value(self):
        return (self.total_x - self.delta_x, self.total_y + self.delta_y)