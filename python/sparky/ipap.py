import radio

import Tkinter

from math import *
import re
import os
import sys
import imp
import string
import popen2
import subprocess

import pyutil
import sparky
import sputil
import tkutil


class couple_dialog(tkutil.Dialog, tkutil.Stoppable):

  F1 = '1'
  F2 = '2'

  def __init__(self, session):

    SOL = '-fn SOL'
    POLY = '-fn POLY -time'
    BC_POLY = '-fn POLY -auto'
    BC_POLY_ORD = '-fn POLY -auto -ord '
    LP = '-fn LP -fb -pred  -ord '
    SP1 = '-fn SP -off 0.5 -end 0.98 -pow 2 -c 0.5'
    SP2 = '-fn SP -off 0.5 -end 0.98 -pow 2 -c 0.5'
    EM = '-fn EM -lb '
    ZF_Auto = '-fn ZF -auto'
    ZF1_Size = '-fn ZF -size 8192'
    ZF2_Size = '-fn ZF -size 1024'
    FT_ONLY = '-fn FT'
    FT_ALT = '-fn FT -alt'
    FT_AUTO = '-fn FT -auto'
    FT_INV = '-fn FT -inv'
    FT_NEG = '-fn FT -neg'
    FT_REAL = '-fn FT -real'
    EXT_LEFT = '-fn EXT -left'
    EXT_RIGHT = '-fn EXT -right'
    EXT_MID = '-fn EXT -mid'
    EXT_XN = '-fn EXT -xn '
    EXT_X1XN = '-fn EXT -x1  -xn '

    self.ipap_root = os.getcwd()
    self.session = session
    self.project = session.project
    self.filenames = []
    self.coupled_peaks = []

#    os.chdir('/scratch2/shaman/s3e')

    tkutil.Dialog.__init__(self, session.tk, 'IPAP')

# ----------------------------------------------------------------------------
# BEGIN SER-FILE DIALOG
# ----------------------------------------------------------------------------
#
    f = Tkinter.Frame(self.top)
    f.pack(side = 'top', anchor = 'w')


    dt_frame = Tkinter.Frame(f)
    dt_frame.pack(side = 'top', anchor = 'w')

    alpha_dialog = Tkinter.Frame(f)
    alpha_dialog.pack(side = 'top', anchor = 'w')

    asp = tkutil.file_field(alpha_dialog, 'File1: ', 'serfile', width = 60)
    asp.frame.pack(side = 'top', anchor = 'w')
    asp.set(os.getcwd() + '/')
    self.a_ser_path = asp

    beta_dialog = Tkinter.Frame(f)
    beta_dialog.pack(side = 'top', anchor = 'w')

    bsp = tkutil.file_field(beta_dialog, 'File2: ', 'serfile', width = 60)
    bsp.frame.pack(side = 'top', anchor = 'e')
    bsp.set(os.getcwd() + '/')
    self.b_ser_path = bsp

    id_frame = Tkinter.Frame(f)
    id_frame.pack(side = 'top', anchor = 'w')
    id = radio.interleaved_field(id_frame, 'Interleaved spectra? ', beta_dialog, alpha_dialog, ('yes', 1), ('no', 0))
    id.frame.pack(side = 'top', anchor = 'w')
    id.set_value(0)
    self.interleaved_state = id.variable

#
# ----------------------------------------------------------------------------
# END SER-FILE DIALOG
# ----------------------------------------------------------------------------
    
    fid_frame = Tkinter.Frame(self.top)
    handling_frame = Tkinter.Frame(self.top)

    dt = radio.data_type_field(dt_frame, 'Type of input data ', fid_frame, f, id, alpha_dialog, beta_dialog, id_frame, handling_frame, ('FID', 0), ('NMRPipe ft2-files', 1), ('Sparky ucsf-files', 2))
    dt.frame.pack(side = 'top', anchor = 'w')
    dt.set_value(0)
    self.data_type = dt.variable

# ----------------------------------------------------------------------------
# BEGIN CONVERSION DIALOG
# ----------------------------------------------------------------------------
#
    conversion_frame = Tkinter.Frame(fid_frame)
    conversion_frame.pack(side = 'top', anchor = 'w')

    cbutton = tkutil.checkbutton(conversion_frame, 'Show conversion dialog', 0)
    cbutton.button.pack(side = 'top', anchor = 'w')
    self.cbutton = cbutton

    conversion_dialog = Tkinter.Frame(fid_frame)

    r = 0

    w2 = Tkinter.Label(conversion_dialog, text = 'Conversion script for NMRPipe')
    w2.grid(row = r, column = 0)

    w3 = Tkinter.Label(conversion_dialog, text = 'Output from conversion')
    w3.grid(row = r, column = 1)
    r = r + 1

    fc = tkutil.scrolling_text(conversion_dialog, height = 13, width = 80)
    fc.frame.grid(row = r, column = 0)
    self.fid_com = fc.text

    co = tkutil.scrolling_text(conversion_dialog, height = 13)
    co.frame.grid(row = r, column = 1)
    self.conversion_output = co.text
    r = r + 1

    fcbr = tkutil.button_row(conversion_dialog,
                             ('Generate by NMRPipe', self.read_parameters_cb),
                             ('Generate by S3EPY', self.read_bruker_cb),
                             ('Load script', self.load_fid_com_cb),
                             ('Apply', self.apply_cb),
                             ('Clear script', self.clear_fid_com_cb),
                             ('Save script as', self.save_fid_com_cb),
                             ('Quit', self.close_cb))
    fcbr.frame.grid(row = r, column = 0)

    cobr = tkutil.button_row(conversion_dialog,
                             ('Clear output', self.clear_conversion_output_cb),
                             ('Quit', self.close_cb))
    cobr.frame.grid(row = r, column = 1)
    r = r + 1

    cbutton.show_widget_cb(conversion_dialog, None)
    cbutton.map_widget(conversion_dialog)
#
# ----------------------------------------------------------------------------
# END CONVERSION DIALOG
# ----------------------------------------------------------------------------
    
# ----------------------------------------------------------------------------
# BEGIN PROCESSING DIALOG
# ----------------------------------------------------------------------------
#    
    processing_frame = Tkinter.Frame(fid_frame)
    processing_frame.pack(side = 'top', anchor = 'w')

    pbutton = tkutil.checkbutton(processing_frame, 'Show processing dialog', 0)
    pbutton.button.pack(side = 'top', anchor = 'w')

    processing_dialog = Tkinter.Frame(processing_frame)
    processing_dialog.pack(side = 'top', anchor = 'w')
    pdr = 0
   
# ----------------------------------------------------------------------------
# first column
    w4 = Tkinter.Label(processing_dialog, text = 'Processing paramaters:')
    w4.grid(row = pdr, column = 0, columnspan = 3)
    pdr = pdr + 1

    w5 = Tkinter.Label(processing_dialog, text = 'Direct dimension:')
    w5.grid(row = pdr, column = 0, columnspan = 2)
    pdr = pdr + 1

    sf = radio.button_field(processing_dialog, 'Solvent filtration method:', 0,
                             ('None', None),
                             ('SOL', SOL),
                             ('POLY', POLY))
    sf.frame.grid(row = pdr, column = 0, sticky = 'nw')
    pdr = pdr + 1
    self.solvent_filter_dialog = sf
    self.solvent_filter = sf.entry_field.variable

    ps1 = radio.phase_correction_dialog2(processing_dialog, 'Phase correction:')
    ps1.frame.grid(row = pdr, column = 0, sticky = 'nw')
    self.phase1_dialog = ps1
    pdr = pdr + 1
  
    ext0 = radio.button_field(processing_dialog, 'FID truncation:', 0,
                             ('None', None),
                             ('to xn', EXT_XN),
                             ('from x1 to xn', EXT_X1XN))
    ext0.frame.grid(row = pdr, column = 0, sticky = 'nw')
    pdr = pdr + 1
    self.extract_region0_dialog = ext0
    self.extract_region0 = ext0.entry_field.variable

    pod = Tkinter.Frame(processing_dialog)
    pod.grid(row = pdr, column = 0, rowspan = 3)
    pdr = pdr + 1
    
    w6 = Tkinter.Label(pod, text = 'Processing output:')
    w6.pack(side = 'top', anchor = 'nw')
    
    po = tkutil.scrolling_text(pod, height = 13)
    po.frame.pack(side = 'top', anchor = 'nw')
    self.processing_output = po.text
    
