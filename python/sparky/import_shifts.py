# ==============================================================================
# Import chemical shifts of N, H, CA and CB for each residue in a protein.
#
import os, string, Tkinter
import atomnames, tkutil, pyutil

# ------------------------------------------------------------------------------
#
monospace_font = { 'posix': ('Courier','12'),
                      'nt': ('Courier','10'),
                     'mac': ('Courier','12'),
                     'os2': ('Courier','12'),
                      'ce': ('Courier','12'),
                    'java': ('Courier','12'),
                  'riscos': ('Courier','12')
                 }[os.name]

aa_codes = ('ALA','A', 'ARG','R', 'ASN','N', 'ASP','D', 'CYS','C',
            'GLN','Q', 'GLU','E', 'GLY','G', 'HIS','H', 'ILE','I',
            'LEU','L', 'LYS','K', 'MET','M', 'PHE','F', 'PRO','P',
            'SER','S', 'THR','T', 'TRP','W', 'TYR','Y', 'VAL','V')

#
# Amino acid chemical shift statistics from BMRB database;
# partial list of restricted set, last updated on 28 June 2006.
#
shift_stats = {'A': {'HA' : 4.26,               # mean
                     'HB' : 1.36,
                     'CA' : (53.18, 2.01),      # mean, S.D.
                     'CB' : (18.96, 1.85)},
               'R': {'HA' : 4.29,
                     'HB' : 1.79,               # weighted mean of HB2 and HB3
                     'HG' : 1.57,
                     'HD' : 3.12,
                     'CA' : (56.84, 2.37),
                     'CB' : (30.64, 1.83),
                     'CG' : (27.24, 1.33),
                     'CD' : (43.14, 1.00)},
               'N': {'HA' : 4.68,
                     'HB' : 2.79,
                     'CA' : (53.50, 1.95),
                     'CB' : (38.63, 1.75)},
               'D': {'HA' : 4.60,
                     'HB' : 2.71,
                     'CA' : (54.62, 2.09),
                     'CB' : (40.80, 1.68)},
               'C': {'HA' : 4.69,
                     'HB' : 2.94,
                     'CA' : (57.80, 3.40),
                     'CB' : (33.65, 6.55)},
               'Q': {'HA' : 4.27,
                     'HB' : 2.04,
                     'HG' : 2.31,
                     'CA' : (56.57, 2.16),
                     'CB' : (29.16, 1.89),
                     'CG' : (33.73, 1.20)},
               'E': {'HA' : 4.25,
                     'HB' : 2.03,
                     'HG' : 2.29,
                     'CA' : (57.39, 2.13),
                     'CB' : (29.97, 1.75),
                     'CG' : (36.03, 1.35)},
               'G': {'HA' : 3.94,
                     'CA' : (45.34, 1.33)},
               'H': {'HA' : 4.62,
                     'HB' : 3.09,
                     'CA' : (56.46, 2.45),
                     'CB' : (30.22, 2.15)},
               'I': {'HA' : 4.18,
                     'HB' : 1.80,
                     'HG1': 1.26,
                     'HG2': 0.79,
                     'HD1': 0.69,
                     'CA' : (61.59, 2.75),
                     'CB' : (38.57, 2.07),
                     'CG1': (27.64, 1.94),
                     'CG2': (17.51, 1.52),
                     'CD1': (13.45, 1.77)},
               'L': {'HA' : 4.31,
                     'HB' : 1.59,
                     'HG' : 1.51,
                     'HD1': 0.77,
                     'HD2': 0.74,
                     'CA' : (55.66, 2.17),
                     'CB' : (42.25, 1.88),
                     'CG' : (26.73, 1.29),
                     'CD1': (24.57, 1.70),
                     'CD2': (24.09, 1.75)},
               'K': {'HA' : 4.27,
                     'HB' : 1.77,
                     'HG' : 1.38,
                     'HD' : 1.61,
                     'HE' : 2.93,
                     'CA' : (56.95, 2.23),
                     'CB' : (32.74, 1.83),
                     'CG' : (24.88, 1.24),
                     'CD' : (28.89, 1.29),
                     'CE' : (41.82, 0.97)},
               'M': {'HA' : 4.39,
                     'HB' : 2.03,
                     'HG' : 2.43,
                     'CA' : (56.18, 2.24),
                     'CB' : (30.00, 2.25),
                     'CG' : (32.02, 1.33)},
               'F': {'HA' : 4.61,
                     'HB' : 2.98,
                     'CA' : (58.17, 2.66),
                     'CB' : (39.90, 2.10)},
               'P': {'HA' : 4.39,
                     'HB' : 2.05,
                     'HG' : 1.92,
                     'HD' : 3.63,
                     'CA' : (63.32, 1.62),
                     'CB' : (31.79, 1.27),
                     'CG' : (27.21, 1.17),
                     'CD' : (50.35, 1.08)},
               'S': {'HA' : 4.49,
                     'HB' : 3.87,
                     'CA' : (58.69, 2.18),
                     'CB' : (63.77, 1.56)},
               'T': {'HA' : 4.46,
                     'HB' : 4.17,
                     'HG2': 1.15,
                     'CA' : (62.17, 2.70),
                     'CB' : (69.63, 1.82),
                     'CG2': (21.47, 1.25)},
               'W': {'HA' : 4.70,
                     'HB' : 3.18,
                     'CA' : (57.63, 2.63),
                     'CB' : (30.05, 2.05)},
               'Y': {'HA' : 4.62,
                     'HB' : 2.89,
                     'CA' : (58.09, 2.61),
                     'CB' : (39.24, 2.18)},
               'V': {'HA' : 4.17,
                     'HB' : 1.99,
                     'HG1': 0.83,
                     'HG2': 0.81,
                     'CA' : (62.47, 2.94),
                     'CB' : (32.65, 1.83),
                     'CG1': (21.43, 1.47),
                     'CG2': (21.30, 1.64)},
               'X': {}}

