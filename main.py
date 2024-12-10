
if __name__ == "__main__":

    def loop():
        PygameRenderer.loop()
        
        interface.UI.TkApp.update_idletasks()
        interface.UI.TkApp.after(15, loop)

    

    # (interface is initialized during import)
    import src.frontend.interface as interface
    import src.frontend.renderer as preview

    from src.shared.variables import *
    PygameRenderer = preview.PygameRender(sv.WIDTH/2, sv.HEIGHT/5*4, interface.UI.preview_frame)
    PygameData.PygameRenderer = PygameRenderer

    # interface.UI.try_update_input('Testing_files/character_1.obj')
    # interface.UI.try_update_input('Testing_files/textures/Dan-shaded-noeyes.png',True)
    interface.UI.random_cloud()

    
    
    # PygameRenderer.render_new_frame()
    loop()
    interface.UI.TkApp.mainloop()


















