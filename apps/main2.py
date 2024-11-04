import frontend.preview2 as preview
import frontend.interface2 as interface
import shared.variables as sv





def loop():


    PygameRenderer.loop()
    
    interface.UI.TkApp.update_idletasks()
    interface.UI.TkApp.after(15, loop)
    



if __name__ == "__main__":
    interface.initialize_interface()
    interface.create_interface()
    PygameRenderer = preview.PygameRender(sv.WIDTH/2, sv.HEIGHT/5*4, interface.UI.preview_frame)
    loop()
    interface.run_main_loop()

















###

