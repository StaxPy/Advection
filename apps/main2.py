import frontend.preview2 as preview
import frontend.interface2 as interface
from shared.variables import *





def loop():


    PygameSettings.PygameRenderer.loop()
    
    interface.UI.TkApp.update_idletasks()
    interface.UI.TkApp.after(15, loop)
    



if __name__ == "__main__":
    # (interface is initialized during import)
    PygameSettings.PygameRenderer = preview.PygameRender(sv.WIDTH/2, sv.HEIGHT/5*4, interface.UI.preview_frame)
    # PygameRenderer.render_new_frame()
    loop()
    interface.UI.TkApp.mainloop()

















###