# ----------------------------------------------------------------------------
# second column
    pdr = 2
    
    lp1 = radio.button_field(processing_dialog, 'Linear prediction method:', 0,
                             ('None', None),
                             ('LP', LP))
    lp1.frame.grid(row = pdr, column = 1, sticky = 'nw')
    pdr = pdr + 1
    self.linear_prediction1_dialog = lp1
    self.linear_prediction1 = lp1.entry_field.variable

    af1 = radio.button_field(processing_dialog, 'Apodization function:', 1,
                             ('None', None),
                             ('SP', SP1),
                             ('EM', EM))
    af1.frame.grid(row = pdr, column = 1, sticky = 'nw')
    pdr = pdr + 1
    self.apodization_function1_dialog = af1
    self.apodization_function1 = af1.entry_field.variable

    zf1 = radio.button_field(processing_dialog, 'Zero fill options:', 1,
                             ('None', None),
                             ('auto', ZF_Auto),
                             ('size (eg. 4096, 8192)', ZF1_Size))
    zf1.frame.grid(row = pdr, column = 1, sticky = 'nw')
    pdr = pdr + 1
    self.zero_fill1_dialog = zf1
    self.zero_fill1 = zf1.entry_field.variable

    ft1 = radio.button_field(processing_dialog, 'Fourier transform options:', 0,
                             ('None', FT_ONLY),
                             ('alt', FT_ALT),
                             ('auto', FT_AUTO),
                             ('inv', FT_INV),
                             ('neg', FT_NEG),
                             ('real', FT_REAL))
    ft1.frame.grid(row = pdr, column = 1, sticky = 'nw')
    pdr = pdr + 1
    self.fourier_transform1_dialog = ft1
    self.fourier_transform1 = ft1.entry_field.variable

    bc1 = radio.button_field(processing_dialog, 'Baseline correction method:', 0,
                             ('None', None),
                             ('POLY auto', BC_POLY),
                             ('POLY auto ord', BC_POLY_ORD))
    bc1.frame.grid(row = pdr, column = 1, sticky = 'nw')
    pdr = pdr + 1
    self.baseline_correction1_dialog = bc1
    self.baseline_correction1 = bc1.entry_field.variable
 
    ext1 = radio.button_field(processing_dialog, 'Extract region options:', 0,
                             ('None', None),
                             ('left', EXT_LEFT),
                             ('right', EXT_RIGHT),
                             ('mid', EXT_MID),
                             ('to xn', EXT_XN),
                             ('from x1 to xn', EXT_X1XN))
    ext1.frame.grid(row = pdr, column = 1, sticky = 'nw')
    pdr = pdr + 1
    self.extract_region1_dialog = ext1
    self.extract_region1 = ext1.entry_field.variable

# ----------------------------------------------------------------------------
# third column
    pdr = 1
   
    w5 = Tkinter.Label(processing_dialog, text = 'Indirect dimension:')
    w5.grid(row = pdr, column = 2)
    pdr = pdr + 1
    
    lp2 = radio.button_field(processing_dialog, 'Linear prediction method:', 0,
                             ('None', None),
                             ('LP', LP))
    lp2.frame.grid(row = pdr, column = 2, sticky = 'nw')
    pdr = pdr + 1
    self.linear_prediction2_dialog = lp2
    self.linear_prediction2 = lp2.entry_field.variable

    af2 = radio.button_field(processing_dialog, 'Apodization function:', 1,
                             ('None', None),
                             ('SP', SP2),
                             ('EM', EM))
    af2.frame.grid(row = pdr, column = 2, sticky = 'nw')
    pdr = pdr + 1
    self.apodization_function2_dialog = af2
    self.apodization_function2 = af2.entry_field.variable

    zf2 = radio.button_field(processing_dialog, 'Zero fill options:', 1,
                             ('None', None),
                             ('auto', ZF_Auto),
                             ('size (eg. 4096, 8192)', ZF2_Size))
    zf2.frame.grid(row = pdr, column = 2, sticky = 'nw')
    pdr = pdr + 1
    self.zero_fill2_dialog = zf2
    self.zero_fill2 = zf2.entry_field.variable

    ft2 = radio.button_field(processing_dialog, 'Fourier transform options:', 1,
                             ('None', FT_ONLY),
                             ('alt', FT_ALT),
                             ('auto', FT_AUTO),
                             ('inv', FT_INV),
                             ('neg', FT_NEG),
                             ('real', FT_REAL))
    ft2.frame.grid(row = pdr, column = 2, sticky = 'nw')
    pdr = pdr + 1
    self.fourier_transform2_dialog = ft2
    self.fourier_transform2 = ft2.entry_field.variable

    bc2 = radio.button_field(processing_dialog, 'Baseline correction method:', 0,
                             ('None', None),
                             ('POLY auto', BC_POLY),
                             ('POLY auto ord', BC_POLY_ORD))
    bc2.frame.grid(row = pdr, column = 2, sticky = 'nw')
    pdr = pdr + 1
    self.baseline_correction2_dialog = bc2
    self.baseline_correction2 = bc2.entry_field.variable

    ext2 = radio.button_field(processing_dialog, 'Extract region options:', 0,
                             ('None', None),
                             ('left', EXT_LEFT),
                             ('right', EXT_RIGHT),
                             ('mid', EXT_MID),
                             ('to xn', EXT_XN),
                             ('from x1 to xn', EXT_X1XN))
    ext2.frame.grid(row = pdr, column = 2, sticky = 'nw')
    pdr = pdr + 1
    self.extract_region2_dialog = ext2
    self.extract_region2 = ext2.entry_field.variable
    
    pobr = tkutil.button_row(processing_dialog,
                             ('Test processing parameters', self.test_processing_parameters_cb),
                             ('Run nmrDraw', self.run_nmrdraw_cb),
                             ('Process spectra', self.process_spectra_cb),
                             ('Clear processing output', self.clear_processing_output_cb),
                             ('Reset to defaults', self.reset_processing_dialog_cb),
                             ('Quit', self.close_cb))
    pobr.frame.grid(row = pdr, column = 0, columnspan = 3)

    pbutton.show_widget_cb(processing_dialog, None)
    pbutton.map_widget(processing_dialog)
#
# ----------------------------------------------------------------------------
# END PROCESSING DIALOG
# ----------------------------------------------------------------------------

    handling_frame.pack(side = 'top', anchor = 'w')

    hbutton = tkutil.checkbutton(handling_frame, 'Show spectra handling dialog', 0)
    hbutton.button.pack(side = 'top', anchor = 'nw')

    spectra_handling_dialog = Tkinter.Frame(handling_frame)
    spectra_handling_dialog.pack(side = 'top', anchor = 'w')

    hc = tkutil.entry_row(spectra_handling_dialog, 'Coefficients for subspectra addition and subtraction: ',
                          ('add c1', '1', 3), ('add c2', '1', 3),
                          ('sub c1', '1', 3), ('sub c2', '1', 3))
    (self.add_c1,
     self.add_c2,
     self.sub_c1,
     self.sub_c2) = hc.variables
    hc.frame.pack(side = 'top', anchor = 'w')

    hod = Tkinter.Frame(spectra_handling_dialog)
    hod.pack(side = 'top', anchor = 'w')
 
    w7 = Tkinter.Label(hod, text = 'Spectra handling output:')
    w7.pack(side = 'top', anchor = 'nw')
    
    ho = tkutil.scrolling_text(hod, height = 5, width = 77)
    ho.frame.pack(side = 'top', anchor = 'nw')
    self.handling_output = ho.text
    
    hobr = tkutil.button_row(spectra_handling_dialog,
                             ('Add/sub spectra', self.addsub_spectra_cb),
                             ('Clear handling output', self.clear_handling_output_cb),
                             ('Quit', self.close_cb))
    hobr.frame.pack()

    hbutton.show_widget_cb(spectra_handling_dialog, None)
    hbutton.map_widget(spectra_handling_dialog)