backbone_atoms = ('N', 'H', 'CA', 'CB')

sample_file = ("The file should be in plain text of the following format:\n" +
               "                                 \n" +
               "    1    LYS    CA     56.471    \n" +
               "    1    LYS    CB     33.317    \n" +
               "    2    THR     N    116.283    \n" +
               "    2    THR     H      8.201    \n" +
               "    2    THR    CA     62.177    \n" +
               "    .    ...    ..      ...      \n")

info_template = ("Error in line %d:\n" +
                 "----------------------------------------\n" +
                 "%s\n" +
                 "%s\n" +
                 "----------------------------------------\n" +
                 "%s\n")


# ==============================================================================
# Query user for the shifts file; preview, check and import its content.
#
class import_shifts_dialog(tkutil.Settings_Dialog):
    
    def __init__(self, session):
        
        self.isotope = Tkinter.IntVar()
        self.error_message = ""
        
        tkutil.Settings_Dialog.__init__(self, session.tk, "Import Chemical Shifts")
        
        self.top.columnconfigure(0, weight = 1)
        self.top.rowconfigure(1, weight = 1)
        
        fb = self.file_browser(self.top, "Shifts file", 20)
        fb.grid(row = 0, sticky = 'we', padx = 3, pady = 3)
        
        self.textbox = textbox(self.top, 10, 45)
        self.textbox.frame.grid(row = 1, sticky = 'news', padx = 3)
        self.textbox.show(sample_file)
        
        cb = Tkinter.Checkbutton(self.top, highlightthickness = 0,
                                 text = "Correct for deuterium isotope effect",
                                 variable = self.isotope)
        cb.grid(row = 2, sticky = 'w', padx = 3)
        
        br = tkutil.button_row(self.top,
                               ("Import", self.import_cb),
                               (" Ok ", self.ok_cb),
                               ("Cancel", self.close_cb),
                              )
        br.frame.grid(row = 3, padx = 3, pady = 3)
        
        self.ok = br.buttons[1]
        self.ok['state'] = 'disabled'       # disable "Ok" button till import finishes
    
    # --------------------------------------------------------------------------
    # Allow user to select a file by browsing or manually entering its path,
    # and automatically generate a preview (for text file) upon selection.
    #
    # Modified from class "file_field" in module "tkutil.py".
    #
    def file_browser(self, parent, title, length):
        
        frame = Tkinter.Frame(parent)
        frame.columnconfigure(0, weight = 1)
        
        self.file_path = tkutil.entry_field(frame, title, "", length)
        self.file_path.frame.grid(row = 0, column = 0, sticky = 'we')
        
        self.file_path.entry.pack(fill = 'x', expand = 1, padx = 3)
        self.file_path.entry.bind('<Return>', self.show_preview)
        
        self.path_entry = self.file_path.variable
        
        browse = Tkinter.Button(frame, text = "Browse ...", command = self.browse_cb)
        browse.grid(row = 0, column = 1)
        
        return frame
    
    # --------------------------------------------------------------------------
    # Pop up a file browsing dialog and set path to that of the chosen file.
    #
    def browse_cb(self):
        
        path = tkutil.load_file(self.top, "Open Shifts File", None)
        
        if path:
            self.path_entry.set(path)
            self.file_path.show_end()           # position to show file name part
            self.show_preview()
    
    # --------------------------------------------------------------------------
    # Preview of file content.
    #
    def show_preview(self, event = None):
        
        self.ok['state'] = 'disabled'
        self.path = self.path_entry.get()
        
        if self.path == "":
            self.error_message += "No shifts file selected!\n"
            self.textbox.show(self.error_message, 'end')
            return 'Failed'
            
        try:
            shifts_file = open(self.path, 'r')          # open file in read mode
            self.file_content = shifts_file.read()
            shifts_file.close()
        
        except IOError, message:
            self.error_message += str(message) + "\n"
            self.textbox.show(self.error_message, 'end')
            return 'Failed'
        
        except MemoryError:
            self.error_message += "File size exceeds memory limit!\n"
            self.textbox.show(self.error_message, 'end')
            shifts_file.close()
            return 'Failed'
        
        for byte in self.file_content:          # check whether it's a plain text file
            
            if byte not in string.printable:
                filename = os.path.split(self.path)[-1]
                self.error_message += "'%s' is not a plain text file!\n" % filename
                self.textbox.show(self.error_message, 'end')
                return 'Failed'
        
        self.error_message = ""                         # reset error message
        self.textbox.show(self.file_content)
    
    # --------------------------------------------------------------------------
    # Import sequence information and chemical shifts from the file.
    #
    def import_cb(self):
        
        if self.format_check() == 'Failed': return
        
        residues = []
        
        for line in self.file_content.splitlines():
            
            words = line.split()
            
            if words == []: continue                    # skip empty line
            
            self.textbox.show("Importing shifts for residue %d" % int(words[0]))
            self.textbox.text.update_idletasks()
            
            #
            # Append new residue to the list as residue number increases.
            #
            for i in range(len(residues), int(words[0])):
                residues.append({'number': i+1, 'name': "X"})
                
                for atom in backbone_atoms:
                    residues[-1][atom] = None           # set default shift to None
            
            residues[-1]['number'] = int(words[0])
            residues[-1]['name'] = words[1].upper()
            
            #
            # Assign chemical shift to the corresponding atom.
            #
            atom = words[2].upper()
            if atom in backbone_atoms:
                residues[-1][atom] = float(words[3])
        
        #
        # Count total number of imported residues.
        #
        total = len(filter(lambda res: res['name'] != "X", residues))
        self.textbox.show("Chemical shifts of %d residue%s imported."
                          % (total, pyutil.plural_ending(total)))
        
        self.residues = residues
        self.ok['state'] = 'normal'                     # enable "Ok" button
    
    # --------------------------------------------------------------------------
    # Check the data format of the shifts file;
    # if an error is found, print a message about its location and type.
    #
    def format_check(self):
        
        if self.show_preview() == 'Failed':
            return 'Failed'
        
        #
        # Trim trailing whitespaces in the file and split its content into lines.
        #
        lines = self.file_content.rstrip().splitlines()
        
        if lines == []:
            self.textbox.show("The selected file is empty!")
            return 'Failed'
        
        seq_number = 1
        
        for i, line in enumerate(lines):
            
            self.textbox.show("Checking data format of line %d" % (i+1))
            self.textbox.text.update_idletasks()
            
            line = line.strip().expandtabs(4)           # convert tab to 4 spaces
            words = line.split()
            
            if words == []: continue
            
            #
            # Check whether all 4 fields are present.
            #
            if len(words) < 4:
                pointer = " " * len(line) + "   ^" * (4-len(words))
                info = ("Missing data field.\n" +
                        "Residue number, name, atom name and shift are required.")
            
            #
            # Check whether the 1st field is a positive integer.
            #
            elif not words[0].isdigit() or int(words[0]) == 0:
                pointer = "^"
                info = ("Invalid residue number '%s'.\n" % words[0] +
                        "Only positive integers are allowed.")
            
            #
            # Check whether residue number increases monotonically (allow jumps).
            #
            elif int(words[0]) < seq_number:
                pointer = "^"
                info = ("Bad sequence (%d -> %s).\n" % (seq_number, words[0]) +
                        "Residue number must increase monotonically.")
            
            #
            # Check whether the 2nd field contains a valid amino acid code.
            #
            elif words[1].upper() not in aa_codes:
                pointer = " " * word_index(2, line) + "^"
                info = ("Residue '%s' not recognized.\n" % words[1] +
                        "Please follow the standard 1-letter or 3-letter codes.")
            
            #
            # Check whether the 4th field is a floating point number.
            #
            elif pyutil.string_to_float(words[3]) == None:
                pointer = " " * word_index(4, line) + "^"
                info = ("Invalid chemical shift '%s'.\n" % words[3] +
                        "The value should be a floating point number.")
            
            else:
                info = ""
                seq_number = int(words[0])
            
            if info:
                line = line[:40] + " ..." * (len(line) > 40)
                error_info = info_template % (i+1, line, pointer, info)
                self.textbox.show(error_info)
                return 'Failed'
    
    # --------------------------------------------------------------------------
    # Apply the imported shifts and close this dialog.
    #
    def ok_cb(self):
        
        #
        # Correct for deuterium isotope effect if required by user.
        #
        if self.isotope.get():
            residues = self.isotope_correction()
        else:
            residues = self.residues
        
        shifts = []
        
        for res in residues:
            
            name = res['name']
            if len(name) != 1:
                name = atomnames.aaa_to_a[name]         # convert to 1-letter code
            
            #
            # Copy NH shifts to the new shift list.
            #
            shifts.append({'group': "%s%d" % (name, res['number']),
                              'NH': (res['N'], res['H'])})
            
            #
            # Fill in shift statistics of CA, HA, CB, HB, CG, HG, etc.
            #
            shifts[-1].update(shift_stats[name])
            
            if res['CA'] != None:
                shifts[-1]['CA'] = (res['CA'], -1)
            if res['CB'] != None:
                shifts[-1]['CB'] = (res['CB'], -1)
        
        #
        # Make sure the list has a minimum length of 3.
        #
        shifts += [{'group': x} for x in ('X1','X2','X3')][len(shifts):3]
        
        self.new_settings_cb(shifts, self.path)
        self.close_cb()
    
    # --------------------------------------------------------------------------
    # Deuterium labeling will cause chemical shifts of carbon atoms to
    # deviate from those in unlabeled sample. This function corrects the
    # imported shifts for such effect.
    #
    # Thanks to Xu Yingqi for providing the code.
    #
    def isotope_correction(self):
        
        residues = []
        
        for res in self.residues:
            residues.append({})
            residues[-1].update(res)
        
        delta_1 = -0.29
        delta_2 = -0.13
        delta_3 = -0.07
        delta_g = -0.39
        
        for res in residues:
            
            name = res['name']
            if len(name) != 1:
                name = atomnames.aaa_to_a[name]
            
            if name in ('N','D','C','H','F','S','W','Y'):
                if res['CA']:
                    res['CA'] -= delta_1 + delta_2 * 2
                if res['CB']:
                    res['CB'] -= delta_1 * 2 + delta_2
            
            elif name in ('R','K','P'):
                if res['CA']:
                    res['CA'] -= delta_1 + delta_2 * 2 + delta_3 * 2
                if res['CB']:
                    res['CB'] -= delta_1 * 2 + delta_2 * 3 + delta_3 * 2
            
            elif name in ('Q','E','M'):
                if res['CA']:
                    res['CA'] -= delta_1 + delta_2 * 2 + delta_3 * 2
                if res['CB']:
                    res['CB'] -= delta_1 * 2 + delta_2 * 3
            
            elif name == 'A':
                if res['CA']:
                    res['CA'] -= delta_1 + delta_2 * 3
                if res['CB']:
                    res['CB'] -= delta_1 * 3 + delta_2
            
            elif name == 'I':
                if res['CA']:
                    res['CA'] -= delta_1 + delta_2 + delta_3 * 5
                if res['CB']:
                    res['CB'] -= delta_1 + delta_2 * 6
            
            elif name == 'L':
                if res['CA']:
                    res['CA'] -= delta_1 + delta_2 * 2 + delta_3
                if res['CB']:
                    res['CB'] -= delta_1 * 2 + delta_2 * 2
            
            elif name == 'T':
                if res['CA']:
                    res['CA'] -= delta_1 + delta_2 + delta_3 * 3
                if res['CB']:
                    res['CB'] -= delta_1 + delta_2 * 4
            
            elif name == 'V':
                if res['CA']:
                    res['CA'] -= delta_1 + delta_2
                if res['CB']:
                    res['CB'] -= delta_1 + delta_2
            
            elif name == 'G':
                if res['CA']:
                    res['CA'] -= delta_g * 2
        
        return residues


# ==============================================================================
# A textbox with vertical scrolling bar,
# used for preview of file content or display of error messages.
#
class textbox(tkutil.scrolling_text):
    
    def __init__(self, parent, height, width):
        
        tkutil.scrolling_text.__init__(self, parent, height, width)
        self.text.config(wrap = 'word', font = monospace_font)
    
    # --------------------------------------------------------------------------
    # Show content in the textbox.
    #
    def show(self, content, index = '0.0'):
        
        self.text['state'] = 'normal'
        self.text.delete('0.0', 'end')
        self.text.insert('0.0', content)
        self.text['state'] = 'disabled'
        
        self.text.see(index)            # scroll to show text at given index


# ==============================================================================
# Return the index of the start of the n-th word in a string;
# if the string has less than n words, return -1.
#
def word_index(n, string_):
    
    words = string_.split()
    
    if n > len(words):
        return -1
    
    if n == 1:
        return string_.index(words[0])
    else:
        start = word_index(n-1, string_) + len(words[n-2])
        return string_.index(words[n-1], start)
