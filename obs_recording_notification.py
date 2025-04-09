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
        self.master.geometry(f'200x50+{screen_width-210}+20')
        
        self.master.attributes('-alpha', 0.0) # Start hidden
        self.master.configure(bg='#0f0f0f') # Darker background
        self.master.overrideredirect(1) # Borderless window
        self.master.attributes('-topmost', True) # Always on top

        # Add rounded corners effect
        self.master.attributes('-transparentcolor', '#0f0f0f')
        self.config(bg='#0f0f0f')

        self.is_animating = False
        self.last_state = None

        # Modern container frame with subtle border
        container = Frame(self, bg='#252525', bd=0, highlightthickness=1, 
                         highlightbackground='#404040', highlightcolor='#404040')
        container.pack(padx=5, pady=5, fill=BOTH, expand=True)

        global canvas
        canvas = Canvas(container, height=30, width=30, bg='#252525', highlightthickness=0)
        # Modern pulsing REC indicator with shadow
        canvas.create_oval(25, 25, 5, 5, outline='#000000', fill='#000000')
        canvas.create_oval(24, 24, 6, 6, outline='#404040', fill='#252525')
        canvas.create_oval(22, 22, 8, 8, fill='#ff3333') # Vibrant red
        canvas.grid(row=0, column=0, padx=(10,5), pady=5)

        global label
        label = Label(container, text="Recording Started", font=('Segoe UI', 11, 'bold'))
        label.grid(row=0, column=1, padx=(0,15), pady=5)
        label.config(bg="#252525", fg="#ffffff")


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
            # Clear notification state after fade out completes
            if hasattr(self, 'notification_type'):
                delattr(self, 'notification_type')
                delattr(self, 'notification_state')


    def check_loop_status(self):
        if not hasattr(self, 'notification_type') or self.is_animating:
            self.after(100, self.check_loop_status)
            return
            
        self.is_animating = True
        
        if self.notification_type == 'recording':
            if self.notification_state == 'started':
                label.config(text="Recording Started")
                canvas.delete("all")
                # Red recording indicator
                canvas.create_oval(25, 25, 5, 5, outline='#000000', fill='#000000')
                canvas.create_oval(24, 24, 6, 6, outline='#404040', fill='#252525')
                canvas.create_oval(22, 22, 8, 8, fill='#ff3333')
            else:  # saved
                label.config(text="Recording Saved")
                canvas.delete("all")
                # Green checkmark
                canvas.create_oval(25, 25, 5, 5, outline='#000000', fill='#000000')
                canvas.create_oval(24, 24, 6, 6, outline='#404040', fill='#252525')
                canvas.create_line(10, 15, 15, 20, fill='#00cc00', width=3)
                canvas.create_line(15, 20, 22, 10, fill='#00cc00', width=3)
        
        elif self.notification_type == 'replay':
            label.config(text="Replay Saved") 
            canvas.delete("all")
            # Blue replay indicator
            canvas.create_oval(25, 25, 5, 5, outline='#000000', fill='#000000')
            canvas.create_oval(24, 24, 6, 6, outline='#404040', fill='#252525')
            canvas.create_oval(22, 22, 8, 8, fill='#0099ff')
        
        self.fade_in()
        self.after(100, self.check_loop_status)
    
 
# Global reference to application instance
app_instance = None

def runtk():  # runs in background thread
    global app_instance
    app_instance = Application()                        
    app_instance.master.title('OBS Recording Notification')  
    app_instance.check_loop_status()
    app_instance.mainloop()
    app_instance = None  # Clear reference when window closes
        
    
thd = threading.Thread(target=runtk)   # gui thread
thd.daemon = True  # background thread will exit if main thread exits



# ----------------------------   OBS script    ------------------------------------------------------------

class Data:
    OutputDir = None

def frontend_event_handler(data):
    global window_start, first_event, app_instance

    if data == obs.OBS_FRONTEND_EVENT_FINISHED_LOADING:
        if not thd.is_alive():
            thd.start()
        return

    if not app_instance or not hasattr(app_instance, 'master') or not app_instance.master.winfo_exists():
        return

    if data == obs.OBS_FRONTEND_EVENT_RECORDING_STARTING:
        first_event = False
        app_instance.after(0, lambda: (
            setattr(app_instance, 'notification_type', 'recording'),
            setattr(app_instance, 'notification_state', 'started'),
            app_instance.check_loop_status()
        ))

    elif data == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED:
        first_event = False
        app_instance.after(0, lambda: (
            setattr(app_instance, 'notification_type', 'recording'),
            setattr(app_instance, 'notification_state', 'saved'),
            app_instance.check_loop_status()
        ))

    elif data == obs.OBS_FRONTEND_EVENT_REPLAY_BUFFER_SAVED:
        app_instance.after(0, lambda: (
            setattr(app_instance, 'notification_type', 'replay'),
            setattr(app_instance, 'notification_state', 'saved'),
            app_instance.check_loop_status()
        ))



def script_description():
    return ("OBS Shadowplay-style Notification\n\n"
            
            "Shows a brief notification when recording starts/stops\n\n"
            "Restart OBS after adding the script\n\n"
            "Requires Python 3.6.8 with Tkinter")



obs.obs_frontend_add_event_callback(frontend_event_handler)
