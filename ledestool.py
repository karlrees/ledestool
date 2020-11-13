#!/usr/bin/env python
import os
import sys
import yaml
from tkinter import *
from tkinter import filedialog

MAJOR_VERSION = "1.0"

print('\n_____________________________________');
print('|                                   |');
print('|  LEDES CONVERSION TOOL            |');
print(f'|     version {MAJOR_VERSION}                   |');
print('|  by Karl Rees, copyright 2020     |');
print('|___________________________________|\n');

CONFIG_FILE = "formatting.yaml"
LEDES_COLUMNS = (  "INVOICE_DATE",
                    "INVOICE_NUMBER",
                    "CLIENT_ID",
                    "LAW_FIRM_MATTER_ID",
                    "INVOICE_TOTAL",
                    "BILLING_START_DATE",
                    "BILLING_END_DATE",
                    "INVOICE_DESCRIPTION",
                    "LINE_ITEM_NUMBER",
                    "EXP/FEE/INV_ADJ_TYPE",
                    "LINE_ITEM_NUMBER_OF_UNITS",
                    "LINE_ITEM_ADJUSTMENT_AMOUNT",
                    "LINE_ITEM_TOTAL",
                    "LINE_ITEM_DATE",
                    "LINE_ITEM_TASK_CODE",
                    "LINE_ITEM_EXPENSE_CODE",
                    "LINE_ITEM_ACTIVITY_CODE",
                    "TIMEKEEPER_ID",
                    "LINE_ITEM_DESCRIPTION",
                    "LAW_FIRM_ID",
                    "LINE_ITEM_UNIT_COST",
                    "TIMEKEEPER_NAME",
                    "TIMEKEEPER_CLASSIFICATION",
                    "CLIENT_MATTER_ID",
                    "PO_NUMBER",
                    "CLIENT_TAX_ID",
                    "MATTER_NAME",
                    "INVOICE_TAX_TOTAL",
                    "INVOICE_NET_TOTAL",
                    "INVOICE_CURRENCY",
                    "TIMEKEEPER_LAST_NAME",
                    "TIMEKEEPER_FIRST_NAME",
                    "ACCOUNT_TYPE",
                    "LAW_FIRM_NAME",
                    "LAW_FIRM_ADDRESS_1",
                    "LAW_FIRM_ADDRESS_2",
                    "LAW_FIRM_CITY",
                    "LAW_FIRM_STATEorREGION",
                    "LAW_FIRM_POSTCODE",
                    "LAW_FIRM_COUNTRY",
                    "CLIENT_NAME",
                    "CLIENT_ADDRESS_1",
                    "CLIENT_ADDRESS_2",
                    "CLIENT_CITY",
                    "CLIENT_STATEorREGION",
                    "CLIENT_POSTCODE",
                    "CLIENT_COUNTRY",
                    "LINE_ITEM_TAX_RATE",
                    "LINE_ITEM_TAX_TOTAL",
                    "LINE_ITEM_TAX_TYPE",
                    "INVOICE_REPORTED_TAX_TOTAL",
                    "INVOICE_TAX_CURRENCY" )

# Output status update
def status_update(message):
    statustext.set(message)
    print(message)
    global status
    status.pack(padx=5, pady=3, fill=X, side=BOTTOM)

# get LEDES column number from name or number
def getcol(x):
    if type(x) is int:
        return x
    else:
        try:
            return LEDES_COLUMNS.index(x)
        except ValueError:
            return False
        
# Allow user to select a directory and store it in global var
# called folder_path
def browse_button():
    global folder_path
    filename = filedialog.askdirectory()
    if filename:
        folder_path.set(filename)
        global lbl1,opts
        lbl1.config(state=NORMAL)
        opts.config(state=NORMAL)

# convert all files in folder_path
def convertfiles():
    global clientformatting, selectedformat
    ccount = 0

    # loop through selected folder path
    for folder, subs, files in os.walk(folder_path.get()):
        for filename in files:         
            if not "converted" in filename:
                # open input file
                fullfilename = os.path.join(folder, filename)
                with open(fullfilename) as f:
                    contents = f.read().splitlines()

                # check that this is a LEDES formatted file
                if "LEDES" in contents[0]:            
                
                    # count number of files converted
                    ccount = ccount + 1
                                           
                    # open conversion file
                    (base,ext) = os.path.splitext(filename)
                    newfilename = base + '.converted' + ext
                    newfullfilename = os.path.join(folder, newfilename)
                    o = open(newfullfilename,"w")              
                                                   
                    # select appropriate settings                    
                    conversionformat = selectedformat.get()                    
                    if "AutoSelect" in conversionformat:
                        for setting in clientformatting.keys():                            
                            if "autoselect" in clientformatting[setting]:
                                for fieldlabel,val in clientformatting[setting]["autoselect"].items():
                                    field = getcol(fieldlabel)
                                    try:
                                        valuechecklist = val if type(val)==list else [val]
                                        for v in valuechecklist:
                                            if str(v) in contents[2][:-2].split('|')[field]: conversionformat=setting
                                    except:
                                        break
                    conversionformat = conversionformat if conversionformat in clientformatting else "Default"                    
                    settings = clientformatting[conversionformat] 
                    
                    status_update(f"Converting {fullfilename} to {newfullfilename} ({conversionformat}) ...")

                    # check output format
                    outputBI = "BI" in settings["output_format"] if "output_format" in settings else True
                    extendtoBI = outputBI and not "BI" in contents[0] 
                    
                    # loop through each line of input file
                    for linenum, content in enumerate(contents):  
                    
                        # write appropriate header
                        if linenum == 0:
                            o.write("LEDES98BI V5[]\n") if outputBI else o.write(content)                           
                            
                        # convert header
                        elif linenum == 1:
                            if extendtoBI:
                                o.write(f"{content[:-2]}|{'|'.join(LEDES_COLUMNS[24:])}[]\n")
                        
                        # convert line                    
                        else:
                            # get fields
                            fields = content[:-2].split('|');
                            
                            # add additional blank fields if needed
                            if extendtoBI:
                                for i in range(23, 51):
                                    fields.append('');
                                
                                # execute transformations
                                if "transformations" in settings:
                                    for transform in settings["transformations"]:                                        
                                        try:
                                            # this is for format where column is specified in 'field' field
                                            if "field" in transform:
                                                fieldlist = transform["field"] if type(transform["field"])==list else [transform["field"]]
                                                for fieldlabel in fieldlist:
                                                    field = getcol(fieldlabel)
                                                    fields[field] = transformfield(field,fields,transform)
                                            # this is for format where column is specified as key
                                            else:
                                                for fieldlabel,args in transform.items():
                                                    field = getcol(fieldlabel)                                                
                                                    fields[field] = transformfield(field,fields,args)
                                        except TypeError:
                                            break
                            # output converted line                                                                                    
                            o.write('|'.join(fields)+'[]\n')
                    # close file        
                    o.close()

    # report to user
    if ccount:
        status_update("All LEDES files in the folder have been converted.")
    else:
        status_update("No LEDES files in the folder.")

