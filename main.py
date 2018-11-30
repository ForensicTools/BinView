#########################
# File: Main.py
# Author: ChrisRisp
# Project: Binview
# Version 0.2
#########################

####
# NOTES
'''
If we flag a group of offsets together with the same label ( When should it flag region )
Offsets within given range occupy certain memory region. How much memory is this relative to the size of file. Signifigance rating
Percentage occupied in memory.


Time is important in forensic investigation this improves the workflow.

Flag region of memory as known type

'''
####

import os
import sys
import binwalk
import math
from collections import defaultdict


header = "\
__________.__            .__           \n\
\______   \__| _______  _|__| ______  _  __\n\
 |    |  _/  |/    \  \/ /  |/ __ \ \/ \/ /\\\n\
 |    |   \  |   |  \   /|  \  ___/\     /\n\
 |______  /__|___|  /\_/ |__|\___  >\/\_/  \n\
        \/        \/             \/         \n"

colors = {
    'blue': '\033[94m',
    'pink': '\033[95m',
    'green': '\033[92m',
    'red' : '\33[31m'
}

# Artifact Count/Offset Dicts
header_count = dict()
header_offsets = defaultdict(list)
header_flagged = defaultdict(list)

#Flag counter
flag_count = 0

# Output text color Func
def colorize(string, color):

    if not color in colors: return string
    return colors[color] + string + '\033[0m'


#
# Run tools
#
def analyze():

    for module in binwalk.scan(sys.argv[1],
                               signature=True,
                               quiet=True):

        for result in module.results:
            key = result.description.split(',')[0]
            meta = result.description.split(',')
            offset = result.offset
            try:
                # Increment Occurence count
                val = header_count[key]
                header_count[key] = val+1
                # Save Metadata
                if(len(meta) == 5):
                    header_offsets[key].append([offset, meta[2], meta[3], meta[4]])
                if(len(meta) == 4):
                    header_offsets[key].append([offset, meta[2], meta[3]])
            except:
                # print ("No such entry yet")
                # Increment Occurence count
                header_count[key] = 1
                # Save Metadata
                if (len(meta) == 5):
                    header_offsets[key].append([offset, meta[2], meta[3], meta[4]])
                if (len(meta) == 4):
                    header_offsets[key].append([offset, meta[2], meta[3]])





    raw_input("Analyzed: Press [Enter] to continue...")

#
# Offsets submenu1: Show Offset results
#
def show_results():
    sub = True
    while sub:
        submenuItems1 = [
            {"List Offsets [idx,#]": show_offsets},
            {"Flag Filetype [#]": flag_header},
            {"Dump All": show_offsets},
            {"Exit": exit},
        ]

        os.system('clear')

        # Print Table
        print(" {0:^10}  {1:^10}".format("Count", "Type"))
        print("-"*30)
        idx = 0

        # Get Header occurences
        for k, v in header_count.items():
            print ("[" + str(idx) + "] {0:^15} {1}".format(v, k))
            idx+=1
        print '\n'

        for item in submenuItems1:
            print colorize("[" + str(submenuItems1.index(item)) + "] ", 'blue') + item.keys()[0]
        choice = raw_input("(binview)$ ")
        selection = choice.split(',')
        try:
            if int(selection[0]) < 0: raise ValueError
            if int(selection[0]) == 3: sub = False
            # Call the matching function

            if int(selection[0]) == 1:
                submenuItems1[int(selection[0])].values()[0](int(selection[1]), str(selection[2]))
            else:
                submenuItems1[int(selection[0])].values()[0](int(selection[1]))


        except (ValueError, IndexError) as e:
            print e
#
# Offsets submenu 2
#
def show_offsets(selection):
    submenuItems2 = [
        {"DD Extract [#]": analyze},
        {"Flag Filetype [#]": flag_header},
        {"Dump All": show_offsets},
        {"Exit": exit},
    ]

    idx = 0
    for offset in header_offsets[header_offsets.keys()[selection]]:
        if (len(offset) > 2):
            print "["+str(idx)+"] " + "Offset: " + hex(offset[0]) + offset[1] + " Bytes"
        else:
            print "["+str(idx)+"] " + "Offset: " + hex(offset[0]) + offset[1] + " Bytes"
        idx+=1


        prev_offset = offset
    os.system('clear')

    for item in submenuItems2:
        print colorize("[" + str(submenuItems2.index(item)) + "] ", 'blue') + item.keys()[0]
    choice = raw_input("(binview)$ ")
    off_selection = choice.split(',')
    try:
        if int(off_selection[0]) < 0: raise ValueError
        # Call the matching function

        if int(off_selection[0]) == 1:
            submenuItems2[int(choice[0])].values()[0](str(off_selection[2]), header_offsets[header_offsets.keys()[selection]][int(off_selection[1])])
        else:
            submenuItems2[int(choice)].values()[0]()
    except (ValueError, IndexError):
        pass