# ----------------------------------------------------------------------------
# BEGIN SPECTRA ASSIGNEMENT DIALOG
# ----------------------------------------------------------------------------
#    
    assign_frame = Tkinter.Frame(self.top)
    assign_frame.pack(side = 'bottom', anchor = 'w')

    abutton = tkutil.checkbutton(assign_frame, 'Show spectra assign dialog', 0)
    abutton.button.pack(side = 'top', anchor = 'nw')

    spectra_assign_dialog = Tkinter.Frame(assign_frame)
    spectra_assign_dialog.pack(side = 'top', anchor = 'w')

    pda = tkutil.entry_field(spectra_assign_dialog, 'Peak displacement to IPAP A:', '', 9, 'ppm')
    pda.frame.pack(side = 'top', anchor = 'w')
    self.peak_displacement_to_A_choice = pda.variable

    pdb = tkutil.entry_field(spectra_assign_dialog, 'Peak displacement to IPAP B:', '', 9, 'ppm')
    pdb.frame.pack(side = 'top', anchor = 'w')
    self.peak_displacement_to_B_choice = pdb.variable

    cd = tkutil.option_menu(spectra_assign_dialog, 'HSQC coupled in dimension F',
                            (self.F1,
                             self.F2), initial = '')
    cd.frame.pack(side = 'top', anchor = 'w')
    self.coupled_dimension_choice = cd.variable

    aod = Tkinter.Frame(spectra_assign_dialog)
    aod.pack(side = 'top', anchor = 'w')
 
    w7 = Tkinter.Label(aod, text = 'Spectra assign output:')
    w7.pack(side = 'top', anchor = 'nw')
    
    ao = tkutil.scrolling_text(aod, height = 5, width = 77)
    ao.frame.pack(side = 'top', anchor = 'nw')
    self.assign_output = ao.text
    
    aobr = tkutil.button_row(spectra_assign_dialog,
                             ('Template assignment', self.template_assignment_cb),
                             ('Open spectra', self.open_cb),
                             ('Assign spectra', self.assign_cb),
                             ('Clear assign output', self.clear_assign_output_cb),
                             ('Quit', self.close_cb))
    aobr.frame.pack()

    abutton.show_widget_cb(spectra_assign_dialog, None)
    abutton.map_widget(spectra_assign_dialog)
#
# ----------------------------------------------------------------------------
# END SPECTRA ASSIGNEMENT DIALOG
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# BEGIN COUPLINGS EVALUATION DIALOG
# ----------------------------------------------------------------------------
#    
    ebutton = tkutil.checkbutton(assign_frame, 'Show coupling evaluation dialog', 0)
    ebutton.button.pack(side = 'top', anchor = 'sw')

    couplings_evaluation_dialog = Tkinter.Frame(assign_frame)
    couplings_evaluation_dialog.pack(side = 'top', anchor = 'w')

    peak_fitting_method_dialog = Tkinter.Frame(couplings_evaluation_dialog)
    peak_fitting_method_dialog.pack(anchor = 'w')
    
    fph = tkutil.entry_field(couplings_evaluation_dialog, 'Fit in ', '90.0', 9, '% of peak height')
    fph.frame.pack(side = 'top', anchor = 'w')
    self.fit_peak_height = fph.variable

    peak_fitting_method_dialog = Tkinter.Frame(couplings_evaluation_dialog)
    peak_fitting_method_dialog.pack(anchor = 'w')
    
    self.peak_fitting_method = Tkinter.StringVar(peak_fitting_method_dialog)
    self.peak_fitting_method.set('pi')
    
    pfm = Tkinter.Label(peak_fitting_method_dialog, text = 'Peak fitting method')
    pfm.grid(row = 0, column = 0, sticky = 'w')
    pirb = Tkinter.Radiobutton(peak_fitting_method_dialog, text = 'pi', variable = self.peak_fitting_method, value = 'pi', highlightthickness = 0, command = self.update_peak_fitting_method)
    pirb.grid(row = 0, column = 1, sticky = 'w')
    pcrb = Tkinter.Radiobutton(peak_fitting_method_dialog, text = 'pc', variable = self.peak_fitting_method, value = 'pc', highlightthickness = 0, command = self.update_peak_fitting_method)
    pcrb.grid(row = 0, column = 2, sticky = 'w')

    coupling_output_dialog = Tkinter.Frame(couplings_evaluation_dialog)
    coupling_output_dialog.pack(side = 'top', anchor = 'w')

    cop = tkutil.file_field(coupling_output_dialog, 'output file: ', 'textfile', width = 59)
    cop.frame.pack(side = 'top', anchor = 'w')
    cop.set(os.getcwd() + '/couplings')
    self.output_path = cop

    eod = Tkinter.Frame(couplings_evaluation_dialog)
    eod.pack(side = 'top', anchor = 'w')
 
    w7 = Tkinter.Label(eod, text = 'Coupling evaluation output:')
    w7.pack(side = 'top', anchor = 'nw')
    
    eo = tkutil.scrolling_text(eod, height = 9, width = 77)
    eo.frame.pack(side = 'top', anchor = 'nw')
    self.evaluation_output = eo.text
    
    eobr = tkutil.button_row(couplings_evaluation_dialog,
#                            ('Fit peaks', self.fit_peaks_cb),
                             ('Evaluate couplings', self.evaluate_couplings_cb),
#                            ('Plot couplings', self.plot_couplings_cb),
                             ('Clear assign output', self.clear_evaluation_output_cb),
                             ('Quit', self.close_cb))
    eobr.frame.pack()

    ebutton.show_widget_cb(couplings_evaluation_dialog, None)
    ebutton.map_widget(couplings_evaluation_dialog)

#
# ----------------------------------------------------------------------------
# END COUPLINGS EVALUATION DIALOG
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
#
  def save_fid_com_cb(self):
  
    self.save_widget(self.fid_com, 'Save conversion script As')

# ----------------------------------------------------------------------------
#
  def save_ft2_com_cb(self):
  
    self.save_widget(self.ft2_com, 'Save processing script As')

# ----------------------------------------------------------------------------
#
  def save_widget(self, widget, title):
  
    path = tkutil.save_file(self.top, title, 'Any')
    self.write_file(path, 'w', widget.get(1.0, 'end'))

# ----------------------------------------------------------------------------
#
  def write_file(self, path, mode, content, write_heading = 0):
    
    if path:
      file = open(path, mode)
      if write_heading and self.heading:
        file.write(self.heading['text'] + '\n')
      file.write(content)
      file.close()
    
# ----------------------------------------------------------------------------
#
  def load_fid_com_cb(self):

    self.load2widget(self.fid_com, 'Load conversion script')

# ----------------------------------------------------------------------------
#
  def load_ft2_com_cb(self):

    self.load2widget(self.ft2_com, 'Load processing script')

# ----------------------------------------------------------------------------
#
  def load2widget(self, widget, title):

    path = tkutil.load_file(self.top, title, 'Any')
    if path:
      script = self.read_file(path, 'r')
      widget.insert('end', script)

# ----------------------------------------------------------------------------
#
  def read_file(self, path, mode):
    
    f = open(path, mode)
    file = f.read()
    f.close()
    return file
    
# ----------------------------------------------------------------------------
#

  def read_parameters_cb(self):
    
    if self.a_ser_path.get():
      self.run_bruker()

# ----------------------------------------------------------------------------
#
  def run_bruker(self):

    self.execute_shell_command(["bruker"], cwd = self.get_path(self.a_ser_path.get()))
    
# ----------------------------------------------------------------------------
#
  def execute_shell_command(self, command, cwd = None):

    #load standard subprocess module
    module_path = sys.prefix + '/lib/python' + `sys.version_info[0]` + '.' + `sys.version_info[1]` + '/'
    subprocess = imp.load_source('subprocess', module_path + 'subprocess.py')
    f=open('/dev/null','w')    
    subprocess.Popen(command, shell=True, stdout = f, stderr = subprocess.STDOUT, cwd=cwd, close_fds=True)
    
# ----------------------------------------------------------------------------
#

  def read_bruker_cb(self):
    
    if self.a_ser_path.get():
      self.read_bruker()

# ----------------------------------------------------------------------------
#
  def read_bruker(self):

    rv = re.compile("(?P<path>.*/)""(?P<ser>.*$)")
    self.acqus_path = self.get_path(self.a_ser_path.get()) + 'acqus'
    self.acqu2s_path = self.get_path(self.a_ser_path.get()) + 'acqu2s'
   
    if self.acqus_path:
      self.acqus = self.find_parameters(self.acqus_path, 'DECIM', 'TD', 'SFO1', 'SW', 'O1', 'AQ_mod')
