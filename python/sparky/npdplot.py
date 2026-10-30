# -----------------------------------------------------------------------------
# Dialog for NDP Plot (Global).- name changed
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: March 28, 2016
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
#
import string
import re
import Tkinter

import pyutil
import sparky
import sputil
import tkutil
import tkMessageBox
import tkColorChooser
import math
import os
import os.path
from operator import itemgetter
# -----------------------------------------------------------------------------
#
class show_npdplot_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    tkutil.Dialog.__init__(self, session.tk, 'Perturbation Plot')

    self.session = session
    self.a_list = [] # analyzed data in here
    self.filter_result = []
    
    # spectrum list
    self.sp = sputil.spectrum_menu(session, self.top, 'Spectrum 1: ')
    self.sp.frame.pack(side = 'top', fill = 'both', expand = 1)    

    self.sp2 = sputil.spectrum_menu(session, self.top, 'Spectrum 2: ')
    self.sp2.frame.pack(side = 'top', fill = 'both', expand = 1)    
    
    # title
    self.title = tkutil.entry_field(self.top, 'Title: ', 'Perturbation Plot', 34)
    self.title.frame.pack(side = 'top', fill = 'both', expand = 1)
    
    # axis
    self.xlabel = tkutil.entry_field(self.top, 'X Label: ', 'Residue Number', 32)
    self.xlabel.frame.pack(side = 'top', fill = 'both', expand = 1)
    self.ylabel = tkutil.entry_field(self.top, 'Y Label: ', 'dH (ppm)', 32)
    self.ylabel.frame.pack(side = 'top', fill = 'both', expand = 1)
    
    # observable
    observable_list = ('H (ppm)', 'N (ppm)', 'C (ppm)', 'CA (ppm)', 'CB (ppm)',
                       'HA/HA2 (ppm)', 'HA/HA3 (ppm)', 'HB/HB2 (ppm)', 'HB/HB3 (ppm)', 
                       '---Below is only for HSQC---', 'Line Width w1 (ppm)', 
                       'Line Width w1 (%)', 'Line Width w1 (ratio)', 'Line Width w2 (ppm)', 
                       'Line Width w2 (%)', 'Line Width w2 (ratio)', 'Data Height (%)', 
                       'Data Height (ratio)', 'Fit Height (%)', 'Fit Height (ratio)', 
                       'Signal-to-Noise (%)', 'Signal-to-Noise (ratio)', 'Volume (%)', 
                       'Volume (ratio)', 'sqrt((H^2+(N/B)^2)/2)', 'sqrt((dH^2+(dN/B)^2)/2)', 
                       'sqrt((HX^2+(CX/B)^2)/2)', 'sqrt((dHX^2+(dCX/B)^2)/2)') 
    self.observables = tkutil.option_menu(self.top, "Observables: ", observable_list, 'H (ppm)')
    self.observables.frame.pack(side = 'top', fill = 'both', expand = 1)
    
    self.BfactorInput = tkutil.entry_field(self.top, 'B-factor: ', '5.0', 10)    
    self.BfactorInput.frame.pack(side = 'top', fill = 'both', expand = 1)    
    self.Bfactor = 5.0
      
    # absolute
    self.absolute_choice = Tkinter.IntVar()
    absolute_cb = Tkinter.Checkbutton(self.top, text = 'Use absolute values', 
                                variable = self.absolute_choice, onvalue=1, offvalue = 0)
    absolute_cb.pack(side = 'top', anchor = 'w')    
    self.absolute_cb = absolute_cb

    # range
    frm = Tkinter.Frame(self.top)
    frm.pack(side='top', anchor = 'w')
    self.gradient_from = tkutil.entry_field(frm, 'Gradient from: ', 'min', width=6)
    self.gradient_from.frame.pack(side='left')
    b = Tkinter.Button(frm, text = 'blue', command=self.grad1)
    b.pack(side = 'right')
    self.btn_grad1 = b
    self.btn_grad1['bg'] = 'blue'
    self.gradient = (0, 0, 255)

    frm = Tkinter.Frame(self.top)
    frm.pack(side='top', anchor = 'w')
    self.gradient_to = tkutil.entry_field(frm, 'Gradient to: ', 'max', width=6)
    self.gradient_to.frame.pack(side='left')
    b = Tkinter.Button(frm, text = 'red', command=self.grad2)
    b.pack(side = 'right')
    self.btn_grad2 = b
    self.btn_grad2['bg'] = 'red'
    self.gradient2 = (255, 0, 0)
    
    # buttons
    self.br = tkutil.button_row(self.top,
          ('Analyze', self.analyze_cb),
          ('Delete', self.delete_cb),
          ('Plot...', self.plot_cb),
          ('Export', self.export_cb),
          ('PyMOL', self.pymol_cb),
          ('Gradient', self.generate_script),
          ('Close', self.close_cb),
          )
    self.br.frame.pack(side = 'top', fill = 'both', expand = 1)
    
    # scroll_list
    self.listbox = tkutil.scrolling_list(self.top, 'Perturbation Data', 10)    
    self.listbox.frame.pack(side = 'top', fill = 'both', expand = 1)
    self.listbox.listbox.bind('<ButtonRelease-1>', self.move_cb)
    
    # file names
    self.ini_path = os.path.join(os.path.expanduser("~"), 'ndpplot.ini')
    self.csv_path = os.path.join(os.path.expanduser("~"), 'ndpplot.csv')
   
  # -----------------------------------------------------------------------------
  #
  def sort_peaks(self, peak_list):
    sorted_list = []
    #iMin = 99999999
    #iMax = -99999999
    
    assign_list = []
    for peak in peak_list:
      if peak.is_assigned == 0: continue
      assign_list.append([peak.resonances()[0].group.number, peak.resonances()[0].atom.name, peak])
    sorted_list2 = sorted(assign_list, key=itemgetter(1,2))
      #if iMin > peak.resonances()[0].group.number: iMin = peak.resonances()[0].group.number
      #if iMax < peak.resonances()[0].group.number: iMax = peak.resonances()[0].group.number      
     
    for (idx, atm, peak) in sorted_list2:
      sorted_list.append(peak)     
    #for i in range(iMin, iMax+1):      
    #  for peak in peak_list:
    #    if peak.is_assigned == 0: continue
    #    if peak.resonances()[0].group.number == i:
    #      sorted_list.append(peak)
        
    return sorted_list      
  # -----------------------------------------------------------------------------
  #
  def filter_observable(self, spec, peak_list, szObservable):
    peak_list2 = []
    
    iMin = 99999999
    iMax = -99999999
    
    # tkMessageBox.showinfo('ob', szObservable)
        
    for peak in peak_list:
      if iMin > peak.resonances()[0].group.number: iMin = peak.resonances()[0].group.number
      if iMax < peak.resonances()[0].group.number: iMax = peak.resonances()[0].group.number      
      
      if szObservable == 'H (ppm)':
        if (peak.resonances()[0].atom.name == 'H') or (peak.resonances()[0].atom.name == 'HN'):
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, peak.frequency[0]))
        elif (peak.resonances()[1].atom.name == 'H') or (peak.resonances()[1].atom.name == 'HN'):
          peak_list2.append((peak.resonances()[1].group.symbol, peak.resonances()[1].group.number, 
                              peak.resonances()[1].atom.name, peak.frequency[1]))
      elif szObservable == 'N (ppm)':
        if (peak.resonances()[0].atom.name == 'N'):
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, peak.frequency[0]))
        elif (peak.resonances()[1].atom.name == 'N'):
          peak_list2.append((peak.resonances()[1].group.symbol, peak.resonances()[1].group.number, 
                              peak.resonances()[1].atom.name, peak.frequency[1]))     
      elif szObservable == 'C (ppm)':      
        if (peak.resonances()[0].atom.name == 'C'):
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, peak.frequency[0]))
        elif (peak.resonances()[1].atom.name == 'C'):
          peak_list2.append((peak.resonances()[1].group.symbol, peak.resonances()[1].group.number, 
                              peak.resonances()[1].atom.name, peak.frequency[1]))  
      elif szObservable == 'CA (ppm)':          
        if (peak.resonances()[0].atom.name == 'CA'):
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, peak.frequency[0]))
        elif (peak.resonances()[1].atom.name == 'CA'):
          peak_list2.append((peak.resonances()[1].group.symbol, peak.resonances()[1].group.number, 
                              peak.resonances()[1].atom.name, peak.frequency[1])) 
      elif szObservable == 'CB (ppm)':
        if (peak.resonances()[0].atom.name == 'CB'):
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, peak.frequency[0]))
        elif (peak.resonances()[1].atom.name == 'CB'):
          peak_list2.append((peak.resonances()[1].group.symbol, peak.resonances()[1].group.number, 
                              peak.resonances()[1].atom.name, peak.frequency[1]))
      elif szObservable == 'HA/HA2 (ppm)':      
        if (peak.resonances()[0].atom.name == 'HA') or (peak.resonances()[0].atom.name == 'HA2'):
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, peak.frequency[0]))
        elif (peak.resonances()[1].atom.name == 'HA') or (peak.resonances()[1].atom.name == 'HA2'):
          peak_list2.append((peak.resonances()[1].group.symbol, peak.resonances()[1].group.number, 
                              peak.resonances()[1].atom.name, peak.frequency[1]))
      elif szObservable == 'HA/HA3 (ppm)':      
        if (peak.resonances()[0].atom.name == 'HA') or (peak.resonances()[0].atom.name == 'HA3'):
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, peak.frequency[0]))
        elif (peak.resonances()[1].atom.name == 'HA') or (peak.resonances()[1].atom.name == 'HA3'):
          peak_list2.append((peak.resonances()[1].group.symbol, peak.resonances()[1].group.number, 
                              peak.resonances()[1].atom.name, peak.frequency[1]))
      elif szObservable == 'HB/HB2 (ppm)':
        if (peak.resonances()[0].atom.name == 'HB') or (peak.resonances()[0].atom.name == 'HB2'):
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, peak.frequency[0]))
        elif (peak.resonances()[1].atom.name == 'HB') or (peak.resonances()[1].atom.name == 'HB2'):
          peak_list2.append((peak.resonances()[1].group.symbol, peak.resonances()[1].group.number, 
                              peak.resonances()[1].atom.name, peak.frequency[1]))
      elif szObservable == 'HB/HB3 (ppm)':
        if (peak.resonances()[0].atom.name == 'HB') or (peak.resonances()[0].atom.name == 'HB3'):
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, peak.frequency[0]))
        elif (peak.resonances()[1].atom.name == 'HB') or (peak.resonances()[1].atom.name == 'HB3'):
          peak_list2.append((peak.resonances()[1].group.symbol, peak.resonances()[1].group.number, 
                              peak.resonances()[1].atom.name, peak.frequency[1]))
      elif (szObservable == 'Line Width w1 (ppm)') or (szObservable == 'Line Width w1 (%)') or \
              (szObservable == 'Line Width w1 (ratio)'):
        if peak.line_width != None:
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, peak.line_width[0]))
        else:
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, 0))
      elif (szObservable == 'Line Width w2 (ppm)') or (szObservable == 'Line Width w2 (%)') or \
              (szObservable == 'Line Width w2 (ratio)'):
        if peak.line_width != None:      
          peak_list2.append((peak.resonances()[1].group.symbol, peak.resonances()[1].group.number, 
                              peak.resonances()[1].atom.name, peak.line_width[1]))
        else:
          peak_list2.append((peak.resonances()[1].group.symbol, peak.resonances()[1].group.number, 
                              peak.resonances()[1].atom.name, 0))      
      elif (szObservable == 'Data Height (%)') or (szObservable == 'Data Height (ratio)'):
        peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, peak.data_height))
      elif (szObservable == 'Fit Height (%)') or (szObservable == 'Fit Height (ratio)'):
        if peak.fit_height != None:            
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, peak.fit_height))
        else:
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, 0))
      elif (szObservable == 'Signal-to-Noise (%)') or (szObservable == 'Signal-to-Noise (ratio)'):
        peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, peak.data_height / spec.noise))
      elif (szObservable == 'Volume (%)') or (szObservable == 'Volume (ratio)'):
        if peak.volume != None:
          #try1 = peak.volume.split('e')
          #if len(try1) == 1:
          #  volume = float(try1[0])
          #else:
          #  volume = float(try1[0]) * pow(10, int(try1[0])             
          peak_list2.append( (peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, peak.volume) )
        else:
          peak_list2.append( (peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, 0) )
      elif (szObservable == 'sqrt((H^2+(N/B)^2)/2)'):
        if ((peak.resonances()[0].atom.name == 'H') or (peak.resonances()[0].atom.name == 'HN')) and \
              (peak.resonances()[1].atom.name == 'N'):
          value = math.sqrt(( pow(peak.frequency[0],2.0) + \
                              pow((peak.frequency[1]/float(self.Bfactor)), 2.0))/2.0)
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, value))
        elif ((peak.resonances()[1].atom.name == 'H') or (peak.resonances()[1].atom.name == 'HN')) and \
                (peak.resonances()[0].atom.name == 'N'):
          value = math.sqrt(( pow(peak.frequency[1],2.0) + \
                              pow((peak.frequency[0] / float(self.Bfactor)), 2.0))/2.0)        
          peak_list2.append((peak.resonances()[1].group.symbol, peak.resonances()[1].group.number, 
                              peak.resonances()[1].atom.name, value))     
      elif (szObservable == 'sqrt((dH^2+(dN/B)^2)/2)'):
        if ((peak.resonances()[0].atom.name == 'H') or (peak.resonances()[0].atom.name == 'HN')) and \
                (peak.resonances()[1].atom.name == 'N'):
          #value = math.sqrt(( pow(peak.frequency[0],2.0)+ pow((peak.frequency[1]/float(self.Bfactor)), 2.0))/2.0)
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, (peak.frequency[0], peak.frequency[1], 
                              float(self.Bfactor) ) ))
        elif ((peak.resonances()[1].atom.name == 'H') or (peak.resonances()[1].atom.name == 'HN')) and \
                              (peak.resonances()[0].atom.name == 'N'):
          #value = math.sqrt(( pow(peak.frequency[1],2.0)+ pow((peak.frequency[0]/float(self.Bfactor)), 2.0))/2.0)        
          peak_list2.append((peak.resonances()[1].group.symbol, peak.resonances()[1].group.number, 
                              peak.resonances()[1].atom.name, (peak.frequency[1], peak.frequency[0], 
                              float(self.Bfactor) ) ))     
      elif (szObservable == 'sqrt((HX^2+(CX/B)^2)/2)'):
        if ((peak.resonances()[0].atom.name[0] == 'H') or (peak.resonances()[0].atom.name[0] == 'Q') or \
              (peak.resonances()[0].atom.name[0] == 'M')) and (peak.resonances()[1].atom.name[0] == 'C'):
          value = math.sqrt(( pow(peak.frequency[0],2.0) + \
                              pow((peak.frequency[1] / float(self.Bfactor)), 2.0))/2.0)
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, value))
        elif ((peak.resonances()[1].atom.name[0] == 'H') or (peak.resonances()[1].atom.name[0] == 'Q') or \
              (peak.resonances()[1].atom.name[0] == 'M')) and (peak.resonances()[0].atom.name[0] == 'C'):
          value = math.sqrt(( pow(peak.frequency[1],2.0) + \
                              pow((peak.frequency[0] / float(self.Bfactor)), 2.0))/2.0)        
          peak_list2.append((peak.resonances()[1].group.symbol, peak.resonances()[1].group.number, 
                              peak.resonances()[1].atom.name, value))     
      elif (szObservable == 'sqrt((dHX^2+(dCX/B)^2)/2)'):
        if ((peak.resonances()[0].atom.name[0] == 'H') or (peak.resonances()[0].atom.name[0] == 'Q') or \
            (peak.resonances()[0].atom.name[0] == 'M')) and  (peak.resonances()[1].atom.name[0] == 'C'):
          #value = math.sqrt(( pow(peak.frequency[0],2.0)+ pow((peak.frequency[1]/float(self.Bfactor)), 2.0))/2.0)
          peak_list2.append((peak.resonances()[0].group.symbol, peak.resonances()[0].group.number, 
                              peak.resonances()[0].atom.name, (peak.frequency[0], peak.frequency[1], 
                              float(self.Bfactor) ) ))
        elif ((peak.resonances()[1].atom.name[0] == 'H') or (peak.resonances()[1].atom.name[0] == 'Q') or (peak.resonances()[1].atom.name[0] == 'M')) and (peak.resonances()[0].atom.name[0] == 'C'):
          #value = math.sqrt(( pow(peak.frequency[1],2.0)+ pow((peak.frequency[0]/float(self.Bfactor)), 2.0))/2.0)        
          peak_list2.append((peak.resonances()[1].group.symbol, peak.resonances()[1].group.number, 
                              peak.resonances()[1].atom.name, (peak.frequency[1], peak.frequency[0], 
                              float(self.Bfactor) ) ))

    if len(peak_list2) == 0:
      return []
      
    # loop and delete duplicates & fill empty
    # we will make averaged version
    peak_list3 = []
    for i in range(iMin, iMax+1):
      iFound = 0
      for peak in peak_list2:
        if peak[1] == i:
          if (peak[0] == '') or (len(peak[0]) != 1): 
            ltpeak = list(peak)
            ltpeak[0] = 'X'
            peak = tuple(ltpeak)
          peak_list3.append(peak)
          iFound = 1
          if szObservable != 'sqrt((dHX^2+(dCX/B)^2)/2)': break
      if iFound == 1: continue
      if (szObservable == 'sqrt((dH^2+(dN/B)^2)/2)' or szObservable == 'sqrt((dHX^2+(dCX/B)^2)/2)'):
        peak_list3.append(('X', i, 'X', (0,0, float(self.Bfactor) )))  
      else:
        peak_list3.append(('X', i, 'X', 0))            
    
    return peak_list3
          
  # -----------------------------------------------------------------------------
  #  
  def check_peaklists(self, peaklist, peaklist2, szObservable):
    filtered_list = self.filter_observable(self.spec, peaklist, szObservable)
    filtered_list2 = self.filter_observable(self.spec2, peaklist2, szObservable) 
    
    if len(filtered_list) != len(filtered_list2): return []
    if (len(filtered_list) == 0) or (len(filtered_list2) == 0): return []    
    if filtered_list[0][1] != filtered_list2[0][1]: return []
    
    return (filtered_list, filtered_list2)
  # -----------------------------------------------------------------------------
  #  
  def delete_cb(self):
    if self.listbox.selected_line_data() == None: return
    sel_nums = self.listbox.selected_line_numbers()
    sel_nums.sort()
    sel_nums.reverse()
    for line_number in sel_nums:
      if line_number == 0: continue # not header
      # delete from a_list
      for i in range(len(self.a_list)):
        processed_data = self.a_list[i]
        szKey = '%s%d%s:' % (processed_data[0], processed_data[1], processed_data[2])
        if self.listbox.line_data[line_number]['seq'] == processed_data[0] and \
            self.listbox.line_data[line_number]['num'] == processed_data[1] and \
            self.listbox.line_data[line_number]['atm'] == processed_data[2]:
          self.a_list.pop(i)
          break
      # delete from listbox
      del self.listbox.line_data[line_number]
      self.listbox.listbox.delete(line_number)
      # make csv and ini again
    self.make_csv()
    self.make_ini()

  # -----------------------------------------------------------------------------
  #  
  def process_data(self, filter_result):
    processed_list = []
    szObservable = self.observables.get()
    for i in range(len(filter_result[0])):
      group = filter_result[0][i]
      group2 = filter_result[1][i]
      
      if szObservable == 'sqrt((dH^2+(dN/B)^2)/2)' or szObservable == 'sqrt((dHX^2+(dCX/B)^2)/2)':
        dHppm = group2[3][0] - group[3][0]
        dNppm = group2[3][1] - group[3][1]
        dBfac = group[3][2]
        diff = math.sqrt(( pow(dHppm,2.0)+ pow( (dNppm/dBfac), 2.0))/2.0)
      else:
        diff = group2[3] - group[3]
        if group[3] != 0:
          ratio = group2[3] / group[3]
        else:
          ratio = 0
      
      if self.absolute_choice.get() == 1:
        diff = abs(diff)
      if szObservable.find('(ppm)') != -1:
        value = diff
      elif szObservable.find('(%)') != -1:
        value = ratio * 100.0
      elif szObservable.find('(ratio)') != -1:  
        value = ratio
      else:
        value = diff
      processed_list.append((group[0], group[1], group[2], value))
      
    for i in range(len(processed_list)):
      processed_data = processed_list[i]
      # update scroll_list
      if self.observables.get().find('(ppm)') != -1:      
        self.listbox.append( '%s%d%s: %.5f ppm' % (processed_data[0], processed_data[1], 
                                            processed_data[2], processed_data[3]),  
                                          {'seq': processed_data[0], 'num': processed_data[1], 
                                          'atm': processed_data[2], 'value': processed_data[3]})
      elif self.observables.get().find('(%)') != -1:      
        self.listbox.append( '%s%d%s: %.3f %%' % (processed_data[0], processed_data[1], 
                                            processed_data[2], processed_data[3]),  
                                          {'seq': processed_data[0], 'num': processed_data[1], 
                                          'atm': processed_data[2], 'value': processed_data[3]})                
      else:  
        self.listbox.append( '%s%d%s: %.3f' % (processed_data[0], processed_data[1], 
                                            processed_data[2], processed_data[3]),  
                                          {'seq': processed_data[0], 'num': processed_data[1], 
                                          'atm': processed_data[2], 'value': processed_data[3]})                      
    return processed_list
  # -----------------------------------------------------------------------------
  #  
  def make_csv(self):
    # generate npdplot.csv
    # format is...
    # GROUP XLABEL YLABEL
    # M1     1     VALUE
    f = open(self.csv_path, 'w')
    szHeader = 'Group,%s,%s\n' % (self.xlabel.variable.get(), self.ylabel.variable.get())
    f.write(szHeader)
    for i in range(len(self.a_list)):
      group = self.a_list[i][0:3]
      value = self.a_list[i][3]
      szLine = '%s%d%s,%d,%f\n' % (group[0], group[1], group[2], group[1], value)
      f.write(szLine)
    f.close()
  # -----------------------------------------------------------------------------
  #  
  def make_ini(self):
    # generate npdplot.ini
    # find value_min and value_max
    value_min = 999999999
    value_max = -999999999
    processed_list = self.a_list
    for i in range(len(processed_list)):
      value = self.a_list[i][3]
      if value_min > value: value_min = value
      if value_max < value: value_max = value

    self.listbox.clear()
    f = open(self.ini_path, 'w')
    (firstidx, lastidx, sequence) = self.get_sequence(self.filter_result[0])
    
    f.write('[GENERAL_START]\n')
    f.write('TITLE=%s\n' % self.title.variable.get())
    f.write('XLABEL=%s\n' % self.xlabel.variable.get())    
    f.write('YLABEL=%s\n' % self.ylabel.variable.get())        
    f.write('XMIN=%d\n' % firstidx)
    f.write('XMAX=%d\n' % lastidx)
    f.write('YMIN=%f\n' % value_min)
    f.write('YMAX=%f\n' % value_max)
    f.write('XSCALE=FLOAT\n')    
    f.write('[GENERAL_END]\n')
    f.write('[SERIES1_START]\n')
    f.write('NAME=NMR Data Perturbation Plot\n')
    f.write('PLOTTYPE=BAR\n')
    
    if self.observables.get().find('(ratio)') != -1:
      f.write('COLORCOUNT=2\n')
    else:
      f.write('COLORCOUNT=1\n')
      
    f.write('DATACOUNT=%d\n' % len(processed_list))
    f.write('COLOR_1=%d,%d,%f,%f,NAVY\n' % (firstidx, firstidx+len(processed_list)-1, 
                                            value_min, value_max))
    if self.observables.get().find('(ratio)') != -1:
      f.write('COLOR_2=%d,%d,-0.000001,0.000001,WHITE\n' % (firstidx, firstidx+len(processed_list)-1))

    fPrev = -9999
    for i in range(1, len(processed_list)+1):
      processed_data = processed_list[i-1]
      if fPrev >= processed_data[1]: x_pos = fPrev + 0.2
      else: x_pos = processed_data[1]
      fPrev = x_pos
      f.write('DATA_%d=%f,%f,0,%s%d%s\n' % (i, x_pos, processed_data[3], processed_data[0], 
                                            processed_data[1],processed_data[2]))
      # update scroll_list
      if self.observables.get().find('(ppm)') != -1:      
        self.listbox.append( '%s%d%s: %.5f ppm' % (processed_data[0], processed_data[1], 
                            processed_data[2], processed_data[3]),  
                            {'seq': processed_data[0], 'num': processed_data[1], 
                            'atm': processed_data[2], 'value': processed_data[3]})
      elif self.observables.get().find('(%)') != -1:      
        self.listbox.append( '%s%d%s: %.3f %%' % (processed_data[0], processed_data[1], 
                            processed_data[2], processed_data[3]),  
                            {'seq': processed_data[0], 'num': processed_data[1], 
                            'atm': processed_data[2], 'value': processed_data[3]})                
      else:  
        self.listbox.append( '%s%d%s: %.3f' % (processed_data[0], processed_data[1], 
                            processed_data[2], processed_data[3]), 
                            {'seq': processed_data[0], 'num': processed_data[1], 
                            'atm': processed_data[2], 'value': processed_data[3]})                      
    f.write('[SERIES1_END]\n')
    f.close()
  # -----------------------------------------------------------------------------
  #  
  def analyze_cb(self):
    # selected two spectra must be 2-D
    self.spec = self.sp.spectrum()
    self.spec2 = self.sp2.spectrum()
    
    if (self.spec == None) or (self.spec2 == None):    
      tkMessageBox.showerror("Error", "Selected 2-D HSQCs.")
      return 0       
    if (self.spec == self.spec2):    
      tkMessageBox.showerror("Error", "Selected two different 2-D HSQCs.")
      return 0             
    if (self.spec.dimension != 2) or (self.spec2.dimension != 2):
      tkMessageBox.showerror("Error", "Selected spectrum must be 2-D.")
      return 0   
    if (len(self.spec.peak_list()) == 0) or (len(self.spec2.peak_list()) == 0):
      tkMessageBox.showerror("Error", "No assignment found.")
      return 0
      
    # sort peaks by assignment
    sorted_list = self.sort_peaks(self.spec.peak_list())
    sorted_list2 = self.sort_peaks(self.spec2.peak_list()) 
    
    if (len(sorted_list) == 0) or (len(sorted_list2) == 0):
      tkMessageBox.showerror("Error", "No assignment found.")
      return 0       

    szObservable = self.observables.get()
    if szObservable == '---Below is only for HSQC---':
      tkMessageBox.showerror("Error", "Select proper observable.")
      return 0                     
      
    try:  
      self.Bfactor = float(self.BfactorInput.variable.get())
    except:
      tkMessageBox.showerror("Error", "Bfactor should be a floating point. Default (5.0) will be used.")
      self.Bfactor = 5.0
          
    filter_result = self.check_peaklists(sorted_list, sorted_list2, szObservable)
    if len(filter_result) != 2:
      tkMessageBox.showerror("Error", "Assignments in two spectra do not match.")
      return 0
      
    # '('H (ppm)', 'N (ppm)', 'C (ppm)', 'CA (ppm)', 'CB (ppm)','HA/HA2 (ppm)', 'HA/HA3 (ppm)', 'HB/HB2 (ppm)', 'Line Width (ppm)', 'Line Width (%)', 'Data Height (%)', 'Fit Height (%)', 'Signal-to-Noise (%)', 'Volume (%)')

    # generate a_list first
    self.a_list = []
    self.a_list = self.process_data(filter_result)
    self.filter_result = filter_result
    # generate csv and ini
    self.make_csv()
    self.make_ini()

    return 1
  # -----------------------------------------------------------------------------
  # get sequence
  def get_sequence(self, filter_result):
    firstidx = filter_result[0][1]
    lastidx = filter_result[-1][1]    
    sequence = ''
    for group in filter_result:
      sequence = sequence + group[0]
    
    return (firstidx, lastidx, sequence)  
  # -----------------------------------------------------------------------------
  # move to the place
  def move_cb(self, *args):
    # get assignment from spec
    # center it.
    ds = self.listbox.selected_line_data()
    if len(ds) != 1:
      return
    if self.spec == None:
      return
    seqidx = ds[0]['num']
    atm = ds[0]['atm']
    for peak in self.spec.peak_list():
      if peak.is_assigned == 0: continue
      if (peak.resonances()[0].group.number ==  seqidx and peak.resonances()[0].atom.name == atm) or (peak.resonances()[1].group.number ==  seqidx and peak.resonances()[1].atom.name == atm):
        sputil.show_peak(peak)
        break
    
  def plot_cb(self):
    if len(self.a_list) == 0:
      if self.analyze_cb() == 0: 
        tkMessageBox.showerror("Error", "Data analysis failed.")
        return
    import nmrfam
    nmrfam.run_npdplot(self.session)
    
  def export_cb(self):    
    if self.analyze_cb() == 0: 
      tkMessageBox.showerror("Error", "Data analysis failed.")
      return
    # copy 
    path = tkutil.save_file(self.session.tk, "Save file", "Save .csv file")
    if not path: return
    import shutil
    shutil.copyfile(self.csv_path, path)
    tkMessageBox.showinfo("Export", "Saved.")
  # -----------------------------------------------------------------------------
  #
  def grad1(self):
    rgbTuplet, colorString = tkColorChooser.askcolor(parent=self.top, 
      title='Pick a gradient color 1', 
      initialcolor=self.btn_grad1['text'])
    try:  
      cl = '#%02x%02x%02x' % (rgbTuplet[0], rgbTuplet[1], rgbTuplet[2])
    except:
      return
    self.btn_grad1['text'] = cl
    self.btn_grad1['bg'] = cl
    self.gradient = (rgbTuplet[0], rgbTuplet[1], rgbTuplet[2])

  def grad2(self):
    rgbTuplet, colorString = tkColorChooser.askcolor(parent=self.top, 
      title='Pick a gradient color 2', 
      initialcolor=self.btn_grad2['text'])
    try:  
      cl = '#%02x%02x%02x' % (rgbTuplet[0], rgbTuplet[1], rgbTuplet[2])
    except:
      return
    self.btn_grad2['text'] = cl
    self.btn_grad2['bg'] = cl
    self.gradient2 = (rgbTuplet[0], rgbTuplet[1], rgbTuplet[2])
    
  # -----------------------------------------------------------------------------
  #  blue-red, 0, 100 ???
  # blue (0, 0, 255), green (0, 255, 0), red (255, 0, 0), yellow (255, 255, 0), 
  # magenta (255, 0, 255), 
  def gradient_color(self, value, vmin, vmax):
    rgb1 = self.gradient
    rgb2 = self.gradient2
    red1, green1, blue1 = rgb1
    red2, green2, blue2 = rgb2
    ratio = float(value - vmin) / float(vmax - vmin)
    ratio = min(ratio, 1.0)
    ratio = max(ratio, 0.0)
    red = int(float(red2-red1) * ratio + red1)
    green = int(float(green2-green1) * ratio + green1)
    blue = int(float(blue2-blue1) * ratio + blue1)
    return red, green, blue
  # -----------------------------------------------------------------------------
  #
  def generate_script(self):
    pymol_script = ''
    # get min, max
    vmin = 9999999999
    vmax = -9999999999
    for i in range(len(self.a_list)):
      value = self.a_list[i][3]
      vmin = min(value, vmin)
      vmax = max(value, vmax)

    if self.gradient_from.variable.get().upper() != 'MIN':
      vmin = float(self.gradient_from.variable.get())
    if self.gradient_to.variable.get().upper() != 'MAX':
      vmax = float(self.gradient_to.variable.get())

    for i in range(len(self.a_list)):
      group = self.a_list[i][0:3]
      value = self.a_list[i][3]
      value = min(value, vmax)
      value = max(value, vmin)
      #if value > gradient[2] or value < gradient[1]: continue
      r, g, b = self.gradient_color(value, vmin, vmax) # 256 scale
      r2, g2, b2 = float(r) / 256.0, float(g) / 256.0, float(b) / 256.0 # 1.0 scale
      line = 'set_color ndpplot_color%d, [%f, %f, %f]\n' % (i+1, r2, g2, b2)
      line2 = 'color ndpplot_color%d, i. %d\n' % (i+1, group[1])
      pymol_script = pymol_script + line + line2
    f = open(os.path.join(self.session.project.sparky_directory, 'p'), 'w')
    f.write(pymol_script)
    f.close()
  """
  # -----------------------------------------------------------------------------
  #
  def generate_p(self, value):
    gradient = value.split(',')
    self.gradient = (gradient[0], float(gradient[1]), float(gradient[2]))
    pymol_script = ''
    
    for i in range(len(self.a_list)):
      group = self.a_list[i][0:3]
      value = self.a_list[i][3]
      value = min(value, self.gradient[2])
      value = max(value, self.gradient[1])
      #if value > gradient[2] or value < gradient[1]: continue
      r, g, b = self.gradient_color(value) # 256 scale
      r2, g2, b2 = float(r) / 256.0, float(g) / 256.0, float(b) / 256.0 # 1.0 scale
      line = 'set_color ndpplot_color%d, [%f, %f, %f]\n' % (i+1, r2, g2, b2)
      line2 = 'color ndpplot_color%d, i. %d\n' % (i+1, group[1])
      pymol_script = pymol_script + line + line2
    f = open(os.path.join(self.session.project.sparky_directory, 'p'), 'w')
    f.write(pymol_script)
    f.close()

  def gradient_cb(self):
    # get cutoff value
    # use two gradient colors and min and max
    # e.g. blue-red,0,10
    import tkSimpleDialog
    value = tkSimpleDialog.askstring('Gradient color',
            'Please type gradient color setting for PyMOL (color1-color2, min, max).', 
            initialvalue = 'blue-red,0,2')
    self.generate_p(value)
    tkMessageBox.showinfo("PyMOL color", "PyMOL color changed. Type @p to update in PyMOL.")
  """
  def pymol_cb(self):
    import tkFileDialog
    # ask if you want to use current pdb file?
    user_pdb_path = tkFileDialog.askopenfilename(
        initialdir = self.session.project.sparky_directory,
        title = 'Select a PDB file for NDP-PLOT analysis')
    if not os.path.exists(user_pdb_path):
      return
    if user_pdb_path[-4:] == '.cif':
      import cif2pdb
      cif2pdb.cif2pdb(user_pdb_path, user_pdb_path[0:-3]+'pdb', HETATM=True)
      user_pdb_path = user_pdb_path[0:-3]+'pdb'
    self.seq_align(user_pdb_path)
    self.generate_script()
    #if self.gradient == ['default', 0, 0]:
    #  self.generate_p('blue-red,0,2')
    self.launch_pymol()

  def launch_pymol(self):
    import nmrfam
    ndpplot_pdb_path = os.path.join(self.session.project.sparky_directory, 
                                    'from_ndpplot.pdb')
    msg = 'Please update your PyMOL by typing @p in PyMOL command-line'
    cmd = "cd %s; load from_ndpplot.pdb" % (self.session.project.sparky_directory)
    msg = msg + '\n Manually run PyMOL and do "%s"' % \
                (cmd)
    msg = msg + ' if PyMOL does not launch correctly. ' + \
          'The command is in your clipboard now.'
    tkMessageBox.showinfo('Launch PyMOL...', msg)
    return nmrfam.run_pymol(self.session, ndpplot_pdb_path)
  # -----------------------------------------------------------------------------
  #
  def seq_align(self, pdb_file):
    ndpplot_pdb_path = os.path.join(self.session.project.sparky_directory, 
                                    'from_ndpplot.pdb')
    import swalign, wlutil
    # build sequence information from resonance list
    # self.session.project.condition_list().resonance_list()
    user_seq_list = []
    user_seqidx_list = []
    for cond in self.session.project.condition_list():
      for res in cond.resonance_list():
        if not res.group.symbol in swalign.m_singlea: continue
        if res.group.number < 1 or res.group.number > 999: continue
        user_seq_list.append(res.group.symbol)
        user_seqidx_list.append(res.group.number)

    user_seq, user_min_seq = wlutil.projlist(user_seq_list, user_seqidx_list)
        
    # read pdb. use the highest 'sum_blosum62' chain
    chain_seq_list = wlutil.ExtractSequenceFromPDB(pdb_file)
    max_blosum62 = -9999999
    best_chain = None
    for chain in chain_seq_list:
      seq_align_dict = swalign.do_swalign(user_seq, user_min_seq, \
                                chain[1], chain[2])
      if seq_align_dict['sum_blosum62'] > max_blosum62:
        best_chain = chain
        max_blosum62 = seq_align_dict['sum_blosum62']

    # perform sequence alignment and set seq_align_dict
    seq_align_dict = swalign.do_swalign(user_seq, user_min_seq, 
                                              best_chain[1], best_chain[2])
    seq_align_chain = best_chain[0]

    # make from_ndpplot.pdb  
    new_lines = swalign.transform(pdb_file, \
                  seq_align_dict, seq_align_chain, HETATM=True)
    f = open(ndpplot_pdb_path, 'w')
    f.write(new_lines)
    f.close()

