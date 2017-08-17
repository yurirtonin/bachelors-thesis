from tkinter import *
from tkinter import ttk

root = Tk()
root.geometry("500x500")

top_frame = Frame(root, width=100, height=100,bg="red")
top_frame.grid(row=0,columnspan=2)

horizontal_line = ttk.Separator(root, orient=HORIZONTAL)
horizontal_line.grid(row=1,sticky="ew")

left_frame = Frame(root, width=200, height=50,bg="blue")
left_frame.grid(row=2,column=0)

right_frame = Frame(root, bg="green", width=100, height=100)
right_frame.grid(row=2,column=1)

w = Label(top_frame, text="Red Sun", bg="red", fg="white")
w.pack(pady=10, anchor="w")

w = Label(right_frame, text="Green Grass", bg="green", fg="black")
w.pack(fill=X, padx=10)

w = Label(left_frame, text="Blue Sky", bg="blue", fg="white")
w.pack(fill=X, padx=10)

mainloop()
