__author__ = 'Daniel Sánchez'

#encoding:utf-8

import tkinter as tk
import tkinter.messagebox as msgbox
import main_algorithm  # Own module
import chart_main  # Own module
import yaml
import os
import platform


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
        with open(str(app_name)+'.yaml', 'w') as f:
            yaml.dump(result, f, default_flow_style=False)

        msgbox.showinfo("Configuration saved", "The configuration has been saved")

    global scan_directories, sd_count, config, ef_count, ee_count
    result = {}
    scan_directories = []
    sd_count = 1
    ef_count = 1
    ee_count = 1
    main = tk.Tk()
    main.title("HIDS GUI")
    app_name = "py_hids_app"
    root = tk.Frame(main)
    root.pack(fill=tk.X)

    def display_current(listbox, option):
        try:

            globals()['config'] = yaml.load(open(str(app_name) + ".yaml", 'r'))
            index = 1

            for row in list(set(globals()['config'][option])):
                listbox.insert(index, row.replace("\\\\","\\"))
                index += 1

                if option == "exclude_extensions":
                    _count = "ee_count"
                elif option == "excluded_files":
                    _count = "ef_count"
                else:
                    _count = "sd_count"
                globals()[_count] += 1
                globals()['config'][option].remove(row)
                # globals()['config']['scan_directories'].append(str(row.replace("\\", "\\\\")))
                globals()['config'][option].append(row)

        except yaml.YAMLError:
            return -1


    ###################################################
    ##########                               ##########
    ##########   Here starts the execution   ##########
    ##########                               ##########
    ###################################################


    # scan_directories
    sd_label = tk.Label(root, text="Add directory to scan (absolute path)")
    sd_label.pack(fill=tk.X)

    # New frame to the textbox and the button
    entry_panel = tk.Frame(root)
    entry_panel.pack()
    # Textbox
    sd_entry = tk.Entry(entry_panel, width=80)
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
    sd_list = tk.Listbox(scan_dir_panel, selectmode=tk.MULTIPLE, yscrollcommand=sd_list_yscroll.set, height=5)
    display_current(sd_list,"scan_directories")

    def remove_scan_dir_callback():  # Method to remove the items from the listbox and the scan_directories
        items = sd_list.curselection()
        for index in reversed(items):
            item = sd_list.get(index)
            sd_list.delete(index)
            split = item.split('\\')
            reconstruct = "\\\\".join(split)
            directories = globals()['config']['scan_directories']
            if reconstruct in directories:
                directories.remove(reconstruct)

    # Button to remove the selected paths to be scanned
    sd_list_remove_button = tk.Button(root, text="Remove selected directories", command=remove_scan_dir_callback)

    def add_scan_directory_callback():  # Method to add items fto the listbox and the scan_directories

        # We ge get the path stored in the text field
        scan_dir = str(os.path.normpath(sd_entry.get()))

        if scan_dir not in sd_list.get(0, tk.END):
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

    # exclude files
    ef_label = tk.Label(root, text="Add files to exclude while scanning (absolute path)")
    ef_label.pack(fill=tk.X)

    # New frame to the textbox and the button
    ef_entry_panel = tk.Frame(root)
    ef_entry_panel.pack()
    # Textbox
    ef_entry = tk.Entry(ef_entry_panel, width=80)
    ef_entry.pack(side=tk.LEFT, padx=1, pady=1)

    # current selected files to exclude
    exclude_file_panel = tk.Frame(root)
    exclude_file_panel.pack(fill=tk.X)

    ef_list_label = tk.Label(exclude_file_panel, text="Current selected files to exclude")
    ef_list_label.pack(fill=tk.X)

    # Y scroll bar
    ef_list_yscroll = tk.Scrollbar(exclude_file_panel)
    ef_list_yscroll.pack(side=tk.RIGHT, fill=tk.Y)
    # List of selected dirs to scan
    ef_list = tk.Listbox(exclude_file_panel, selectmode=tk.MULTIPLE, yscrollcommand=sd_list_yscroll.set, height=5)
    display_current(ef_list, "excluded_files")

    def remove_exclude_file_callback():  # Method to remove the items from the listbox and the scan_directories
        items = ef_list.curselection()
        for index in reversed(items):
            item = ef_list.get(index)
            ef_list.delete(index)
            split = item.split('\\')
            reconstruct = "\\\\".join(split)
            directories = globals()['config']['excluded_files']
            if reconstruct in directories:
                directories.remove(reconstruct)

    # Button to remove the selected files to be excluded
    ef_list_remove_button = tk.Button(root, text="Remove selected files", command=remove_exclude_file_callback)

    def add_exclude_file_callback():  # Method to add items fto the listbox and the excluded_files

        # We ge get the path stored in the text field
        exclude_file = str(os.path.normpath(ef_entry.get()))

        if exclude_file not in ef_list.get(0, tk.END):
            ef_list.insert(globals()['ef_count'], exclude_file)
            globals()['ef_count'] += 1
            # As we are going to insery the path in a yaml file, we need to scape the \ replacing them by \\
            globals()['config']['excluded_files'].append(str(exclude_file.replace("\\", "\\\\")))

            # We clear the tetxt
            ef_entry.delete(0, len(ef_entry.get()))
            ef_entry.insert(0, "")
        else:
            msgbox.showwarning("Already excluded", "The file '{0}' is already excluded".format(exclude_file))

    ef_button = tk.Button(ef_entry_panel, text="Exclude", command=add_exclude_file_callback, height=1, width=5)
    ef_button.pack(pady=1, padx=1)

    ef_list.pack(fill=tk.X, pady=1, padx=1)
    ef_list_remove_button.pack(pady=1, padx=1)

    # ----------------------------------------

     # exclude extensions
    ee_label = tk.Label(root, text="Add extensions to exclude (e.g.: .pdf)")
    ee_label.pack(fill=tk.X)

    # New frame to the textbox and the button
    ee_entry_panel = tk.Frame(root)
    ee_entry_panel.pack()
    # Textbox
    ee_entry = tk.Entry(ee_entry_panel, width=80)
    ee_entry.pack(side=tk.LEFT, padx=1, pady=1)

    # current selected files to exclude
    exclude_extension_panel = tk.Frame(root)
    exclude_extension_panel.pack(fill=tk.X)

    ee_list_label = tk.Label(exclude_extension_panel, text="Current selected files to exclude")
    ee_list_label.pack(fill=tk.X)

    # Y scroll bar
    ee_list_yscroll = tk.Scrollbar(exclude_extension_panel)
    ee_list_yscroll.pack(side=tk.RIGHT, fill=tk.Y)
    # List of selected dirs to scan
    ee_list = tk.Listbox(exclude_extension_panel, selectmode=tk.MULTIPLE, yscrollcommand=sd_list_yscroll.set, height=5)
    display_current(ee_list, "exclude_extensions")

    def remove_exclude_extension_callback():  # Method to remove the items from the listbox and the scan_directories
        items = ee_list.curselection()
        for index in items:
            item = ee_list.get(index)
            ee_list.delete(index)
            split = item.split('\\')
            reconstruct = "\\\\".join(split)
            directories = globals()['config']['exclude_extension']
            if reconstruct in directories:
                directories.remove(reconstruct)

    # Button to remove the selected files to be excluded
    ee_list_remove_button = tk.Button(root, text="Remove selected extensions", command=remove_exclude_extension_callback)

    def add_exclude_extension_callback():  # Method to add items to the listbox and the exclude_extensions

        # We ge get the path stored in the text field
        exclude_extension = str(os.path.normpath(ee_entry.get()))

        if exclude_extension not in ee_list.get(0, tk.END):
            ee_list.insert(globals()['ee_count'], exclude_extension)
            globals()['ee_count'] += 1
            # As we are going to insery the path in a yaml file, we need to scape the \ replacing them by \\
            globals()['config']['exclude_extension'].append(str(exclude_extension.replace("\\", "\\\\")))

            # We clear the text
            ee_entry.delete(0, len(ee_entry.get()))
            ee_entry.insert(0, "")
        else:
            msgbox.showwarning("Already excluded", "The extension '{0}' is already excluded".format(exclude_extension))

    ee_button = tk.Button(ee_entry_panel, text="Exclude", command=add_exclude_extension_callback, height=1, width=5)
    ee_button.pack(pady=1, padx=1)

    ee_list.pack(fill=tk.X, pady=1, padx=1)
    ee_list_remove_button.pack(pady=1, padx=1)

    # ----------------------------------------

    # Frame for the last buttons
    last_button_frame = tk.Frame(root)
    last_button_frame.pack(side=tk.BOTTOM)
    # Save button
    save_config_button = tk.Button(last_button_frame, text="Save current configuration", command=save_yaml)
    save_config_button.grid(row=0, column=0)
    # Display chart button
    display_current_chart = tk.Button(last_button_frame, text="Display current ratio chart", command=lambda: chart_main.main_chart(show=True))
    display_current_chart.grid(row=0, column=1)
    # Perform a scan now
    perform_scan = tk.Button(last_button_frame, text="Perform a scan now", command=lambda: main_algorithm.main_method(show=True))
    perform_scan.grid(row=0, column=2)

    def open_log_callback():
        try:
            if platform.system() == "Windows":
                os.system("start hids.log")
            elif platform.system() == "Linux":
                os.system("xdg-open hids.log")
            else:
                msgbox.showinfo("Could not open","The log file could not be opened in this {0} system".format(platform.system()))
        except:
            msgbox.showerror("Error","There was a problem opening the log file")

    # Open log file
    open_log = tk.Button(last_button_frame, text="Open log", command=open_log_callback)
    open_log.grid(row=0, column=3)

    root.mainloop()

if __name__ == "__main__":

    gui_main()