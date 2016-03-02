__author__ = 'Daniel Sánchez'

#encoding:utf-8

import tkinter as tk
import tkinter.messagebox as msgbox
import main  # Own module
import chart_main  # Own module
import yaml
import os

#TODO: Graphic interface
#TODO: Automate tasks


def gui_main():

    def save_yaml():
        # We remove the duplicated ones
        scan_directories = sorted(list(set(globals()['config']['scan_directories'])))
        exclude_extensions = sorted(list(set(globals()['config']['exclude_extensions'])))
        excluded_files = sorted(list(set(globals()['config']['excluded_files'])))
        result = {}



        result['scan_directories'] = scan_directories
        result['exclude_extensions'] = exclude_extensions
        result['excluded_files'] = excluded_files
        with open('result.yaml', 'w') as f:
            yaml.dump(result, f, default_flow_style=False)

    global scan_directories, sd_count, config
    result = {}
    scan_directories = []
    sd_count = 1
    main = tk.Tk()
    main.title("HIDS GUI")
    app_name = "py_hids_app"
    root = tk.Frame(main)
    root.pack(fill=tk.X)

    def display_current_scandirs(listbox):
        try:

            globals()['config'] = yaml.load(open(str(app_name) + ".yaml", 'r'))
            index = 1

            for row in sorted(list(set(globals()['config']['scan_directories']))):
                listbox.insert(index, row)
                index += 1
                globals()['sd_count'] += 1
                globals()['config']['scan_directories'].remove(row)
                globals()['config']['scan_directories'].append(str(row.replace("\\", "\\\\")))

        except yaml.YAMLError:
            return -1

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
    sd_entry = tk.Entry(entry_panel, width=100)
    sd_entry.pack(side=tk.LEFT, padx=1, pady=1)

    # current selected dir to scan
    scan_dir_panel = tk.Frame(root)
    scan_dir_panel.pack(fill=tk.X)

    sd_list_label = tk.Label(scan_dir_panel, text="Current selected directories to scan")
    sd_list_label.pack(fill=tk.X)

    # Y scroll bar
    sd_list_yscroll = tk.Scrollbar(scan_dir_panel)
    sd_list_yscroll.pack(side=tk.RIGHT, fill=tk.Y)
    # List of selected dirs to scan
    sd_list = tk.Listbox(scan_dir_panel, selectmode=tk.MULTIPLE, yscrollcommand=sd_list_yscroll.set)
    display_current_scandirs(sd_list)

    def remove_scan_dir_callback():
        items = sd_list.curselection()
        for index in items:
            item = sd_list.get(index)
            sd_list.delete(index)
            split = item.split('\\')
            reconstruct = "\\\\".join(split)
            globals()['config']['scan_directories'].remove(reconstruct)

    sd_list_remove_button = tk.Button(root, text="Remove selected directories", command=remove_scan_dir_callback)

    def add_scan_directory_callback():

        # We ge get the path stored in the text field
        scan_dir = str(os.path.normpath(sd_entry.get()))

        if scan_dir not in globals()['config']['scan_directories']:
            sd_list.insert(globals()['sd_count'], scan_dir)
            globals()['sd_count'] += 1
            # As we are going to insery the path in a yaml file, we need to scape the \ replacing them by \\
            globals()['config']['scan_directories'].append(str(scan_dir.replace("\\", "\\\\")))

            # We clear the tetxt
            sd_entry.delete(0, len(sd_entry.get()))
            sd_entry.insert(0, "")
        else:
            msgbox.showwarning("Already selected", "The path '{0}' is already selected".format(scan_dir))

    sd_button = tk.Button(entry_panel, text="Add", command=add_scan_directory_callback, height=1, width=5)
    sd_button.pack(pady=1,padx=1)

    sd_list.pack(fill=tk.X, pady=1, padx=1)
    sd_list_remove_button.pack(pady=1, padx=1)

    # ----------------------------------------

    save_config_button = tk.Button(root, text="Save current configuration", command=save_yaml)

    save_config_button.pack(padx=1,pady=1)

    root.mainloop()

if __name__ == "__main__":

    gui_main()