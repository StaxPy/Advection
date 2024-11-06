









if __name__ == "__main__":

    def loop():


        PygameData.PygameRenderer.loop()
        
        interface.UI.TkApp.update_idletasks()
        interface.UI.TkApp.after(15, loop)
    

    # (interface is initialized during import)
    import frontend.preview2 as preview
    import frontend.interface2 as interface
    from shared.variables import *
    PygameData.PygameRenderer = preview.PygameRender(sv.WIDTH/2, sv.HEIGHT/5*4, interface.UI.preview_frame)
    
    # PygameRenderer.render_new_frame()
    loop()
    interface.UI.TkApp.mainloop()

















###

