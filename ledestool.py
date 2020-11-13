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

CONFIG_FILE = "profiles.yaml"
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
    status_text.set(message)
    print(message)
    global status
    status.pack(padx=5, pady=3, fill=X, side=BOTTOM)

# get LEDES column number from name or number
def get_column(x):
    if type(x) is int:
        return x
    else:
        try:
            return LEDES_COLUMNS.index(x)
        except ValueError:
            return -1
        
# Allow user to select a directory and store it in global var
# called folder_path
def browse_button():
    global folder_path
    filename = filedialog.askdirectory()
    if filename:
        folder_path.set(filename)
        global label1,opts
        label1.config(state=NORMAL)
        opts.config(state=NORMAL)

# convert all files in folder_path
def convert_files():
    global profiles, selected_profile
    converted_file_count = 0

    # loop through selected folder path
    for folder, subs, files in os.walk(folder_path.get()):
        for filename in files:         
            if not "converted" in filename:
                # open input file
                full_filename = os.path.join(folder, filename)
                with open(full_filename) as f:
                    contents = f.read().splitlines()

                # check that this is a LEDES formatted file
                if "LEDES" in contents[0]:            
                
                    # count number of files converted
                    converted_file_count = converted_file_count + 1
                                           
                    # open conversion file
                    (base,ext) = os.path.splitext(filename)
                    new_filename = base + '.converted' + ext
                    new_full_filename = os.path.join(folder, new_filename)
                    o = open(new_full_filename,"w")              
                                                   
                    # select appropriate profile                    
                    conversion_profile_name = selected_profile.get()                                       
                    if "AutoSelect" in conversion_profile_name:
                        for profile_name in profiles.keys():                            
                            if "autoselect" in profiles[profile_name]:
                                for label,val in profiles[profile_name]["autoselect"].items():
                                    field = get_column(label)
                                    try:
                                        valuechecklist = val if type(val)==list else [val]
                                        for v in valuechecklist:
                                            if str(v) in contents[2][:-2].split('|')[field]: conversion_profile_name=profile_name
                                    except:
                                        break
                        if "AutoSelect" in conversion_profile_name:
                            if "Default" in profiles: 
                                conversion_profile_name = "Default"
                                profile = profiles[conversion_profile_name]
                            else:                                
                                conversion_profile_name = next(iter(profiles.keys()))
                    profile = profiles[conversion_profile_name]  
                    
                    status_update(f"Converting {full_filename} to {new_full_filename} ({conversion_profile_name}) ...")

                    # check output format
                    output_BI = "BI" in profile["output_format"] if "output_format" in profile else True
                    extend_to_BI = output_BI and not "BI" in contents[0] 
                    
                    # loop through each line of input file
                    for line_number, content in enumerate(contents):  
                    
                        # write appropriate header
                        if line_number == 0:
                            o.write("LEDES98BI V5[]\n") if output_BI else o.write(content)                           
                            
                        # convert header
                        elif line_number == 1:
                            if extend_to_BI:
                                o.write(f"{content[:-2]}|{'|'.join(LEDES_COLUMNS[24:])}[]\n")
                        
                        # convert line                    
                        else:
                            # get fields
                            fields = content[:-2].split('|');
                            
                            # add additional blank fields if needed
                            if extend_to_BI:
                                for i in range(23, 51):
                                    fields.append('');
                                
                                # execute transformations
                                if "transformations" in profile:
                                    for transformation in profile["transformations"]:                                        
                                        try:
                                            # this is for format where column is specified in 'field' field
                                            if "field" in transformation:
                                                field_list = transformation["field"] if type(transformation["field"])==list else [transformation["field"]]
                                                for label in field_list:
                                                    field_id = get_column(label)
                                                    fields[field_id] = transform_field(field_id,fields,transformation)
                                            # this is for format where column is specified as key
                                            else:
                                                for label,args in transformation.items():
                                                    field_id = get_column(label)                                                
                                                    fields[field_id] = transform_field(field_id,fields,args)
                                        except:
                                            break
                            # output converted line                                                                                    
                            o.write('|'.join(fields)+'[]\n')
                    # close file        
                    o.close()

    # report to user
    if converted_file_count:
        status_update("All LEDES files in the folder have been converted.")
    else:
        status_update("No LEDES files in the folder.")

