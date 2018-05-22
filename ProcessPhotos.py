print('Loading Dependencies...')
from tkinter import *
from tkinter import ttk
import tkFileDialog, arcpy, os
from core import assc_photos as PhotoAnalysis
print('Configuring GUI...')
#turn off edit logging, speeds up edits greatly
arcpy.SetLogHistory(False)


def set_photo_folder():
	change_lbl(photo_folder_location,'')
	folder_name = tkFileDialog.askdirectory()
	change_lbl(photo_folder_location,folder_name)

def define_photo_workspace():
	#defines the workspace that the analysis will take place in
	change_lbl(photo_gdb,'')
	folder_name = tkFileDialog.askdirectory()
	change_lbl(photo_gdb,folder_name)
	print('Loading selected Collector GDB...')
	generate_photo_fcs(folder_name)

def change_lbl(labelvar,label):
	#changes a label variable
	labelvar.set(label)

def generate_photo_fcs(workspace):
	#generate a list of feature classes after defining the workspace
	try:
		#check if the fodler may actually be a GDB. This is a pretty weak check as
		#folders can end in .gdb but are not actually GDBs. hopefully, attempting
		#to do some of the following operations on an invalid folder will throw 
		#an error to trigger the except clause.
		if '.gdb' not in workspace:
			raise ValueError('Not a valid workspace.')
		arcpy.env.workspace = workspace
		fcs = []
		for fds in arcpy.ListDatasets('','feature') + ['']:
			for fc in arcpy.ListFeatureClasses('','',fds):
				fcs.append(os.path.join(fds, fc))
		
		tables = arcpy.ListTables()

		photo_table.set("")
		collector_fc.set("")
		photo_table_combobox['values'] = tables
		photo_table_combobox['state'] = "readonly"
		collector_fc_combobox['values'] = fcs
		collector_fc_combobox['state'] = "readonly"
		arcpy.env.workspace = ''
	except:
		change_lbl(photo_gdb,'INVALID WORKSPACE')
		print('Invalid GDB selected...')
		photo_table_combobox['values'] = []
		photo_table_combobox['state'] = "disabled"
		collector_fc_combobox['values'] = []
		collector_fc_combobox['state'] = "disabled"
		photo_table.set('')
		collector_fc.set('')
		arcpy.env.workspace = ''

def set_photo_table(*args):
	value = photo_table.get()
	photo_table.set(value)

def set_collector_fc(*args):
	value = collector_fc.get()
	collector_fc.set(value)

def photo_fc_loading(*args):
	photo_table.set('Loading GDB...')
	collector_fc.set('Loading GDB...')

def define_master_workspace():
	#defines the workspace that the analysis will take place in
	change_lbl(master_gdb,'')
	folder_name = tkFileDialog.askdirectory()
	change_lbl(master_gdb,folder_name)
	print('Loading selected Master GDB...')
	generate_master_fcs(folder_name)

def generate_master_fcs(workspace):
	#generate a list of feature classes after defining the workspace
	try:
		#check if the fodler may actually be a GDB. This is a pretty weak check as
		#folders can end in .gdb but are not actually GDBs. hopefully, attempting
		#to do some of the following operations on an invalid folder will throw 
		#an error to trigger the except clause.
		if '.gdb' not in workspace:
			raise ValueError('Not a valid workspace.')
		arcpy.env.workspace = workspace
		fcs = []
		for fds in arcpy.ListDatasets('','feature') + ['']:
			for fc in arcpy.ListFeatureClasses('','',fds):
				fcs.append(os.path.join(fds, fc))
		
		master_fc.set("")
		master_fc_combobox['values'] = fcs
		master_fc_combobox['state'] = "readonly"
		arcpy.env.workspace = ''
	except:
		change_lbl(master_gdb,'INVALID WORKSPACE')
		print('Invalid GDB selected...')
		master_fc_combobox['values'] = []
		master_fc_combobox['state'] = "disabled"
		master_fc.set('')
		arcpy.env.workspace = ''

def master_fc_loading(*args):
	master_fc.set('Loading GDB...')

def set_master_fc(*args):
	value = master_fc.get()
	master_fc.set(value)

def set_manufacturer(*args):
	value = manufacturervar.get()
	manufacturervar.set(value)

def set_processing(*args):
	if photos_processed.get() == 0:
		statusvar.set("Processing Photos - Do not press anything.")
		startButton['state'] = 'disabled'
	else:
		startButton['state'] = 'disabled'
		statusvar.set("Photos already processed.")