#      self.acqus['CNST5'] = self.find_cnst5(self.acqus_path)
    if self.acqu2s_path:
      self.acqu2s = self.find_parameters(self.acqu2s_path, 'TD', 'FnMODE', 'SFO1', 'SW', 'O1')

    if self.acqus and self.acqu2s:
      script = self.create_conversion_script()
      self.fid_com.insert('end', script)

# ----------------------------------------------------------------------------
#
  def find_parameters(self, path, *patterns):
    
    parameters={}
    
    if path:
      file = self.read_file(path, 'r')
      for pattern in patterns:
        search_result = re.compile("(?<=\$" + pattern + "= )\d+(.\d+)?").search(file)
        if search_result:
          parameters[pattern] = search_result.group(0)

      if int(float(parameters['SFO1'])) == 600 or int(float(parameters['SFO1'])) == 500:
        parameters['LAB'] = '1H'
      elif int(float(parameters['SFO1'])) == 150 or int(float(parameters['SFO1'])) == 125:
        parameters['LAB'] = '13C'
      elif int(float(parameters['SFO1'])) == 60 or int(float(parameters['SFO1'])) == 50:
        parameters['LAB'] = '15N'
    
    return parameters
    
# ----------------------------------------------------------------------------
#
# def find_cnst5(self, path):
#
#   if path:
#     file = self.read_file(path, 'r')
#
#   search_result = re.compile("(?<=\$CNST= \(0....\))(?P<CNST14>(.)?\n\d+(\.\d+)? \d+(\.\d+)? \d+(\.\d+)? \d+(\.\d+)? \d+(\.\d+)? )(?P<CNST5>\d+(\.\d+)?)(?P<CNST6> .*)").search(file)
#   if search_result:
#     cnst5 = search_result.group('CNST5')
#     self.cnst5_entry.entry.delete('0', 'end')
#     self.cnst5_entry.entry.insert('end', '%4.1f' % float(cnst5))
#     
#   return cnst5
#
# ----------------------------------------------------------------------------
#
  def create_conversion_script(self):
    
    script = '#!/bin/csh\n'
    script = script + 'bruk2pipe -in ser -bad 0.0 -swap -DMX'
    script = script +  ' -decim ' + self.acqus['DECIM'] + ' -dspfvs 12   '
    script = script + '\\\n'
    
    xn = xt = float(self.acqus['TD']) / 2  # begin bruker feature
    while (xn%32) != 0:
      xn = xn + 1
    xn = xn * 2                       # end bruker feature
    script = script + string.ljust(' -xN', 16) + string.ljust(`int(xn)`, 15)
    script = script + string.ljust('-yN', 15) + string.ljust(self.acqu2s['TD'], 15)
    script = script + '\\\n'
    
    yt=float(self.acqu2s['TD']) / 2
    script = script + string.ljust(' -xT', 16) + string.ljust(`int(xt)`, 15)
    script = script + string.ljust('-yT', 15) + string.ljust(`int(yt)`, 15)
    script = script + '\\\n'
    
    script = script + string.ljust(' -xMODE', 16)
    if self.acqus['AQ_mod'] == '3':
      script = script + string.ljust('DQD', 15)
    script = script + string.ljust('-yMODE', 15)
    if self.acqu2s.has_key('FnMODE'):
      if self.acqu2s['FnMODE'] == '5':
        script = script + string.ljust('States-TPPI', 15)
      elif self.acqu2s['FnMODE'] == '6':
        script = script + string.ljust('Echo-Antiecho', 15)
    # defaults FnMODE to States-TPPI
    else:
      script = script + string.ljust('States-TPPI', 15)
    script = script + '\\\n'

    xsw = float(self.acqus['SW']) * float(self.acqus['SFO1'])
    ysw = float(self.acqu2s['SW']) * float(self.acqu2s['SFO1'])
    script = script + string.ljust(' -xSW', 16) + string.ljust("%8.3f" % xsw, 15)
    script = script + string.ljust('-ySW', 15) + string.ljust("%8.3f" % ysw, 15)
    script = script + '\\\n'
    
    script = script + string.ljust(' -xOBS', 16) + string.ljust("%7.3f" % float(self.acqus['SFO1']), 15)
    script = script + string.ljust('-yOBS', 15) + string.ljust("%7.3f" % float(self.acqu2s['SFO1']), 15)
    script = script + '\\\n'
    
    xcar = float(self.acqus['O1']) / float(self.acqus['SFO1']) + self.reference(self.acqus)
    ycar = float(self.acqu2s['O1']) / float(self.acqu2s['SFO1']) + self.reference(self.acqu2s)
    script = script + string.ljust(' -xCAR', 16) + string.ljust("%1.3f" % xcar, 15)
    script = script + string.ljust('-yCAR', 15) + string.ljust("%7.3f" % ycar, 15)
    script = script + '\\\n'
    
    script = script + string.ljust(' -xLAB', 16) + string.ljust(self.acqus['LAB'], 15)
    script = script + string.ljust('-yLAB', 15) + string.ljust(self.acqu2s['LAB'], 15)
    script = script + '\\\n'
    
    script = script + string.ljust(' -ndim', 16) + string.ljust('2', 15)
    script = script + string.ljust('-aq2D', 15) + string.ljust('States', 15)
    script = script + '\\\n'
    
    script = script + ' -out test.fid -verb -ov \n'

    return script

# ----------------------------------------------------------------------------
#
  def reference(self, parameters):

   nucleus = parameters['LAB']
   if nucleus == '1H':
     result = 0.0
   elif nucleus == '13C':
     result = 2.7
   elif nucleus == '15N':
     result = -0.61
   else:
     result = 0.0

   return result
   
# ----------------------------------------------------------------------------
#
  def apply_cb(self):

    execute = 0

    #test for FID1
    if self.a_ser_path.get():
      execute = 1
    else:
      self.conversion_output.insert('end', 'Please specify the "FID1 file" path\n')

    #test for interleaved spectra
    if execute and self.interleaved_state.get():
      execute = 1

    #test for conversion script
    if execute:
      if self.fid_com.get(1.0, 'end') != '\n':
        execute = 1
      else:
        execute = 0
        self.conversion_output.insert('end', 'Please fill in the "Conversion script"\n')

    #test for FID2 for non-interleaved spectra
    if execute and not self.interleaved_state.get():
      if self.b_ser_path.get():
        execute = 1
      else:
        execute = 0
        self.conversion_output.insert('end', 'Please specify the "FID2 file" path\n')

    #test for FID1 != FID2 for non-interleaved spectra
    if execute and not self.interleaved_state.get():
      if self.a_ser_path.get() != self.b_ser_path.get():
        execute = 1
      else:
        execute = 0
        self.conversion_output.insert('end', 'WARNING !!! You have specified the same filename for the "FID1 file" and the "FID2 file"\n')

    #if tests passsed then execute conversion
    if execute:
      self.apply()

# ----------------------------------------------------------------------------
#
  def apply(self):

    self.conversion_output.insert('end', 'Conversion of the FID1 file:\n')
    output = self.execute_script(self.get_path(self.a_ser_path.get()), 'fid.com', 
                                                    self.fid_com.get(1.0, 'end'))
    self.conversion_output.insert('end', output[0] + output[1])
    self.conversion_output.insert('end', '\n')
    self.conversion_output.insert('end', '\n')
    
    #if interleaved then split to ...
    if self.interleaved_state.get():
      #... odd rows for FID1
      subspectrum_name = 'test1'
      self.conversion_output.insert('end', 'Splitting interleaved experiment to ' + subspectrum_name + '.fid\n')
      output = self.execute_script(self.get_path(self.a_ser_path.get()), 'split_' + subspectrum_name + '.com', 
                                                     self.create_split_script(subspectrum_name, 1, 0))
      self.conversion_output.insert('end', output[0] + output[1])
      #... even rows for FID2
      subspectrum_name = 'test2'
      self.conversion_output.insert('end', 'Splitting interleaved experiment to ' + subspectrum_name + '.fid\n')
      output = self.execute_script(self.get_path(self.a_ser_path.get()), 'split_' + subspectrum_name + '.com', 
                                                     self.create_split_script(subspectrum_name, 0, 1))
      self.conversion_output.insert('end', output[0] + output[1])
      self.conversion_output.insert('end', '\n')
      self.conversion_output.insert('end', '\n')
    #if not interleaved, do normal conversion of spectrum
    else:
      self.conversion_output.insert('end', 'Conversion of the FID2 file:\n')
      output = self.execute_script(self.get_path(self.b_ser_path.get()), 'fid.com', 
                                                      self.fid_com.get(1.0, 'end'))
      self.conversion_output.insert('end', output[0] + output[1])
      self.conversion_output.insert('end', '\n')
      self.conversion_output.insert('end', '\n')
      #and rename both converted subspectra to test1.fid and test2.fid in a_ser_path directory, respectively
      self.execute_shell_command(["mv " + self.get_path(self.a_ser_path.get()) + "test.fid " + self.get_path(self.a_ser_path.get()) + "test1.fid"])
      self.execute_shell_command(["mv " + self.get_path(self.b_ser_path.get()) + "test.fid " + self.get_path(self.a_ser_path.get()) + "test2.fid"])

