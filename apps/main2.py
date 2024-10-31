import frontend.preview2 as preview
import frontend.interface2 as interface
import shared.variables as sv





def loop():


    PreviewApp.loop()
    
    interface.TkApp.update_idletasks()
    interface.TkApp.after(30, loop)
    



if __name__ == "__main__":
    interface.initialize_interface()
    PreviewApp = preview.PygameRender(sv.WIDTH/2, sv.HEIGHT, interface.preview_frame)
    loop()
    interface.run_main_loop()

















###

