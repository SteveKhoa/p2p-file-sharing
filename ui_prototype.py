import tkinter

END = "end"

def Publish_Command():
    file_name = publish_input_entry.get()
    publish_input_entry.delete(0, END)
    print("Published", file_name)
    
def Fetch_Command():
    file_name = fetch_input_entry.get()
    fetch_input_entry.delete(0, END)
    print("Fetched", file_name)
    pass

def Stop_Command():  
    main_window.destroy()
    pass

main_window = tkinter.Tk()

main_window.title('UI Prototype')

tkinter.Label(main_window, text='File to Publish').grid(row=0, column=0)

publish_input_entry = tkinter.Entry(main_window)
publish_input_entry.grid(row=0, column=1)

button = tkinter.Button(main_window, text='Publish', width=20, command=Publish_Command).grid(row=0, column=2)

tkinter.Label(main_window, text='File to Fetch').grid(row=1, column=0)

fetch_input_entry = tkinter.Entry(main_window)
fetch_input_entry.grid(row=1, column=1)

button = tkinter.Button(main_window, text='Fetch', width=20, command=Fetch_Command).grid(row=1, column=2)

button = tkinter.Button(main_window, text='Stop', width=20, command=Stop_Command).grid(row=3, column=0)

main_window.minsize(600, 300)

main_window.mainloop()

