# -----------------------------------------------------------------------------
# Format PostScripts
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: October 1, 2019
# 
#
# -----------------------------------------------------------------------------
# CITATION:
#
# -----------------------------------------------------------------------------

import os, sys
import Tkinter
import tkutil
import sputil
import wlutil
import tkFont
import sparky
import tkMessageBox
import tkFileDialog

default_cfg_text = """/bottomAxisScale?	true	def	% If the bottom axis is shown
/topAxisScale?		true	def	% If the top axis is shown
/leftAxisScale?		true	def	% If the left axis is shown
/rightAxisScale?	true	def	% If the right axis is shown
/leftAxisLabel?		true	def	% If the left axis label is shown
/bottomAxisLabel?	true	def	% If the bottom axis label is shown
/bottomTick?		true	def	% If the bottom ticks are shown
/topTick?		true	def	% If the top ticks are shown
/leftTick?		true	def	% If the left ticks are shown
/rightTick?		true	def	% If the right ticks are shown
/showBanner?		true	def	% If the banner is to be shown
/shadowUnderBanner?	true	def	% Place shadow box under banner
/planeBanner?		true	def	% In N-D spectra, shows current plane
/useGray?		true	def	% On B/W printer use gray scale?
/MajorTickInset		0	def	% Amount major tick goes inside panel
/MajorTickOutset	12	def	% Amount major tick goes outside panel
/MajorTickThickness	4	def	% Thickness of major tick
/MinorTickInset		0	def	% Amount minor tick goes inside panel
/MinorTickOutset	8	def	% Amount minor tick goes outside panel
/MinorTickThickness	1	def	% Thickness of minor tick
/EdgeLineWidth		4	def	% Thickness of border around panels
/LeftLabelPad		32	def	% Pad between left axis labels & label
/BottomLabelPad		32	def	% Pad between bottom axis labels & label
/AxisPad		8	def	% Pad between ticks and labels
/AxisFont		/Helvetica	def	% Font used for X/Y axis
/AxisFontSize		12		def	%   and its size
/BannerFont		/Helvetica	def	% Font used for the banner
/BannerFontSize		12 		def	%   and its size
/LabelFont		/Helvetica	def	% Font used for peak labels"""
default_cfg_lines = default_cfg_text.split('\n')
default_cfg_param_list, default_cfg_value_list, default_cfg_def_list = \
                                                          [], [], []
tmp_fntfam = tkFont.families()
fntfam = []
for fnt in tmp_fntfam: fntfam.append(fnt.replace(' ', ''))
fntfam=list(set(fntfam))
fntfam.sort()

default_fonts = ['Helvetica','FreeSans','Arial','Verdana',\
                  'Calibri','NotoSans','Ubuntu']
for i in range(len(default_cfg_lines)): 
  default_cfg_param_list.append(default_cfg_lines[i].strip().split()[0])
  val = default_cfg_lines[i].strip().split()[1]
  if val[0] == '/': # fonts
    for fnt in default_fonts:
      if fnt in fntfam:
        val = '/' + fnt
        break
  default_cfg_value_list.append(val)
  iPos = default_cfg_lines[i].strip().find('def')
  default_cfg_def_list.append(default_cfg_lines[i].strip()[iPos:])

def write_ps_cfg(ps_file, cfg_param_list, cfg_value_list, \
                  cfg_def_list, cfg_pos_list):
  f = open(ps_file, 'r')
  lines = f.readlines()
  f.close()
  for i in range(len(cfg_pos_list)):
    iPos = cfg_pos_list[i]
    val = cfg_value_list[i].strip()
    if val == '': continue
    if cfg_def_list[i].find('Font used') != -1:
      val = val.replace('/','')
      if not val in fntfam:
        val = default_cfg_value_list[i]
      else: val = '/' + val
    line = '%s\t\t%s\t%s\n' % (cfg_param_list[i], val, cfg_def_list[i])
    lines[iPos] = line
  f = open(ps_file, 'w')
  for line in lines:
    f.write(line)
  f.close()
  
def read_ps_cfg(ps_file):
  cfg_param_list, cfg_value_list, cfg_def_list, cfg_pos_list = \
          list(default_cfg_param_list), list(default_cfg_value_list), \
          list(default_cfg_def_list), \
          list(map(lambda x: -1, range(len(default_cfg_param_list))))
  f = open(ps_file, 'r')
  lines = f.readlines()
  f.close()
  for i in range(0, min(80, len(lines))):
    line = lines[i].strip()
    sp = line.split()
    if len(sp) < 5: continue
    try:
      idx = cfg_param_list.index(sp[0])
    except:
      continue
    cfg_value_list[idx], cfg_pos_list[idx] = sp[1], i
    try:
      idx = cfg_pos_list.index(-1)
    except:
      break
  
  try:
    idx = cfg_pos_list.index(-1)
    print cfg_param_list[idx]
    return None
  except:
    pass    
  return cfg_param_list, cfg_value_list, cfg_def_list, cfg_pos_list