def transform_field(field_id,fields,transformation):
    ret = fields[field_id]
    # copy
    if "source" in transformation:
        ret = fields[get_column(transformation["source"])]
    
    # set    
    if "value" in transformation:
        ret = str(transformation["value"])
    
    # replace text
    if "oldtext" in transformation:
        newtext = "" if "newtext" not in transformation else transformation["newtext"]
        ret = ret.replace(transformation["oldtext"],newtext)

    # map values (replace only if field is exactly
    if "map" in transformation:
        try:
            if ret in transformation["map"]:
                ret = str(transformation["map"][ret])
        except TypeError:
            False
            
    # upper
    if "upper" in transformation:
        ret = ret.upper()                                                
        
    # lower
    if "lower" in transformation:
        ret = ret.lower()
        
    # split
    if "split" in transformation:
        i = transformation["index"] if "index" in transformation else 0
        if transformation["split"] in ret:
            try:
                ret = ret.split(transformation["split"])[i]
            except IndexError:
                ret = ""
    return ret

def make_dummy_profile():
    o = open(CONFIG_FILE,"w") 
    o.write("# LEDES Tool profile file\n# Add a separate entry for each desired profile\n\n")
    o.write("Default:\n output_format: 1998BI\n")
    o.close()

def get_profiles():
    if not os.path.exists(CONFIG_FILE): 
        make_dummy_profile()
    try:
        with open(CONFIG_FILE) as f:
            profiles = yaml.load(f, Loader=yaml.FullLoader)
        return profiles
    except:
        status_update("Error parsing profile file!")
        return False


window=Tk()
folder_path = StringVar(window)
status_text = StringVar(window)
selected_profile = StringVar(window)

if __name__ == "__main__":

    # title frame
    frame = Frame(window)
    title = Label(frame, text="LEDES Conversion Tool", fg='black', font=("Helvetica", 16))
    subtitle = Label(frame, text="version "+MAJOR_VERSION, fg='black', font=("Helvetica", 10))
    title.pack(padx=5, pady=10, side=LEFT)
    subtitle.pack(padx=5, pady=10, side=RIGHT)

    # option selection frame
    frame1 = Frame(window)
    label1 = Label(frame1, text="Select conversion profile:", state=DISABLED)
    label1.pack(padx=5, pady=5, side=LEFT)
    button_convert=Button(frame1, text="Convert", command=convert_files, state=DISABLED)
    button_convert.pack(padx=5, pady=5, side=RIGHT)

    # folder selection frame
    frame2 = Frame(window)
    label2 = Label(frame2, text="Select a folder to convert:")
    label2.pack(padx=5, pady=5, side=LEFT)
    folder_entry=Entry(frame2, textvariable = folder_path, bd=5, width=40)
    folder_entry.pack(padx=5, pady=5, side=LEFT)
    button_browse=Button(frame2, text="Browse", command=browse_button)
    button_browse.pack(padx=5, pady=5, side=RIGHT)

    # status frame
    status = Label(window, textvariable = status_text, relief=SUNKEN, bd=3, fg="#333")

    # get profile
    profiles = get_profiles()
    if not profiles:
        status_text.set("Error parsing profile file!")
        button_browse.config(state=DISABLED)
        status.config(fg='red')
    else:
        #option selection frame
        option_list = list(profiles.keys())
        option_list.insert(0,"AutoSelect")
        selected_profile.set("Pick a Profile")
        opts = OptionMenu(frame1,selected_profile, *option_list, command=lambda o: button_convert.config(state=NORMAL))
        opts.config(width=20,state=DISABLED)
        opts.pack(padx=5, pady=5, side=LEFT, fill=X)

    # pack the frames all up
    frame.pack(fill=X)
    frame2.pack(fill=X)
    frame1.pack(fill=X)

    # and go
    window.title('LEDES Conversion Tool')
    window.mainloop()