# ----------------------------------------------------------------------------
#
  def create_split_script(self, subspectrum_name, c1, c2, axis = 'Y'):

      split_script = '#!/bin/csh\n'
      split_script = split_script + 'nmrPipe   -in test.fid \\\n'
      split_script = split_script + ' | nmrPipe -fn COADD -axis ' + axis + ' -cList ' + `c1` + ' ' + `c2` + ' -time \\\n'
      split_script = split_script + ' | nmrPipe -out ' + subspectrum_name + '.fid -ov \n'
      
      return split_script

# ----------------------------------------------------------------------------
#
  def execute_script(self, path, name, script, command='sh '):

    os.chdir(path)
    self.write_file(name, 'w', script)
    
    r, w, e = popen2.popen3('csh')
    
    w.write('cd ' + path + '\n')
    w.write(command + name + '\n')
    w.write('exit\n')
    
    w.close()
    
    stdout = r.read()
    stderr = e.read()
    
    r.close()
    e.close()
    
    return stdout, stderr
    
# ----------------------------------------------------------------------------
#
  def execute_command(self, command, path='', arguments=''):

    r, w, e = popen2.popen3('csh')
    
    if path:
      w.write('cd ' + path + '\n')
    w.write(command + ' ' + arguments + '\n')
    w.write('exit\n')
    
    w.close()
    
    stdout = r.read()
    stderr = e.read()
    
    r.close()
    e.close()
    
    return stdout, stderr
    
# ----------------------------------------------------------------------------
#
  def clear_fid_com_cb(self):
    
    self.fid_com.delete(1.0, 'end')

# ----------------------------------------------------------------------------
#
  def clear_conversion_output_cb(self):
    
    self.conversion_output.delete(1.0, 'end')

# ----------------------------------------------------------------------------
#
  def test_processing_parameters_cb(self):

    if self.a_ser_path.get():
      if os.access(self.get_path(self.a_ser_path.get()) + 'test1.fid', os.R_OK) == True:
        self.test_processing_parameters()
      else:
        self.processing_output.insert('end', 'Please convert the spectra before processing, test1.fid not found.\n')

# ----------------------------------------------------------------------------
#
  def test_processing_parameters(self):
    
    output = self.execute_script(self.get_path(self.a_ser_path.get()), 'ft2.com', 
                                   self.create_processing_script())

    self.processing_output.insert('end', output[0] + output[1])

# ----------------------------------------------------------------------------
#
  def run_nmrdraw_cb(self):
    
    self.run_nmrdraw()
      
# ----------------------------------------------------------------------------
#
  def run_nmrdraw(self):
    
    r, w, e = popen2.popen3('csh')
    if self.a_ser_path.get():
      w.write('cd ' + self.get_path(self.a_ser_path.get()) + '\n')
    w.write('nmrDraw\n')
    w.write('exit\n')

    w.close()
    r.close()
    e.close()
    
    return

# ----------------------------------------------------------------------------
#
  def process_spectra_cb(self):

    if self.a_ser_path.get():
      if os.access(self.get_path(self.a_ser_path.get()) + 'test1.fid', os.R_OK) == True:
        if os.access(self.get_path(self.a_ser_path.get()) + 'test2.fid', os.R_OK) == True:
          self.process_spectra()
        else:
          self.processing_output.insert('end', 'test2.fid not found\n')
      else:
        self.processing_output.insert('end', 'test1.fid not found\n')
    else:
      self.processing_output.insert('end', 'Please specify the "FID1 file" path\n')

# ----------------------------------------------------------------------------
#
  def process_spectra(self):
    
    self.process_spectrum(self.processing_output, self.get_path(self.a_ser_path.get()), 'test1', 'Processing of the fid1')
    self.process_spectrum(self.processing_output, self.get_path(self.a_ser_path.get()), 'test2', 'Processing of the fid2')

# ----------------------------------------------------------------------------
#
  def process_spectrum(self, output_dialog, path, subspectrum_name, text = ''):

    if text:
      output_dialog.insert('end', text + ' ... ')
    output = self.execute_script(path,
      subspectrum_name + '.com', 
      self.create_processing_script(subspectrum_name = subspectrum_name, output = subspectrum_name + '.ft2'))
    if output[1]:
      output_dialog.insert('end', 'ERROR:\n' + output[0] + output[1])
    else:
      output_dialog.insert('end', 'OK\n')
      
# ----------------------------------------------------------------------------
#
  def create_processing_script(self, ps2p0 = 0.0, ps2p1 = 0.0, subspectrum_name = 'test1', output = 'test.ft2'):

    script = '#!/bin/csh\n'
    script = script + 'nmrPipe   -in ' + subspectrum_name + '.fid \\\n'
    if self.solvent_filter.get():
      script = script + ' | nmrPipe ' + self.solvent_filter.get() + ' \\\n'
    if self.extract_region0.get():
      script = script + ' | nmrPipe ' + self.extract_region0.get() + ' -sw \\\n'
    if self.linear_prediction1.get():
      script = script + ' | nmrPipe ' + self.linear_prediction1.get() + ' \\\n'
    if self.apodization_function1.get():
      script = script + ' | nmrPipe ' + self.apodization_function1.get() + ' \\\n'
    else:
      script = script + ' | nmrPipe -fn SP -off 0.5 -end 0.98 -pow 2 -c 0.5 \\\n'
    if self.zero_fill1.get():
      script = script + ' | nmrPipe ' + self.zero_fill1.get() + ' \\\n'
    else:
      script = script + ' | nmrPipe -fn ZF -auto \\\n'
    if self.fourier_transform1.get():
      script = script + ' | nmrPipe ' + self.fourier_transform1.get() + ' \\\n'
    else:
      script = script + ' | nmrPipe -fn FT \\\n'
    if self.phase1_dialog.p0:
      script = script + ' | nmrPipe -fn PS -p0 ' + self.phase1_dialog.p0[0].get()
    else:
      script = script + ' | nmrPipe -fn PS -p0 0.0'
    if self.phase1_dialog.p1[0].get():
      script = script + ' -p1 ' + self.phase1_dialog.p1[0].get() + ' -di \\\n'
    else:
      script = script + ' -p1 0.0 -di \\\n'
    script = script + ' | nmrPipe -fn TP \\\n'
    if self.linear_prediction2.get():
      script = script + ' | nmrPipe ' + self.linear_prediction2.get() + ' \\\n'
    if self.apodization_function2.get():
      script = script + ' | nmrPipe ' + self.apodization_function2.get() + ' \\\n'
    else:
      script = script + ' | nmrPipe -fn SP -off 0.5 -end 0.98 -pow 2 -c 0.5 \\\n'
    if self.zero_fill2.get():
      script = script + ' | nmrPipe ' + self.zero_fill2.get() + ' \\\n'
    else:
      script = script + ' | nmrPipe -fn ZF -auto \\\n'
    if self.fourier_transform2.get():
      script = script + ' | nmrPipe ' + self.fourier_transform2.get() + ' \\\n'
    else:
      script = script + ' | nmrPipe -fn FT \\\n'
    if self.phase1_dialog.p0[1].get():
      script = script + ' | nmrPipe -fn PS -p0 ' + `ps2p0 + float(self.phase1_dialog.p0[1].get())`
    else:
      script = script + ' | nmrPipe -fn PS -p0 ' + `ps2p0`
    if self.phase1_dialog.p1[1].get():
      script = script + ' -p1 ' + `ps2p1 + float(self.phase1_dialog.p1[1].get())` + ' -di \\\n'
    else:
      script = script + ' -p1 ' + `ps2p1` + ' -di \\\n'
    script = script + ' | nmrPipe -fn TP \\\n'
    if self.baseline_correction1.get():
      script = script + ' | nmrPipe ' + self.baseline_correction1.get() + ' \\\n'
    if self.baseline_correction2.get():
      script = script + ' | nmrPipe -fn TP \\\n'
      script = script + ' | nmrPipe ' + self.baseline_correction2.get() + ' \\\n'
      script = script + ' | nmrPipe -fn TP \\\n'
    if self.extract_region1.get():
      script = script + ' | nmrPipe ' + self.extract_region1.get() + ' -sw \\\n'
    if self.extract_region2.get():
      script = script + ' | nmrPipe -fn TP \\\n'
      script = script + ' | nmrPipe ' + self.extract_region2.get() + ' -sw \\\n'
      script = script + ' | nmrPipe -fn TP \\\n'
    script = script + ' | nmrPipe -out ' + output + ' -ov \n'
    
    return script