def transformfield(field,fields,transform):
    ret = fields[field]
    # copy
    if "source" in transform:
        ret = fields[getcol(transform["source"])]
    
    # set    
    if "value" in transform:
        ret = str(transform["value"])
    
    # replace text
    if "oldtext" in transform:
        newtext = "" if "newtext" not in transform else transform["newtext"]
        ret = ret.replace(transform["oldtext"],newtext)

    # map values (replace only if field is exactly
    if "map" in transform:
        try:
            if ret in transform["map"]:
                ret = str(transform["map"][ret])
        except TypeError:
            False
            
    # upper
    if "upper" in transform:
        ret = ret.upper()                                                
        
    # lower
    if "lower" in transform:
        ret = ret.lower()
        
    # split
    if "split" in transform:
        i = transform["index"] if "index" in transform else 0
        if transform["split"] in ret:
            try:
                ret = ret.split(transform["split"])[i]
            except IndexError:
                ret = ""
    return ret

def makedummyconfig():
    o = open(CONFIG_FILE,"w") 
    o.write("# LEDES Tool configuration file\n# Add a separate entry for each desired conversion setting\n\n")
    o.write("Default:\n output_format: 1998BI\n")
    o.close()

def getsettings():
    if not os.path.exists(CONFIG_FILE): 
        makedummyconfig()
    try:
        with open(CONFIG_FILE) as f:
            clientformatting = yaml.load(f, Loader=yaml.FullLoader)
        return clientformatting
    except:
        status_update("Error parsing configuration file!")
        return False


window=Tk()
folder_path = StringVar(window)
statustext = StringVar(window)
selectedformat = StringVar(window)

# title frame
frame = Frame(window)
title = Label(frame, text="LEDES Conversion Tool", fg='black', font=("Helvetica", 16))
subtitle = Label(frame, text="version "+MAJOR_VERSION, fg='black', font=("Helvetica", 10))
title.pack(padx=5, pady=10, side=LEFT)
subtitle.pack(padx=5, pady=10, side=RIGHT)

# option selection frame
frame1 = Frame(window)
lbl1 = Label(frame1, text="Select conversion settings:", state=DISABLED)
lbl1.pack(padx=5, pady=5, side=LEFT)
btnconvert=Button(frame1, text="Convert", command=convertfiles, state=DISABLED)
btnconvert.pack(padx=5, pady=5, side=RIGHT)

# folder selection frame
frame2 = Frame(window)
lbl2 = Label(frame2, text="Select a folder to convert:")
lbl2.pack(padx=5, pady=5, side=LEFT)
txtfld=Entry(frame2, textvariable = folder_path, bd=5, width=40)
txtfld.pack(padx=5, pady=5, side=LEFT)
btnbrowse=Button(frame2, text="Browse", command=browse_button)
btnbrowse.pack(padx=5, pady=5, side=RIGHT)

# status frame
status = Label(window, textvariable = statustext, relief=SUNKEN, bd=3, fg="#333")

# get settings
clientformatting = getsettings()
if not clientformatting:
    statustext.set("Error parsing configuration file!")
    btnbrowse.config(state=DISABLED)
    status.config(fg='red')
    #status.pack(padx=5, pady=3, fill=X, side=BOTTOM)
else:
    #option selection frame
    optionlist = list(clientformatting.keys())
    optionlist.insert(0,"AutoSelect")
    selectedformat.set("Select a Format")
    opts = OptionMenu(frame1,selectedformat, *optionlist, command=lambda o: btnconvert.config(state=NORMAL))
    opts.config(width=20,state=DISABLED)
    opts.pack(padx=5, pady=5, side=LEFT, fill=X)

# pack the frames all up
frame.pack(fill=X)
frame2.pack(fill=X)
frame1.pack(fill=X)

# and go
window.title('LEDES Conversion Tool')
window.mainloop()