def start_analysis(*args):
	print("Processing Photos - Do not press anything.")
	try:	
		if not photos_processed.get() == 1:	
			pfl = photo_folder_location.get()
			photo_workspace = photo_gdb.get()
			pt = photo_table.get()
			cfc = collector_fc.get()
			master_workspace = master_gdb.get()
			mfc = master_fc.get()
			
			arcpy.env.workspace = photo_workspace
			photo_dictionary = PhotoAnalysis.build_photo_dict(pt,pfl)
			aud_uid_dict = PhotoAnalysis.build_aud_uid_dict(photo_dictionary, cfc)
			number_of_photo_fields = PhotoAnalysis.determine_number_of_photo_fields(aud_uid_dict)

			arcpy.env.workspace = master_workspace
			PhotoAnalysis.add_photo_fields(mfc,number_of_photo_fields)
			PhotoAnalysis.insert_photos_into_master(mfc,aud_uid_dict,number_of_photo_fields)
			
			statusvar.set("Photos processed successfully")
			photos_processed.set(1)
		else:
			statusvar.set("You clicked more than once, didn't you?")
	except Exception as e:
		raise
		statusvar.set("ERROR PROCESSING PHOTOS")
	
root = Tk()
root.title("Photo Processing")

mainframe = ttk.Frame(root, padding="25 25 25 25")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

#variables
photo_folder_location = StringVar()
photo_gdb = StringVar()
photo_table = StringVar()
collector_fc = StringVar()
master_gdb = StringVar()
master_fc = StringVar()

statusvar = StringVar()

photos_processed = BooleanVar()
photos_processed.set(0)

#labels
ttk.Label(mainframe, text = "Select Photo Folder:").grid(column =1, row = 1, sticky = W)
ttk.Label(mainframe, text = "Select Collector GDB:").grid(column =1, row = 2, sticky = W)
ttk.Label(mainframe, text = "Select Attachment Feature Table:").grid(column = 1, row = 3, sticky = W)
ttk.Label(mainframe, text = "Select Collector Feature Class:").grid(column = 1, row = 4, sticky = W)
ttk.Label(mainframe, text = "Select Master GDB:").grid(column =1, row = 5, sticky = W)
ttk.Label(mainframe, text = "Select Master Feature Class:").grid(column =1, row = 6, sticky = W)

#widgets set up
# - Select Photo folder
photo_folder_button = ttk.Button(mainframe,text = "Browse...", command = set_photo_folder)
photo_folder_button.grid(column = 2, row = 1, sticky = (W, E))
ttk.Label(mainframe,textvariable = photo_folder_location).grid(column = 3, row = 1, sticky = E)

# - Select Photo GDB
photo_workspace_button = ttk.Button(mainframe,text = "Browse for GDB", command = define_photo_workspace)
photo_workspace_button.grid(column = 2, row = 2, sticky = (W, E))
ttk.Label(mainframe,textvariable = photo_gdb).grid(column = 3, row = 2, sticky = E)
photo_workspace_button.bind('<ButtonRelease>',photo_fc_loading)

#- Select Photo Table
photo_table_combobox = ttk.Combobox(mainframe,state = "disabled",textvariable=photo_table)
photo_table_combobox.grid(column = 2, row = 3, sticky = (E,W))
photo_table_combobox.bind('<<ComboboxSelected>>',set_photo_table)
ttk.Label(mainframe,textvariable = photo_table).grid(column =3, row =3, sticky = E)

#- Select collector fc
collector_fc_combobox = ttk.Combobox(mainframe,state = "disabled",textvariable=collector_fc)
collector_fc_combobox.grid(column = 2, row = 4, sticky = (E,W))
collector_fc_combobox.bind('<<ComboboxSelected>>',set_collector_fc)
ttk.Label(mainframe,textvariable = collector_fc).grid(column =3, row =4, sticky = E)

# - Select Master GDB
master_gdb_button = ttk.Button(mainframe,text = "Browse for GDB", command = define_master_workspace)
master_gdb_button.grid(column = 2, row = 5, sticky = (W, E))
ttk.Label(mainframe,textvariable = master_gdb).grid(column = 3, row = 5, sticky = E)
master_gdb_button.bind('<ButtonRelease>',master_fc_loading)

#- Select collector fc
master_fc_combobox = ttk.Combobox(mainframe,state = "disabled",textvariable=master_fc)
master_fc_combobox.grid(column = 2, row = 6, sticky = (E,W))
master_fc_combobox.bind('<<ComboboxSelected>>',set_master_fc)
ttk.Label(mainframe,textvariable = master_fc).grid(column =3, row =6, sticky = E)


# - Start Analysis
startButton = ttk.Button(mainframe,text = "Process Photos", command = start_analysis)
startButton.grid(column = 2, row = 7, sticky = (E,W))
ttk.Label(mainframe,textvariable = statusvar, foreground = 'red').grid(column = 2, row = 8, sticky= (E,W), columnspan = 3)
startButton.bind('<ButtonPress>',set_processing)
startButton.bind('<ButtonRelease>', start_analysis)


for child in mainframe.winfo_children(): child.grid_configure(padx=10, pady=10)

root.mainloop()