# ----------------------------------------------------------------------------
#
  def combine_spectra(self, output_widget, inName1, inName2, outName, Action = 'add', c1 = 1.0, c2 = 1.0, trailer = ''):
    
    output_widget.insert('end', 'Combining spectra in ratio '
                          + string.zfill('%5.3f' % c1, 4) 
                          + ':'
                          + string.zfill('%5.3f' % c2, 4))
    if trailer != '':
      output_widget.insert('end', trailer)
    output_widget.insert('end', ' ... ')
    output = self.addNMR(inName1, inName2, outName, Action, c1, c2)
    if output[1]:
      output_widget.insert('end', 'ERROR:\n' + output[0] + output[1])
    else:
      output_widget.insert('end', 'OK\n')
    
    ucsf_file = re.compile("(?P<name>.*)""(?P<suffix>\.ft2$)").search(outName).group('name') + '.ucsf'

    output_widget.insert('end', 'Conversion of spectrum to UCSF-format ... ')
    output = self.pipe2ucsf(outName, ucsf_file)
    if output[1]:
      output_widget.insert('end', 'ERROR:\n' + output[0] + output[1])
    else:
      output_widget.insert('end', 'OK\n')

# ----------------------------------------------------------------------------
#
  def addNMR(self, inName1, inName2, outName, Action, c1, c2):
    
    r, w, e = popen2.popen3('csh')
    
    w.write('cd ' + self.get_path(inName1) + '\n')
    w.write('addNMR -in1 ' + inName1 + ' -in2 ' + inName2 + ' -out ' + outName + ' -' + Action + ' -c1 ' + `c1` + ' -c2 ' + `c2` + '\n')
    w.write('exit\n')
    
    w.close()
    
    stdout = r.read()
    stderr = e.read()
    
    r.close()
    e.close()
    
    return stdout, stderr
    
# ----------------------------------------------------------------------------
#
  def pipe2ucsf(self, pipe_file, ucsf_file):

    r, w, e = popen2.popen3('csh')
    
    w.write('pipe2ucsf ' + pipe_file + ' ' + ucsf_file + '\n')
    w.write('exit\n')
    
    w.close()
    
    stdout = r.read()
    stderr = e.read()
    
    r.close()
    e.close()
    
    return stdout, stderr
  

# ----------------------------------------------------------------------------
#
  def reset_processing_dialog_cb(self):

   self.solvent_filter_dialog.reset_cb()

   self.phase1_dialog.reset_cb()
   self.extract_region0_dialog.reset_cb()
   
   self.baseline_correction1_dialog.reset_cb()
   self.apodization_function1_dialog.reset_cb()
   self.zero_fill1_dialog.reset_cb()
   self.fourier_transform1_dialog.reset_cb()
   self.extract_region1_dialog.reset_cb()
   
   self.baseline_correction2_dialog.reset_cb()
   self.apodization_function2_dialog.reset_cb()
   self.zero_fill2_dialog.reset_cb()
   self.fourier_transform2_dialog.reset_cb()
   self.extract_region2_dialog.reset_cb()

# ----------------------------------------------------------------------------
#
  def clear_processing_output_cb(self):
    
    self.processing_output.delete(1.0, 'end')

# ----------------------------------------------------------------------------
#
  def update_correction_method(self):
    
    pass
    
# ----------------------------------------------------------------------
#
  def update_peak_fitting_method(self):

    pass

# ----------------------------------------------------------------------
#
  def addsub_spectra_cb(self):

    data_type = self.data_type.get()

    #check for type of input data
    if data_type == 1:
    #for the case of already processed NMRPipe ft2-files
      if self.a_ser_path.get():
        if self.b_ser_path.get():
          if os.access(self.a_ser_path.get(), os.R_OK) == True:
            if os.access(self.b_ser_path.get(), os.R_OK) == True:
              self.addsub_spectra(self.a_ser_path.get(), self.b_ser_path.get())
            else:
              self.assign_output.insert('end', '"file2" not found\n')
          else:
            self.assign_output.insert('end', '"file1" not found\n')
        else:
          self.assign_output.insert('end', 'Please specify the "file2"\n')
      else:
        self.assign_output.insert('end', 'Please specify the "file1"\n')
    elif data_type == 0:
    #for the case of FID(s)
      if self.a_ser_path.get():
        if os.access(self.get_path(self.a_ser_path.get()) + 'test1.ft2', os.R_OK) == True:
          if os.access(self.get_path(self.a_ser_path.get()) + 'test2.ft2', os.R_OK) == True:
            self.addsub_spectra(self.get_path(self.a_ser_path.get()) + 'test1.ft2', self.get_path(self.a_ser_path.get()) + 'test2.ft2')
          else:
            self.assign_output.insert('end', 'Antiphase spectrum not found\n')
        else:
          self.assign_output.insert('end', 'In-phase spectrum not found\n')
      else:
        self.assign_output.insert('end', 'Please specify the "FID1 file" path\n')
    else:
      self.assign_output.insert('end', 'Cannot add and subtract such type of input data\n')

# ----------------------------------------------------------------------
#
  def addsub_spectra(self, inphase_spectrum, antiphase_spectrum):

    self.combine_spectra(self.assign_output, inphase_spectrum, antiphase_spectrum,
             self.get_path(self.a_ser_path.get()) + 'alpha.ft2',
             c1 = float(self.add_c1.get()), c2 = float(self.add_c2.get()))
    self.filenames.append(self.get_path(self.a_ser_path.get()) + 'alpha')

    self.combine_spectra(self.assign_output, inphase_spectrum, antiphase_spectrum,
             self.get_path(self.a_ser_path.get()) + 'beta.ft2',
             c1 = float(self.sub_c1.get()), c2 = float(self.sub_c2.get()),
             Action = 'sub')
    self.filenames.append(self.get_path(self.a_ser_path.get()) + 'beta')

# ----------------------------------------------------------------------------
#
  def clear_handling_output_cb(self):
    
    self.handling_output.delete(1.0, 'end')

# ----------------------------------------------------------------------
#
  def template_assignment_cb(self):

    self.session.command_characters('fo')

# ----------------------------------------------------------------------
#
  def open_cb(self):

    data_type = self.data_type.get()

    #check for type of input data
    if data_type == 2:
    #for the case of already prepared Sparky ucsf-files
      if self.a_ser_path.get():
        if self.b_ser_path.get():
          if os.access(self.a_ser_path.get(), os.R_OK) == True:
            if os.access(self.b_ser_path.get(), os.R_OK) == True:
              self.filenames = []
              self.filenames.append(self.get_path(self.a_ser_path.get()) + self.get_basename(self.get_filename(self.a_ser_path.get())))
              self.filenames.append(self.get_path(self.b_ser_path.get()) + self.get_basename(self.get_filename(self.b_ser_path.get())))
              self.open_spectra()
            else:
              self.assign_output.insert('end', '"file2" not found\n')
          else:
            self.assign_output.insert('end', '"file1" not found\n')
        else:
          self.assign_output.insert('end', 'Please specify the "file2"\n')
      else:
        self.assign_output.insert('end', 'Please specify the "file1"\n')
    else:
    #for the case of FID(s)
      if self.a_ser_path.get():
        if self.filenames:
          if os.access(self.filenames[0] + '.ucsf', os.R_OK) == True:
            if os.access(self.filenames[1] + '.ucsf', os.R_OK) == True:
              self.open_spectra()
            else:
              self.assign_output.insert('end', 'Antiphase spectrum not found\n')
          else:
            self.assign_output.insert('end', 'In-phase spectrum not found\n')
        else:
          self.assign_output.insert('end', 'Please combine the spectra first before assignement\n')
      else:
        self.assign_output.insert('end', 'Please specify the "FID1 file" path\n')