# -----------------------------------------------------------------------------
class formatPS_dialog(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
    self.session = session
    tkutil.Dialog.__init__(self, session.tk, 'Format PostScripts')

    # Scrolling List
    self.slPS = tkutil.scrolling_list(self.top, 
          'PostScripts', 5, xscrollbar=True)
    self.slPS.listbox['selectmode'] = 'extended' # multiselect enabled
    self.slPS.frame.pack(side='top', fill = 'both', expand = 1)
    self.slPS.listbox.bind('<ButtonRelease-1>', self.selectPS_cb)

    # buttons
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)
    self.br = tkutil.button_row(self.top,
          ('Add', self.add_cb),
          ('Delete', self.delete_cb),
          ('Clear', self.clear_cb),
          ('Apply', self.apply_cb),
          ('Default', self.default_cb),
          ('Save', self.save_cb),
          ('Load', self.load_cb),
          ('Close', self.close_cb),
          )
    self.br.frame.pack(side = 'top', fill = 'both', expand = 0)     
    tkutil.create_hint(self.br.buttons[0], 'Add a PostScript to format.')
    tkutil.create_hint(self.br.buttons[1], 'Delete selected PostScripts from the list.')
    tkutil.create_hint(self.br.buttons[2], 'Clear all PostScripts in the list.')
    tkutil.create_hint(self.br.buttons[3], 'Apply changes to the selected PostScripts.')
    tkutil.create_hint(self.br.buttons[4], 'Load default settings.')
    tkutil.create_hint(self.br.buttons[5], 'Save user settings.')
    tkutil.create_hint(self.br.buttons[6], 'Load user settings.')
    
    # new panel for split panels
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)
    
    sp_frame = Tkinter.Frame(self.top)
    sp_frame.pack(side='top', fill = 'both', expand = 1)
    # right-panel: font-family
    self.lbFontFamily = tkutil.scrolling_list(sp_frame, 'Available Fonts', 29,
                          xscrollbar=True)
    for fnt in fntfam:  self.lbFontFamily.append(fnt, fnt)
    self.lbFontFamily.frame.pack(side='right', fill = 'both', expand = 1)

    # left-panel: settings
    self.scc = Tkinter.Frame(sp_frame)
    self.scc.pack(side='left', expand = 1)

    self.param_ef_list = []
    for pname in default_cfg_param_list:
      #ef = tkutil.entry_field(self.scc.frame, pname, initial='')
      pname = pname.replace('/','')
      ef = tkutil.entry_field(self.scc, pname, initial='')
      ef.frame.pack(side = 'top', anchor = 'w', expand = 1)
      self.param_ef_list.append(ef)

  def selectPS_cb(self, event):
    # bring settings
    ps_list = self.slPS.selected_line_data()

    if len(ps_list) == 0: return
    ps_file = ps_list[0]
    cfg_param_list, cfg_value_list, cfg_def_list, cfg_pos_list = \
      read_ps_cfg(ps_file)
    for i in range(len(self.param_ef_list)):
        ef = self.param_ef_list[i]
        val = cfg_value_list[i]
        if cfg_def_list[i].find('Font used') != -1:
          val = val.replace('/','')
        ef.variable.set(val)
  
  def add_cb(self):
    filez = tkFileDialog.askopenfilenames(parent=self.top, 
      title='Select PostScript file(s) to reconfigure.',
      defaultextension = '.ps',
      filetypes = [('PostScript files','.ps'),('All files (*.*)', '')],
      initialdir = tkutil.initial_file_dialog_path('PostScriptDir'),
      initialfile = '')
    ps_list = self.session.tk.splitlist(filez)
    for ps_file in ps_list:
      if ps_file in self.slPS.line_data: continue
      self.slPS.append(ps_file, ps_file)

  def delete_cb(self):
    self.slPS.delete_selected()

  def clear_cb(self):
    self.slPS.clear()

  def apply_cb(self):
    ps_list = self.slPS.selected_line_data()
    if len(ps_list) == 0:
      ps_list = self.slPS.line_data
    for ps_file in ps_list:
      cfg_param_list, cfg_value_list, cfg_def_list, cfg_pos_list = \
        read_ps_cfg(ps_file)
      for i in range(len(self.param_ef_list)):
        ef = self.param_ef_list[i]
        val = ef.variable.get()
        if val == '': continue
        if cfg_def_list[i].find('Font used') != -1:
          val2 = val.replace('/','')
          if not val2 in fntfam: continue
        cfg_value_list[i] = val
      write_ps_cfg(ps_file, cfg_param_list, cfg_value_list, \
                  cfg_def_list, cfg_pos_list)
    tkMessageBox.showinfo('Format Postscripts', 'Finished.')

    
  def default_cb(self):
    # set defaults in the settings
    for i in range(len(self.param_ef_list)):
      ef = self.param_ef_list[i]
      ef.variable.set(default_cfg_value_list[i])

  def load_cb(self):
    path = tkutil.load_file2(self.top, 'Load PostScript settings',
                  'postscript_settings', '.ini',
                  [('INI files','.ini'),('All files (*.*)', '')])
    if path:
      section = 'PostScript Settings'
      for i in range(len(default_cfg_param_list)):
        key = default_cfg_param_list[i].replace('/','')
        val = wlutil.LoadIniString(path, section, key)
        if val == '': continue
        ef = self.param_ef_list[i]
        ef.variable.set(val.replace('/',''))
      tkMessageBox.showinfo('Load Postscript settings', 'Loaded.')

  def save_cb(self):
    path = tkutil.save_file2(self.top, 'Save PostScript settings',
                  'postscript_settings', '.ini',
                  [('INI files','.ini'),('All files (*.*)', '')])
    if path:
      section = 'PostScript Settings'
      for i in range(len(self.param_ef_list)):
        key = default_cfg_param_list[i].replace('/','')
        ef = self.param_ef_list[i]
        val = ef.variable.get()
        if val == '':
          val = default_cfg_value_list[i]
        wlutil.SaveIniString(path, section, key, val.replace('/',''))
      tkMessageBox.showinfo('Save Postscript settings', 'Saved.')

# -----------------------------------------------------------------------------
#
def show_formatPS_dialog(session):
  sputil.the_dialog(formatPS_dialog,session).show_window(1)