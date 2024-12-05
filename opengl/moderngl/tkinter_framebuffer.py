from PIL import Image, ImageTk


class FramebufferImage(ImageTk.PhotoImage):
    def __init__(self, master, ctx, size):
        """
        Create a FramebufferImage object.

        Parameters
        ----------
        master : tkinter widget
            The parent widget for the image.
        ctx : moderngl.Context
            The OpenGL context to use.
        size : tuple of two integers
            The size of the image.

        Returns
        -------
        A new FramebufferImage object.
        """
        super(FramebufferImage, self).__init__(Image.new('RGB', size, (0, 0, 0)))
        self.ctx = ctx
        self.fbo = self.ctx.simple_framebuffer(size)
        self.scope = self.ctx.scope(self.fbo)

    def __enter__(self):
        """
        Enters the context for the framebuffer image, activating the OpenGL scope.

        This method is called when entering a `with` block, allowing for rendering
        operations to be performed within the scope of the framebuffer.
        """

        self.scope.__enter__()

    def __exit__(self, *args):
        """
        Exits the context for the framebuffer image, deactivating the OpenGL scope.

        This method is called when exiting a `with` block, ensuring that any
        resources are properly released. It also updates the image by reading
        the contents of the framebuffer and pasting it into the Tkinter image.
        """

        self.scope.__exit__(*args)
        self.paste(Image.frombytes('RGB', self.fbo.size, self.fbo.read(), 'raw', 'RGB', 0, -1))