# ----------------------------------------------------------------------
#
  def open_spectra(self):

    if os.access(self.filenames[0] + '.save', os.R_OK) == True:
      self.session.open_spectrum(self.filenames[0] + '.save')
    else:
      self.session.open_spectrum(self.filenames[0] + '.ucsf')
    self.ipap_a = self.project.spectrum_list()[-1:][0]
    self.assign_output.insert('end', 'Assign spectrum and using `fa` save the spectrum as ' + self.filenames[0] + '.save\n')
 
    if os.access(self.filenames[1] + '.save', os.R_OK) == True:
      self.session.open_spectrum(self.filenames[1] + '.save')
    else:
      self.session.open_spectrum(self.filenames[1] + '.ucsf')
    self.ipap_b = self.project.spectrum_list()[-1:][0]
    self.assign_output.insert('end', 'Assign spectrum and using `fa` save the spectrum as ' + self.filenames[1] + '.save\n')

# ----------------------------------------------------------------------
#
  def assign_cb(self):

    if self.a_ser_path.get():
      if self.filenames:
        if os.access(self.filenames[0] + '.ucsf', os.R_OK) == True:
          if os.access(self.filenames[1] + '.ucsf', os.R_OK) == True:
            if self.session.selected_peaks():
              if self.peak_displacement_to_A_choice.get():
                if self.peak_displacement_to_B_choice.get():
                  if self.coupled_dimension_choice.get():
                    self.assign_spectra()
                  else:
                    self.assign_output.insert('end', 'Please choose the coupled dimension\n')
                else:
                  self.assign_output.insert('end', 'Please insert approximate displacement of the assignment peaks to beta spectrum\n')
              else:
                self.assign_output.insert('end', 'Please insert approximate displacement of the assignment peaks to alpha spectrum\n')
            else:
              self.assign_output.insert('end', 'ERROR: No peaks selected for analysis in spectrum with assignment.\n')
          else:
            self.assign_output.insert('end', 'Antiphase spectrum not found\n')
        else:
          self.assign_output.insert('end', 'In-phase spectrum not found\n')
      else:
        self.assign_output.insert('end', 'Please combine the spectra first before assignement\n')
    else:
      self.assign_output.insert('end', 'Please specify the "in-phase FID file" path\n')

# ----------------------------------------------------------------------
#
  def assign_spectra(self):

    self.peak_displacement_to_A = pyutil.string_to_float(self.peak_displacement_to_A_choice.get())
    self.peak_displacement_to_B = pyutil.string_to_float(self.peak_displacement_to_B_choice.get())
    self.coupled_dimension = pyutil.string_to_float(self.coupled_dimension_choice.get()) - 1

    self.assigned_peaks = self.session.selected_peaks()[:] #upravit
    self.couple_peaks()
    self.assign()
    self.session.command_characters('js')
      
# ----------------------------------------------------------------------
#
  def couple_peaks(self):

    self.coupled_peaks=[]
    for peak in self.assigned_peaks:
      couple = [[],[]]
      for dimension in range(len(peak.position)):
        if dimension == self.coupled_dimension:
          couple[0].append(peak.position[dimension] - self.peak_displacement_to_A)
          couple[1].append(peak.position[dimension] + self.peak_displacement_to_B)
        else:
          couple[0].append(peak.position[dimension])
          couple[1].append(peak.position[dimension])
      peak_assignement = self.get_peak_assignement(peak.assignment)
      peak_assignement[0] = peak_assignement[0] + '_1'
      couple[0].append(peak_assignement)
      peak_assignement = self.get_peak_assignement(peak.assignment)
      peak_assignement[0] = peak_assignement[0] + '_2'
      couple[1].append(peak_assignement)
      self.coupled_peaks.append(couple)
     
# ----------------------------------------------------------------------
#
  def assign(self):

    for couple in self.coupled_peaks:
      peak = couple[0]
#       if peak[0] > self.coupled_spectrum.spectrum().region[1][0]:
#         peak[0] = peak[0] - (int((peak[0] - self.coupled_spectrum.spectrum().region[1][0]) / self.coupled_spectrum.spectrum().spectrum_width[0]) + 1) * self.coupled_spectrum.spectrum().spectrum_width[0]
#       if peak[0] < self.coupled_spectrum.spectrum().region[0][0]:
#         peak[0] = peak[0] + (int((self.coupled_spectrum.spectrum().region[0][0] - peak[0]) / self.coupled_spectrum.spectrum().spectrum_width[0]) + 1) * self.coupled_spectrum.spectrum().spectrum_width[0]
      self.ipap_a.place_peak((peak[0], peak[1]))
      self.assign_peak(self.ipap_a.peak_list()[len(self.ipap_a.peak_list()) - 1], peak[2])
    
      peak = couple[1]
      self.ipap_b.place_peak((peak[0], peak[1]))
      self.assign_peak(self.ipap_b.peak_list()[len(self.ipap_b.peak_list()) - 1], peak[2])
    
# ----------------------------------------------------------------------
#
  def assign_peak(self, peak, assignement):

    for i in range(2):
      peak.assign(i, assignement[0], assignement[1][i])

    peak.show_assignment_label()
    peak.center()
    
# ----------------------------------------------------------------------
#
  def get_peak_assignement(self, assignement):

    rv = re.compile("(?P<residue>\D*\d*)(?P<w1>\D*\d*(')?)-(?P<w2>\D*\d*(')?)").search(assignement)
    residue = rv.group('residue')
    w = [rv.group('w1'), rv.group('w2')]

    return [residue, w]

# ----------------------------------------------------------------------------
#
  def save_spectra_cb(self):

    self.session.command_characters('js')

# ----------------------------------------------------------------------------
#
  def clear_assign_output_cb(self):
    
    self.assign_output.delete(1.0, 'end')

# ----------------------------------------------------------------------
#
  def evaluate_couplings_cb(self):

    if self.session.selected_peaks():
      if not self.fit_peak_height.get():
        self.fit_peak_height.set('90.0')
      peak_fitting_method = self.peak_fitting_method.get()
      if peak_fitting_method == 'pi':
        self.fit_peaks()
        self.evaluate_couplings()
      else:
        if peak_fitting_method == 'pc':
          self.center_peaks()
          self.evaluate_couplings()
    else:
      self.evaluation_output.insert('end', 'ERROR: No peaks selected for analysis in spectrum with assignment.\n')

    
