from PIL import Image, ImageTk


class FramebufferImage(ImageTk.PhotoImage):
    def __init__(self, master, ctx, size):
        super(FramebufferImage, self).__init__(Image.new('RGB', size, (0, 0, 0)))
        self.ctx = ctx
        self.fbo = self.ctx.simple_framebuffer(size)
        self.scope = self.ctx.scope(self.fbo)

    def __enter__(self):
        self.scope.__enter__()

    def __exit__(self, *args):
        self.scope.__exit__(*args)
        self.paste(Image.frombytes('RGB', self.fbo.size, self.fbo.read(), 'raw', 'RGB', 0, -1))