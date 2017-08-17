import tkinter as tk

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # <create the rest of your GUI here>





if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()




# class Navbar(tk.Frame): ...
# class Toolbar(tk.Frame): ...
# class Statusbar(tk.Frame): ...
# class Main(tk.Frame): ...
# class MainApplication(tk.Frame):
#     def __init__(self, parent, *args, **kwargs):
#         tk.Frame.__init__(self, parent, *args, **kwargs)
#         self.statusbar = Statusbar(self, ...)
#         self.toolbar = Toolbar(self, ...)
#         self.navbar = Navbar(self, ...)
#         self.main = Main(self, ...)
#
#         self.statusbar.pack(side="bottom", fill="x")
#         self.toolbar.pack(side="top", fill="x")
#         self.navbar.pack(side="left", fill="y")
#         self.main.pack(side="right", fill="both", expand=True)