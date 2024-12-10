import customtkinter as ctk
from src.shared.variables import *
import multiprocessing
import src.backend.file_processor as fp
from os import path as os_path
from os import startfile as os_startfile
from os import name as os_name






class Exporter_Progress(ctk.CTkToplevel):
    def __init__(self, TkApp, export_button, modifiers):
        super().__init__(TkApp)
        self.TkApp = TkApp
        self.grab_set()
        self.transient(self.TkApp)
        self.output_path = OutputData.path

        self.export_button = export_button
        self.export_button.configure(state="disabled")
        self.title("Progress")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.click_close)
        self.allow_closing = False

        # get the position of the main window
        x = TkApp.winfo_x() + (TkApp.winfo_width() - 250) // 2
        y = TkApp.winfo_y() + (TkApp.winfo_height() - 100) // 2

        self.geometry(f"+{x}+{y}")
        self.attributes("-topmost", True)
        self.configure(fg_color=Styles.almost_black)
        self.frame = ctk.CTkFrame(self,fg_color=Styles.almost_black)
        self.frame.pack(fill="both", expand=True,padx=30,pady=30)
        
        self.create_UI()

        self.launch(modifiers)
        

    def create_UI(self):
        # To implement in subclasses
        pass

    def launch(self,modifiers):
        # To implement in subclasses
        pass
    
    def stop(self):
        # To implement in subclasses
        pass


    def click_close(self):
        if self.allow_closing:
            self.stop()

    def finished_UI(self):
        # To implement in subclasses
        pass

    def open_output(self):
        if os_name == 'nt':  # Windows
            os_startfile(self.output_path)
        elif os_name == 'posix':  # macOS or Linux
            import subprocess
            subprocess.run(['open', '-R', self.output_path])
        # super.destroy()
        self.stop()
            
class Single_Exporter_Progress(Exporter_Progress):

    def create_UI(self):

        
        self.progress_bar = ctk.CTkProgressBar(self.frame,
            orientation="horizontal",
            width=200,
            height=50,
            corner_radius=0,
            mode="indeterminate",
            fg_color=Styles.almost_black,
            border_color=Styles.white,
            border_width=0,
            progress_color=Styles.special_color)
        
        self.label = ctk.CTkLabel(self.frame, text="Exporting...",text_color=Styles.white)
        self.cancel_button = ctk.CTkButton(self.frame, text="Cancel", command=self.stop,**Styles.normal_button_style)
        self.open_output_button = ctk.CTkButton(self.frame, text="Open Output Folder", command=self.open_output,**Styles.normal_button_style)

        self.progress_bar.pack()
        self.label.pack()
        self.cancel_button.pack()

    def launch(self,modifiers):
        
        try: # Try to get the output name from the current frame
            self.output_name = os_path.splitext(os_path.basename(InputData.sequence_files[PygameData.frame.get()]["path"]))[0].lower()
        except: # If no frames where detected, default to the input file name
            self.output_name = os_path.splitext(os_path.basename(InputData.path))[0].lower()

        fp.write_mcfunction_file(ParticlesCache.DataParticlesCloud,OutputData.path,self.output_name,modifiers)

        self.finished_UI()

    def finished_UI(self):
        self.allow_closing = True
        self.progress_bar.forget()
        self.cancel_button.forget()
        self.label.configure(text=f"File exported to {OutputData.path}\{self.output_name}.mcfunction !")
        self.open_output_button.pack(pady=10)

    def open_output(self):
        if os_name == 'nt':  # Windows
            os_startfile(self.output_path)
        elif os_name == 'posix':  # macOS or Linux
            import subprocess
            subprocess.run(['open', '-R', self.output_path])
        # super.destroy()
        self.stop()

    def stop(self):
        self.export_button.configure(state="normal")
        super().destroy()

class Sequence_Exporter_Progress(Exporter_Progress):

    def create_UI(self):


        self.progress_bar = ctk.CTkProgressBar(self.frame,
            orientation="horizontal",
            width=200,
            height=50,
            corner_radius=0,
            mode="determinate",
            fg_color=Styles.almost_black,
            border_color=Styles.white,
            border_width=0,
            progress_color=Styles.special_color)
                
        self.progress_bar.set(0.01)
        self.label = ctk.CTkLabel(self.frame, text="Progress: 1%",text_color=Styles.white)
        self.cancel_button = ctk.CTkButton(self.frame, text="Cancel", command=self.stop,**Styles.normal_button_style)
        self.open_output_button = ctk.CTkButton(self.frame, text="Open Output Folder", command=self.open_output,**Styles.normal_button_style)

        self.progress_bar.pack()
        self.label.pack()
        self.cancel_button.pack()

        self.progress = 0
        self.progress_count = 0

    def launch(self,modifiers):
        sequence_files = InputData.sequence_files
        start = int(SequenceData.start.get())
        end = int(SequenceData.end.get())
        args_list = []

        for i in range(start, end+1):
            input_file_path = sequence_files[i]['path']
            output_name = str(i)
            args_list.append((input_file_path,self.output_path,output_name,modifiers))
            # fp.write_mcfunction_file(input_file_path,OutputData.path,output_name)

        self.progress_maximum = len(args_list)

        # Create a pool of worker processes
        self.pool = multiprocessing.Pool()
        self.results = [self.pool.apply_async(fp.write_mcfunction_file, args) for args in args_list]

        self.check_results()

    def update_progress(self,result):
        self.progress_count += 1
        self.progress += 1/self.progress_maximum  # increment progress
        self.progress_bar.set(self.progress)
        self.label.configure(text=f"Progress: {round(self.progress*100)}% ({self.progress_count}/{self.progress_maximum})")

    def check_results(self):
        for result in self.results:
            if result.ready():
                self.update_progress(result.get())
                self.results.remove(result)
        if self.results:
            self.after(100, self.check_results)
        else:
            self.finished_UI()

    def finished_UI(self):
        self.allow_closing = True
        self.progress_bar.forget()
        self.cancel_button.forget()
        self.label.configure(text=f"Sucessfully exported {self.progress_count} files!")
        self.open_output_button.pack(pady=10)

    def stop(self):
        self.export_button.configure(state="normal")
        self.pool.terminate()
        super().destroy()