# ----------------------------------------------------------------------
#
  def fit_peaks(self):

    template_save_a = self.read_file(self.ipap_a.save_path, 'r')
    positive_treshold_a = re.compile("(?<=contour.pos\ )(?P<contourlevel>\d+)\ +(?P<treshold>\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save_a).group('treshold')
    negative_treshold_a = re.compile("(?<=contour.neg\ )(?P<contourlevel>\d+)\ +(?P<treshold>-\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save_a).group('treshold')
   
    template_save_b = self.read_file(self.ipap_b.save_path, 'r')
    positive_treshold_b = re.compile("(?<=contour.pos\ )(?P<contourlevel>\d+)\ +(?P<treshold>\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save_b).group('treshold')
    negative_treshold_b = re.compile("(?<=contour.neg\ )(?P<contourlevel>\d+)\ +(?P<treshold>-\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save_b).group('treshold')
   
    self.view_tmp=[]
    view_buff = 0
    
    couple_id = 0

    for couple in self.coupled_peaks:
      peak_id = 0
      coupled_peak = couple[peak_id]
      peak = self.ipap_a.find_peak(coupled_peak[2][0] + coupled_peak[2][1][0] + '-' + coupled_peak[2][1][1])
      treshold = peak.data_height * (float(self.fit_peak_height.get()) / 100.0)
      save = string.replace(template_save_a, positive_treshold_a, `treshold`, 1)
      save = string.replace(template_save_a, negative_treshold_a, `treshold`, 1)
      self.write_file(self.get_filename(self.ipap_a.save_path) + '_' + peak.assignment + '.save', 'w', save)
      self.session.open_spectrum(self.get_filename(self.ipap_a.save_path) + '_' + peak.assignment + '.save')
      views = self.session.project.view_list()
      last_view = views[len(views) - 1]
      fitted_peak = last_view.spectrum.find_peak(coupled_peak[2][0] + coupled_peak[2][1][0] + '-' + coupled_peak[2][1][1])
      fitted_peak.fit(last_view)
      for dimension in range(len(fitted_peak.position)):
        self.coupled_peaks[couple_id][peak_id][dimension] = fitted_peak.position[dimension] * fitted_peak.spectrum.hz_per_ppm[dimension]
      self.view_tmp.append(last_view)
      if view_buff: view_buff.destroy()
      view_buff = last_view

      peak_id = 1
      coupled_peak = couple[peak_id]
      peak = self.ipap_b.find_peak(coupled_peak[2][0] + coupled_peak[2][1][0] + '-' + coupled_peak[2][1][1])
      treshold = peak.data_height * (float(self.fit_peak_height.get()) / 100.0)
      save = string.replace(template_save_b, positive_treshold_b, `treshold`, 1)
      save = string.replace(template_save_b, negative_treshold_b, `treshold`, 1)
      self.write_file(self.get_filename(self.ipap_b.save_path) + '_' + peak.assignment + '.save', 'w', save)
      self.session.open_spectrum(self.get_filename(self.ipap_b.save_path) + '_' + peak.assignment + '.save')
      views = self.session.project.view_list()
      last_view = views[len(views) - 1]
      fitted_peak = last_view.spectrum.find_peak(coupled_peak[2][0] + coupled_peak[2][1][0] + '-' + coupled_peak[2][1][1])
      fitted_peak.fit(last_view)
      for dimension in range(len(fitted_peak.position)):
        self.coupled_peaks[couple_id][peak_id][dimension] = fitted_peak.position[dimension] * fitted_peak.spectrum.hz_per_ppm[dimension]
      self.view_tmp.append(last_view)
      if view_buff: view_buff.destroy()
      view_buff = last_view
      couple_id = couple_id + 1

# ----------------------------------------------------------------------
#
  def center_peaks(self):

    template_save_a = self.read_file(self.ipap_a.save_path, 'r')
    positive_treshold_a = re.compile("(?<=contour.pos\ )(?P<contourlevel>\d+)\ +(?P<treshold>\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save_a).group('treshold')
    negative_treshold_a = re.compile("(?<=contour.neg\ )(?P<contourlevel>\d+)\ +(?P<treshold>-\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save_a).group('treshold')
   
    template_save_b = self.read_file(self.ipap_b.save_path, 'r')
    positive_treshold_b = re.compile("(?<=contour.pos\ )(?P<contourlevel>\d+)\ +(?P<treshold>\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save_b).group('treshold')
    negative_treshold_b = re.compile("(?<=contour.neg\ )(?P<contourlevel>\d+)\ +(?P<treshold>-\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save_b).group('treshold')
   
    self.view_tmp=[]
    view_buff = 0
    
    couple_id = 0

    for couple in self.coupled_peaks:
      peak_id = 0
      coupled_peak = couple[peak_id]
      peak = self.ipap_a.find_peak(coupled_peak[2][0] + coupled_peak[2][1][0] + '-' + coupled_peak[2][1][1])
      treshold = peak.data_height * (float(self.fit_peak_height.get()) / 100.0)
      save = string.replace(template_save_a, positive_treshold_a, `treshold`, 1)
      save = string.replace(template_save_a, negative_treshold_a, `treshold`, 1)
      self.write_file(self.get_filename(self.ipap_a.save_path) + '_' + peak.assignment + '.save', 'w', save)
      self.session.open_spectrum(self.get_filename(self.ipap_a.save_path) + '_' + peak.assignment + '.save')
      views = self.session.project.view_list()
      last_view = views[len(views) - 1]
      fitted_peak = last_view.spectrum.find_peak(coupled_peak[2][0] + coupled_peak[2][1][0] + '-' + coupled_peak[2][1][1])
      fitted_peak.fit(last_view)
      for dimension in range(len(fitted_peak.position)):
        self.coupled_peaks[couple_id][peak_id][dimension] = fitted_peak.position[dimension] * fitted_peak.spectrum.hz_per_ppm[dimension]
      self.view_tmp.append(last_view)
      if view_buff: view_buff.destroy()
      view_buff = last_view

      peak_id = 1
      coupled_peak = couple[peak_id]
      peak = self.ipap_b.find_peak(coupled_peak[2][0] + coupled_peak[2][1][0] + '-' + coupled_peak[2][1][1])
      treshold = peak.data_height * (float(self.fit_peak_height.get()) / 100.0)
      save = string.replace(template_save_b, positive_treshold_b, `treshold`, 1)
      save = string.replace(template_save_b, negative_treshold_b, `treshold`, 1)
      self.write_file(self.get_filename(self.ipap_b.save_path) + '_' + peak.assignment + '.save', 'w', save)
      self.session.open_spectrum(self.get_filename(self.ipap_b.save_path) + '_' + peak.assignment + '.save')
      views = self.session.project.view_list()
      last_view = views[len(views) - 1]
      fitted_peak = last_view.spectrum.find_peak(coupled_peak[2][0] + coupled_peak[2][1][0] + '-' + coupled_peak[2][1][1])
      fitted_peak.center()
      for dimension in range(len(fitted_peak.position)):
        self.coupled_peaks[couple_id][peak_id][dimension] = fitted_peak.position[dimension] * fitted_peak.spectrum.hz_per_ppm[dimension]
      self.view_tmp.append(last_view)
      if view_buff: view_buff.destroy()
      view_buff = last_view
      couple_id = couple_id + 1

# ----------------------------------------------------------------------
#
  def evaluate_couplings(self):

    output = ''

    for couple in self.coupled_peaks:
      regsearch = re.compile("(?P<resname>[A-Za-z]*)(?P<resnum>[0-9]*)_1").search(couple[0][2][0])
      resname = regsearch.group('resname')
      resnum = regsearch.group('resnum')
      output = output + '%1s %2s %-4s %-4s       %7.3f\n' % ( resname, resnum, couple[0][2][1][0], couple[0][2][1][1], couple[0][int(self.coupled_dimension)] - couple[1][int(self.coupled_dimension)] )
      self.evaluation_output.insert('end', '%1s %2s %-4s %-4s       %7.3f\n' % ( resname, resnum, couple[0][2][1][0], couple[0][2][1][1], couple[0][int(self.coupled_dimension)] - couple[1][int(self.coupled_dimension)] ))
      #print '%1s %2s %-4s %-4s       %7.3f' % ( resname, resnum, couple[0][2][1][0], couple[0][2][1][1], couple[0][int(self.coupled_dimension)] - couple[1][int(self.coupled_dimension)] )
#      print couple[0][2][0], couple[0][2][1][0] + '-' + couple[0][2][1][1], couple[1][int(self.coupled_dimension)] - couple[0][int(self.coupled_dimension)]

    if self.output_path.get():
      self.write_file(self.output_path.get(), 'w', output)
   
# ----------------------------------------------------------------------------
#
  def clear_evaluation_output_cb(self):
    
    self.evaluation_output.delete(1.0, 'end')

# ----------------------------------------------------------------------
#
  def close_spectra_cb(self):
    
    for view in self.view_tmp:
      view.destroy()
          
# ----------------------------------------------------------------------
#
  def get_path(self, path):
    
    if path:
      rv = re.compile("(?P<path>.*/)""(?P<filename>.*$)")
      p = rv.search(path).group('path')
      return p

# ----------------------------------------------------------------------
#
  def get_filename(self, path):
    
    if path:
      rv = re.compile("(?P<path>.*/)""(?P<filename>.*$)")
      p = rv.search(path).group('filename')
      return p

# ----------------------------------------------------------------------
#
  def get_basename(self, filename):
    
    if filename:
      rv = re.compile("(?P<basename>.*)""(?P<suffix>\..*$)")
      p = rv.search(filename).group('basename')
      return p

# ----------------------------------------------------------------------
#
  def read_file(self, path, mode):
    
    f = open(path, mode)
    file = f.read()
    f.close()
    return file
    
# ----------------------------------------------------------------------
#
  def write_file(self, path, mode, content, write_heading = 0):
    
    if path:
      file = open(path, mode)
      if write_heading and self.heading:
        file.write(self.heading['text'] + '\n')
      file.write(content)
      file.close()
    
# ----------------------------------------------------------------------
#
def show_ipap(session):
  sputil.the_dialog(couple_dialog,session).show_window(1)
