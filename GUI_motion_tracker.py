import tkinter as tk 
import subprocess
from json_decoder_v2 import *
from IMU_motion_tracker import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


window = tk.Tk()

class app():
    def __init__(self, window):
        self.states = ["Idle", "Listening", "Analyzing", "Graphing"]
        self.current_state = self.states[0] #start at 0
        self.listen_button_cf = False
        self.graph_button_cf = False
        self.analysis_button_cf = False
        self.port = ''
        self.window = window
        self.index = 0
        self.listen_button = tk.Button(self.window, text = "Listen on Port", command = self.listen_on_click, cursor="hand2")
        self.viewports_button = tk.Button(self.window, text = "View available ports", command = self.viewports_on_click, cursor="hand2")
        self.graph_button = tk.Button(self.window, text = "Graph results",   command = self.graph_on_click, cursor="hand2")
        self.analysis_button = tk.Button(self.window, text = "Run analysis", command = self.analyze_on_click, cursor="hand2")
        self.next_graph_button = tk.Button(self.window, text = "Next Graph", command = self.go_next_graph, cursor="hand2")
        self.main_window_label = tk.Label(text = "Motion tracker GUI").pack()
        self.port_input_label = tk.Label(text = "Selected Port")      
        self.port_input_box = tk.Text(self.window, height = 1, width = 16) 
        self.free_ports = []   
        self.graphs = []
        self.current_canvas = None
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_closing(self):
        self.window.destroy()
        self.window.quit()

    def get_port(self) -> str:
        return self.port
    
    def set_port(self, port) -> None:
        self.port = port

    def get_current_state(self) -> str:
        return self.current_state

    def update_state(self, state_index) -> None:
        if( state_index < 0 or state_index > 3):
            print(f"Invalid state index: {state_index}")
        else:
            print(f"State updated: {self.current_state} -> {self.states[state_index]}")
            self.current_state = self.states[state_index]
    
    def reset_state(self) -> None:
        self.current_state = self.states[0]

    def build_app(self):
        self.window.geometry("1200x600")
        self.window.resizable(0,0)
        self.listen_button.place(x= 325,y= 23)
        self.graph_button.place(x= 415,y= 23)
        self.analysis_button.place(x= 500,y= 23)
        self.viewports_button.place(x= 205,y= 23)
        self.port_input_label.place(x= 5, y=5)
        self.port_input_box.place(x= 5, y=23)   
        self.next_graph_button.place(x= 400, y = 550)

    def is_port_valid(self, input) -> bool:
        #true if port is valid
        #false if port is invalid
        port_name = str(input).strip()
        return port_name in self.free_ports
    
    def listen_on_click(self) -> None:
        if(self.is_port_valid(self.port_input_box.get(1.0,tk.END))):
            local_address = self.port_input_box.get(1.0,tk.END).split(":")[0]
            port_num = self.port_input_box.get(1.0,tk.END).split(":")[1]
            listen_json(IP = local_address, port_number = int(port_num))
            self.update_state(state_index = 1)
        else:
            print(f"Port {self.port_input_box.get(1.0,tk.END)} is invalid.")

    def analyze_on_click(self):
        self.graphs = graph_data() #call to IMU_motion_tracker logic
        self.update_state(state_index = 2)

    def graph_on_click(self):
        self.update_state(state_index = 3)
        fig = self.graphs[0]
        canvas = FigureCanvasTkAgg(fig, master=self.window)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().place(x=205,y=70)
        self.current_canvas = canvas  # Save the current canvas to be able to destroy it later

    def go_next_graph(self):
        if(self.index+1 > len(self.graphs)):
            next_index = 0
            self.index = 0 
        else:
            next_index = self.index + 1
            self.index += 1

        if hasattr(self, 'current_canvas'):
            self.current_canvas.get_tk_widget().destroy()  # Remove the current canvas widget
        fig = self.graphs[next_index]
        canvas = FigureCanvasTkAgg(fig, master=self.window)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().place(x=170, y=70)
        self.current_canvas = canvas  # Save the new canvas to be able to destroy it later
    
    def get_ports(self) -> list:
        raw_cmd = subprocess.check_output("netstat -a -n -p tcp -o", shell = True)
        raw_cmd = raw_cmd.decode("utf-8")
        available_ports = raw_cmd.split('\n')[4:]
        list_ports = [line.split()[1] for line in available_ports if line != "" and line.split()[3] == "LISTENING"]
        self.free_ports = list_ports
        return list_ports

    def viewports_on_click(self) -> None:
        textBox = tk.Text(self.window, height = 50, width = 16)
        textBox.place(x= 5, y=60)
        output = self.get_ports()
        for port in output:
            textBox.insert("end-1c", port+"\n")

    def what_state(self) -> None:
        print(self.current_state)

#instance of application. 
application = app(window)
application.build_app()
window.mainloop()
