import tkinter as tk
from tkinter import *
import threading
import obspython as obs

# --------------------------------------------------

window = None

window_start = False
first_event = True  # Track if we've processed first recording event

class Application(tk.Frame):              
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.config(bg="#1a1a1a")   
        self.pack()                
        
        # Position at top-right of screen
        screen_width = self.master.winfo_screenwidth()
        self.master.geometry(f'180x40+{screen_width-190}+10')
        
        self.master.attributes('-alpha', 0.0) # Start hidden
        self.master.configure(bg='#1a1a1a') # Dark background
        self.master.overrideredirect(1) # Borderless window
        self.master.attributes('-topmost', True) # Always on top

        self.is_animating = False
        self.last_state = None

        global canvas
        canvas = Canvas(self, height=25, width=30, bg='#1a1a1a', highlightthickness=0)
        canvas.create_oval(21, 21, 2, 3, outline='#333333', fill='#333333')
        canvas.create_oval(20, 20, 4, 5, fill='#00a800', outline='') # Green REC indicator
        canvas.grid(row=0, column=0, padx=(10,5), pady=5)

        global label
        label = Label(self, text="Recording Started", font=('Helvetica', 10))
        label.grid(row=0, column=1, padx=(0,10), pady=5)
        label.config(bg="#1a1a1a", fg="white")


    def fade_in(self):
        current = float(self.master.attributes('-alpha'))
        if current < 0.9:
            current += 0.1
            self.master.attributes('-alpha', current)
            self.after(30, self.fade_in)
        else:
            self.after(3000, self.fade_out) # Stay visible for 3 seconds

    def fade_out(self):
        current = float(self.master.attributes('-alpha'))
        if current > 0.1:
            current -= 0.1
            self.master.attributes('-alpha', current)
            self.after(30, self.fade_out)
        else:
            self.is_animating = False


    def check_loop_status(self):
        global window_start, label, canvas, first_event
        
        if not first_event and window_start != self.last_state and not self.is_animating:
            self.is_animating = True
            self.last_state = window_start
            
            if window_start:
                label.config(text="Recording Started")
                canvas.delete("all")
                canvas.create_oval(21, 21, 2, 3, outline='#333333', fill='#333333')
                canvas.create_oval(20, 20, 4, 5, fill='#00a800', outline='')
            else:
                label.config(text="Recording Stopped") 
                canvas.delete("all")
                canvas.create_oval(21, 21, 2, 3, outline='#333333', fill='#333333')
                canvas.create_oval(20, 20, 4, 5, fill='#ff0000', outline='')
            
            self.fade_in()
        
        self.after(100, self.check_loop_status)
    
 
def runtk():  # runs in background thread
    app = Application()                        
    app.master.title('OBS Recording Notification')  
    app.check_loop_status()
    app.mainloop()
        
    
thd = threading.Thread(target=runtk)   # gui thread
thd.daemon = True  # background thread will exit if main thread exits



# ----------------------------   OBS script    ------------------------------------------------------------

class Data:
    OutputDir = None

# this function responds to events inside OBS
def frontend_event_handler(data):
    global window_start, first_event

    if data == obs.OBS_FRONTEND_EVENT_FINISHED_LOADING:
        if not thd.is_alive():
            thd.start()
        return

    if data == obs.OBS_FRONTEND_EVENT_RECORDING_STARTING:
        window_start = True
        first_event = False

    if data == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED:
        window_start = False
        first_event = False



def script_description():
    return ("OBS Shadowplay-style Notification\n\n"
            
            "Shows a brief notification when recording starts/stops\n\n"
            "Restart OBS after adding the script\n\n"
            "Requires Python 3.6.8 with Tkinter")



obs.obs_frontend_add_event_callback(frontend_event_handler)
