import tkinter as tk 
import subprocess

window = tk.Tk()
#set window label
main_window_label = tk.Label(text = "Motion tracker GUI",
                            #background = "red", 
                            #forground = "green"
                             ).pack()

class app():
    def __init__(self, window):
        self.states = ["Idle", "Listening", "Analyzing", "Graphing"]
        self.current_state = self.states[0] #start at 0
        self.listen_button_cf = False
        self.graph_button_cf = False
        self.analysis_button_cf = False
        self.port = ''
        self.window = window

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

    #def set_on_click(self, action):
    #    if(action == "listen"):
    #        self.listen_button_cf = True
    #        self.graph_button_cf, self.analysis_button_cf = False, False
    #        self.update_state(state_index = 1)
    #    elif(action == "graph"):
    #        self.graph_button_cf = True
    #        self.listen_button_cf, self.analysis_button_cf = False, False
    #        self.update_state(state_index = 3)
    #    elif(action == "analyze"):
    #        self.analysis_button_cf = True
    #        self.graph_button_cf, self.listen_button_cf = False, False
    #        self.update_state(state_index = 2)
    #    self.what_state()

    def listen_on_click(self):
        self.update_state(state_index = 1)
    def analyze_on_click(self):
        self.update_state(state_index = 2)
    def graph_on_click(self):
        self.update_state(state_index = 3)
    
    def get_ports(self):
        raw_cmd = subprocess.check_output("netstat -a -n -p tcp -o", shell=True)
        raw_cmd = raw_cmd.decode("utf-8")
        
        all_ports = ""
        return all_ports

    def viewports_on_click(self):
        output = subprocess.check_output("netstat -a -n -p tcp -o", shell=True)
        output = output.decode("utf-8")
        #print(output.split('\n'))
        textBox = tk.Text(self.window, height = 50, width = 16)
        textBox.place(x= 5, y=90)
        #smth = "10.0.0.20:64297\n10.0.0.20:64298\n10.0.0.20:64299"
        output = self.get_ports()
        textBox.insert("end-1c", output)
        #textBox.insert("end-1c", smth)


    def what_state(self) -> None:
        print(self.current_state)

#instance of application. 
application = app(window)

#make window fixed size
window.geometry("800x600")
window.resizable(0,0)

#creating the buttons
listen_button = tk.Button(window, text = "Listen on Port", command = application.listen_on_click, cursor="hand2")
viewports_button = tk.Button(window, text = "View available ports", command = application.viewports_on_click, cursor="hand2")
graph_button = tk.Button(window, text = "Graph results",   command = application.graph_on_click, cursor="hand2")
analysis_button = tk.Button(window, text = "Run analysis", command = application.analyze_on_click, cursor="hand2")

listen_button.place(x= 125,y= 50)
graph_button.place(x= 215,y= 50)
analysis_button.place(x= 300,y= 50)
viewports_button.place(x= 5,y= 50)

window.mainloop()