def show_npd_dialog(session):
  sputil.the_dialog(show_npdplot_dialog,session).show_window(1)

# -----------------------------------------------------------------------------
# Generating fake assignment
#
def fake_assign(session):
  # check selected spectrum
  if session.selected_spectrum() == None:
    tkMessageBox.showerror("Error", "Please select N-HSQC first.")
    return
  spec = session.selected_spectrum() 
  if spec.dimension != 2:
    tkMessageBox.showerror("Error", "Please select N-HSQC first.")
    return      
  if (spec.nuclei[0] == '1H') and (spec.nuclei[1] == '15N'):
    iMode = 0
  elif (spec.nuclei[1] == '1H') and (spec.nuclei[0] == '15N'):
    iMode = 1
  else:      
    tkMessageBox.showerror("Error", "Please select N-HSQC first.")
    return
  if len(spec.peak_list()) == 0:
    tkMessageBox.showerror("Error", "Please pick peaks first.")
    return  
  if len(spec.selected_peaks()) == 0:  
    peak_list = spec.peak_list()  
  else:
    peak_list = spec.selected_peaks()
  
  iNum = 1  
  for peak in peak_list:
    if peak.is_assigned == 1: continue
    peak.assign(iMode, '%s' % (iNum), 'H')  
    peak.assign(1-iMode, '%s' % (iNum), 'N')
    iNum = iNum+1
  tkMessageBox.showinfo("Arbitrary assignment", "%d peaks assigned arbitrarily." % (iNum))        
