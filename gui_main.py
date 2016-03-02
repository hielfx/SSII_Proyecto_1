__author__ = 'Daniel Sánchez'

#encoding:utf-8

import tkinter as tk
import tkinter.messagebox
import main  # Own module
import chart_main  # Own module
import yaml
import os

#TODO: Graphic interface
#TODO: Automate tasks


def gui_main():

    global scan_directories, sd_count
    result = {}
    scan_directories = []
    sd_count = 1
    root = tk.Frame()
    root.pack(fill=tk.X)

    ###################################################
    ##########                               ##########
    ##########   Here starts the execution   ##########
    ##########                               ##########
    ###################################################


    # scan_directories
    sd_label = tk.Label(root, text="Add directory to scan")
    sd_label.pack(fill=tk.X)

    # New frame to the textbox and the button
    entry_panel = tk.Frame(root)
    entry_panel.pack()
    # Textbox
    sd_entry = tk.Entry(entry_panel, width=75)
    sd_entry.pack(side=tk.LEFT, padx=1, pady=1)

    scan_dir_panel = tk.Frame(root)
    scan_dir_panel.pack(fill=tk.X)
    # X scroll bar
    sd_list_xscroll = tk.Scrollbar(scan_dir_panel)
    sd_list_xscroll.pack(side=tk.RIGHT, fill=tk.Y)
    # Y scroll bar
    sd_list_yscroll = tk.Scrollbar(scan_dir_panel, orient=tk.HORIZONTAL)
    sd_list_yscroll.pack(side=tk.BOTTOM, fill=tk.X)
    # List of selected dirs to scan
    sd_list = tk.Listbox(scan_dir_panel, xscrollcommand=sd_list_xscroll.set, yscrollcommand=sd_list_yscroll.set)


    def add_scan_directory_callback():

        # We ge get the path stored in the text field
        scan_dir = str(os.path.normpath(sd_entry.get()))
        sd_list.insert(globals()['sd_count'], scan_dir)
        globals()['sd_count'] += 1
        # As we are going to insery the path in a yaml file, we need to scape the \ replacing them by \\
        globals()['scan_directories'].append(scan_dir.replace("\\", "\\\\"))

        # We clear the tetxt
        sd_entry.delete(0, len(sd_entry.get()))
        sd_entry.insert(0, "")

    sd_button = tk.Button(entry_panel, text="Add", command=add_scan_directory_callback, height=1, width=5)
    sd_button.pack(pady=1,padx=1)

    sd_list.pack(fill=tk.X, pady=1, padx=1)

    # ----------------------------------------

    root.mainloop()

if __name__ == "__main__":

    gui_main()

    # with open('result.yaml', 'w') as f:
    #     yaml.dump(test1, f, default_flow_style=False)