#
# Flag header
#
def flag_header(description, offset):
    #global flag_count
    # Header name [header_count.keys()[selection]
    size = get_size(offset)
    header_flagged[description].append([offset[0], size])
   # header_flagged.append(header_count.keys()[selection])
    #flag_count+=1
    print colorize("Header Flagged!", 'red')

#
# Report Builder
#

def build_profile():
    # Get Density Report: Print range of memory frequent headers
    rp = open(sys.argv[1] + "_report.txt", "w")

    # Write heading
    rp.write("BinView v0.1 Report\n"
            "File: " + sys.argv[1] + "\n\n")

    # Write Flagged Headers
    rp.write("[Flagged Headers]\n\n")
    for entry in header_flagged:
            rp.write("*" + entry + "\n")

    # Write total identified headers
    rp.write("\n\n[Identified Headers]\n\n")
    for entry in header_count.keys():
            rp.write(entry + "\n")

#
# Layout Graphing
#
def build_graph():
    file_size = os.stat(sys.argv[1]).st_size
    print ("File Size: " + str(file_size))
    print ("File End: " + str(hex(file_size)))
    print ("Row Count: " + str(file_size/(file_size/16)))
    row_count = file_size/(file_size/16)
    row_size = math.ceil(file_size/row_count)
    print "Size Per Row: " + str(row_size)

    # Rows to be inserted
    marker_rows = []

    # Distance between marked locations for averaging
    mem_avg = []
    #
    #######################

    # Calculate Size Percentage
    ############################################333
    flag_name = ""
    flagged_size_total = 0
    # How many offsets associate with flag len(val)
    prev_off = -1
    for key, val in header_flagged.items():
        flag_name = key
        # Calculate percentage of binary based on size
        for offset in val:
            # Should be size
            flagged_size_total += int(offset[1])
            if prev_off != -1:
                mem_avg.append(math.fabs(int(offset[0])))
            prev_off=offset[0]

    area = (float(flagged_size_total) / float(file_size))
    area_percent = area * 100
    print "Occupies " + str(area_percent) + "%"
    #####################################################

    #Calculate memory range
    ###############################################

    #Add sizes, Check distance between offsets and place into memory area
    dist_total = 0
    for dist in mem_avg:
        dist_total+=dist
    dist_total = dist_total/len(mem_avg)

    print "Average Memory location: " + str(hex(int(dist_total)))


    print colorize("|------------------------|", 'blue')
    for i in range(0,file_size/(file_size/16)+1): # Or size of file

        curr = row_size * i
        next = row_size * (i +1)


        if(((row_size*i) <= dist_total <= (row_size*(i+1)))):
            print colorize("|########################| <-- Addr: " + str(hex(int(curr))) + " <-- Flag: " + flag_name + " Avg: " + str(hex(int(dist_total))), 'red')

        else:
            print colorize("|########################| <-- Addr: " + str(hex(int(curr))), 'blue')
    #
        #else:
         #   print colorize("|                        |", 'blue')
        # If there is a density
    print colorize("|------------------------|", 'blue')


def get_size(meta_data):
    size = 0
    for el in meta_data:
        el = str(el)
        if "size" in el:
            tmp = el.split(':')
            tmp2 = tmp[1].split(' ')
            size = tmp2[1]
            break
    return size



menuItems = [
    {"Analyze File": analyze},
    {"Show Results": show_results},
    {"Build Profile": build_graph},
    {"Exit": exit},
]


def main():
    while True:
        os.system('clear')
        print colorize(header, 'blue')
        print colorize('version 0.2\n', 'green')
        for item in menuItems:
            print colorize("[" + str(menuItems.index(item)) + "] ", 'blue') + item.keys()[0]
        choice = raw_input("(binview)$ ")
        try:
            if int(choice) < 0: raise ValueError
            # Call the matching function
            menuItems[int(choice)].values()[0]()
        except (ValueError, IndexError):
            pass


if __name__ == "__main__":
    main()