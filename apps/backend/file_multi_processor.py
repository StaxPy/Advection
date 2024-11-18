import customtkinter as ctk
from shared.variables import *
import multiprocessing
import backend.file_processor as fp






class MultiProcessor_Progress(ctk.CTkToplevel):
    def __init__(self, TkApp, export_button, modifiers):
        super().__init__(TkApp)
        self.TkApp = TkApp
        self.export_button = export_button
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
        self.cancel_button = ctk.CTkButton(self.frame, text="Cancel", command=self.destroy,**Styles.normal_button_style)
        self.open_output_button = ctk.CTkButton(self.frame, text="Open Output Folder", command=self.open_output_folder,**Styles.normal_button_style)

        self.progress_bar.pack()
        self.label.pack()
        self.cancel_button.pack()

        self.progress = 0
        self.progress_count = 0

        sequence_files = InputData.sequence_files
        self.output_path = OutputData.path
        start = int(SequenceData.start.get())
        end = int(SequenceData.end.get())
        args_list = []


        

        for i in range(start, end+1):
            input_file_path = sequence_files[i]['path']
            output_name = str(i)
            args_list.append((input_file_path,self.output_path,output_name,modifiers))
            # fp.write_mcfunction_file(input_file_path,OutputData.path,output_name)

        # self.start_button.config(state=tk.DISABLED) #TODO
        self.progress_maximum = len(args_list)

        # with multiprocessing.Pool() as pool:
        #     # Map the write_mcfunction_file_wrapper function to the arguments
        #     pool.map(write_mcfunction_file_wrapper, args_list)

            # Create a pool of worker processes
        self.pool = multiprocessing.Pool()
        self.results = [self.pool.apply_async(fp.write_mcfunction_file, args) for args in args_list]

        self.check_results()
        
        # self.update_progress()


    def stop(self):
        # self.TkApp.attributes("-alpha", 1)
        self.export_button.configure(state="normal")
        # self.pool.close()
        # self.pool.join()
        # super().destroy()
        self.destroy()


    def click_close(self):
        if self.allow_closing:
            self.stop()



    def update_progress(self,result):
        if sv.DEBUG == True:
            print(result)
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
            self.interface_finished()

    def interface_finished(self):
        self.allow_closing = True
        self.progress_bar.forget()
        self.cancel_button.forget()
        self.label.configure(text=f"Sucessfully exported {self.progress_count} files!")
        self.open_output_button.pack(pady=10)

    def open_output_folder(self):
        import os
        if os.name == 'nt':  # Windows
            os.startfile(self.output_path)
        elif os.name == 'posix':  # macOS or Linux
            import subprocess
            subprocess.run(['open', '-R', self.output_path])
        # super.destroy()
        self.destroy()
            