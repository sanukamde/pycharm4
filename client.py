import socket
import json
from tkinter import *
import matplotlib.pyplot as plt


class Client:
    def __init__(self):
        self.countries = []
        self.host = socket.gethostname()
        self.port = 9999
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

    def request_initial_data(self):
        self.client_socket.send(bytes("initialize", 'utf-8'))
        msg = self.client_socket.recv(1024)
        msg = json.loads(msg.decode("utf-8"))
        self.countries = msg.get("countries")

    def request_country_data(self, country):
        self.client_socket.send(bytes(country, 'utf-8'))
        msg = self.client_socket.recv(1024)
        msg = json.loads(msg.decode("utf-8"))
        y = []
        va = []
        for k, v in msg.items():
            y.append(k)
            va.append(v)
        graph_years = [int(i) for i in y]
        graph_years.reverse()
        graph_val = [int(i) for i in va]
        graph_val.reverse()
        return graph_years, graph_val

    def create_XY_plot(self, list1, list2, name):
        plt.plot(list1, list2, '-')
        plt.ylabel('Values - ' + name)
        plt.xlabel('Years - ' + name)
        plt.style.use("seaborn-dark-palette")
        plt.locator_params(axis="x", nbins=10)
        plt.tight_layout()
        plt.grid()
        plt.show()


cl = Client()
cl.request_initial_data()

root = Tk()
root.geometry("300x200")

variable = StringVar(root)
variable.set(cl.countries[42])

y = Label(root, text="Choose a country to view:")
w = OptionMenu(root, variable, *cl.countries)
y.pack()
w.pack()

def ok():
    print("You chose: " + variable.get())
    list_tuple = cl.request_country_data(variable.get())
    cl.create_XY_plot(list_tuple[0], list_tuple[1], variable.get())

button = Button(root, text="OK", command=ok)
button.pack()

Button(root, text="Quit", command=quit).pack()
root.mainloop()
