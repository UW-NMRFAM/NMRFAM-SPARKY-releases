# -----------------------------------------------------------------------------
# GetSBY (Get Secondary structure by PACSY)
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Dec 12, 2018
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
# Citation:
# 
#   Structural proteomics by NMR spectroscopy
#     J Shin, W Lee, W Lee - 2008, Expert Review of Proteomics
#   
#   Method to predict protein secondary structure using NMR spectroscopy
#     WLee, WLee - 2010 KR Patent Reg #1008899400000, App #102008008752
# -----------------------------------------------------------------------------
#
#  Current default setting is tri-peptide smoothing.
#
#

import tkMessageBox
from math import erf, sqrt
import math

singleline_aa = 'ARNDCQEGHILKMFPSTWYV'

def get_zscore(value, mean, dev):
  if dev == 0:
    return 0
  return (value - mean) / dev

def z2p(z):
  return 0.5 * (1+erf(z/sqrt(2)))
  
# alternative approach
def normpdf(x, mean, sd):
  var = float(sd)**2
  pi = 3.1415926
  denom = (2*pi*var)**.5
  num = math.exp(-(float(x)-float(mean))**2/(2*var))
  return num/denom
  
def getsby_index_atom(index):
  if index == 0: return 'H'  
  if index == 1: return 'N'  
  if index == 2: return 'C'
  if index == 3: return 'CA'
  if index == 4: return 'CB'
  if index == 5: return 'HA'  
  return ''      
  
def getsby_atom_index(atom):
  if (atom == 'H') or (atom == 'HN'): return 0
  if atom == 'N': return 1
  if (atom == 'C') or (atom == 'CO'): return 2
  if atom == 'CA': return 3
  if atom == 'CB': return 4  
  if atom == 'HA': return 5  
  return -1  
  
def run_getsby(session):
  iAAmode = 0
  if session.project == None:
    iAAmode = 1
    
  resonance_list = []  # [1, 'M', H_CS, N_CS, C_CS, CA_CS, CB_CS, HA_CS]
  
  h_mean_list = []
  h_dev_list = []
  h_zscore_list = []
  
  e_mean_list = []
  e_dev_list = []
  e_zscore_list = []

  t_mean_list = []
  t_dev_list = []
  t_zscore_list = []

  g_mean_list = []
  g_dev_list = []
  g_zscore_list = []

  c_mean_list = []
  c_dev_list = []
  c_zscore_list = []
  
  b_mean_list = []
  b_dev_list = []
  b_zscore_list = []
  
  hec_prob_list = []        # raw
  smooth_prob_list = []     # tri-peptide smoothing
  smooth2_prob_list = []    # pepta-peptide smoothing
  

  iMin = 999999
  iMax = -999999
  if iAAmode == 0:
    for condition in session.project.condition_list():    
      for resonance in condition.resonance_list():
        try:
          if iMin > resonance.group.number: iMin = resonance.group.number
          if iMax < resonance.group.number: iMax = resonance.group.number      
        except:
          pass
          
  if (iMin >= iMax):
    iAAmode = 1

  import myseq  
  if iAAmode == 1:
    read_seq = myseq.ReadSequence(session)  
    if len(read_seq) == 0:
      tkMessageBox.showerror('Error', 'Not supported sequence file.')
      return
    print read_seq
  else:
    group_list = []
    sequence_from_session = myseq.BuildSequence(session, 3)
    sequence = myseq.CheckSequence(sequence_from_session)
    if myseq.GapInSequence(sequence) == 1: # there is a gap
      tkMessageBox.showinfo('Gap', 'There is a gap between your assignment.\nYou need to specify a sequence file.')
      read_seq = myseq.LoadSeq(session, sequence)
      if read_seq == None:
        tkMessageBox.showerror('Sequence', 'Sequence information is not satisfactory.')
        return
    else:
      read_seq = sequence
  iMin = read_seq[0][0]
  iMax = read_seq[-1][0]
  
  try:
    for i in range(iMin, iMax+1):
#      curseq = 'X'
#      if iAAmode == 1: curseq = read_seq[i-iMin][1]
      curseq = read_seq[i-iMin][1]
      resonance_list.append([i, curseq, 9999,9999,9999,9999,9999,9999])
      h_mean_list.append([i, curseq, 9999,9999,9999,9999,9999,9999])
      h_dev_list.append([i, curseq, 9999,9999,9999,9999,9999,9999])
      e_mean_list.append([i, curseq, 9999,9999,9999,9999,9999,9999])
      e_dev_list.append([i, curseq, 9999,9999,9999,9999,9999,9999])
      c_mean_list.append([i, curseq, 9999,9999,9999,9999,9999,9999])
      c_dev_list.append([i, curseq, 9999,9999,9999,9999,9999,9999])
      t_mean_list.append([i, curseq, 9999,9999,9999,9999,9999,9999])
      t_dev_list.append([i, curseq, 9999,9999,9999,9999,9999,9999])
      g_mean_list.append([i, curseq, 9999,9999,9999,9999,9999,9999])
      g_dev_list.append([i, curseq, 9999,9999,9999,9999,9999,9999])
      b_mean_list.append([i, curseq, 9999,9999,9999,9999,9999,9999])
      b_dev_list.append([i, curseq, 9999,9999,9999,9999,9999,9999])      
  except:
    tkMessageBox.showerror('Error', 'Your assignments are not in general format- seg 1')    
    return
    
#  try:                
  # find real chemical shifts
  from pacsylayout import pacsy_ss_layout  
  from pacsylayout import pacsy_tripep_ss_count
  for condition in session.project.condition_list():    
    for resonance in condition.resonance_list():
      seqidx = resonance.group.number
      seq = resonance.group.symbol
      try:
        h_mean_list[seqidx-iMin][1] = seq
        e_mean_list[seqidx-iMin][1] = seq
        c_mean_list[seqidx-iMin][1] = seq
        g_mean_list[seqidx-iMin][1] = seq
        t_mean_list[seqidx-iMin][1] = seq
        b_mean_list[seqidx-iMin][1] = seq                        
        h_dev_list[seqidx-iMin][1] = seq
        e_dev_list[seqidx-iMin][1] = seq
        c_dev_list[seqidx-iMin][1] = seq 
        g_dev_list[seqidx-iMin][1] = seq 
        t_dev_list[seqidx-iMin][1] = seq 
        b_dev_list[seqidx-iMin][1] = seq                         
        resonance_list[seqidx-iMin][1] = seq
      except:
        tkMessageBox.showerror('Error', [seqidx, iMin])
        return
      if singleline_aa.find(seq) == -1: continue
      atomidx = getsby_atom_index(resonance.atom.name)
      if atomidx == -1: continue
      pacsy_key = '%s_%s' % (seq, getsby_index_atom(atomidx))  
      # check pacsy
      if not pacsy_ss_layout.has_key(pacsy_key): continue
      if pacsy_key == 'P_H': continue
      
      h_mean_list[seqidx-iMin][2+atomidx] = pacsy_ss_layout[pacsy_key]['SS_H'][0]
      h_dev_list[seqidx-iMin][2+atomidx] = pacsy_ss_layout[pacsy_key]['SS_H'][1]
      e_mean_list[seqidx-iMin][2+atomidx] = pacsy_ss_layout[pacsy_key]['SS_E'][0]
      e_dev_list[seqidx-iMin][2+atomidx] = pacsy_ss_layout[pacsy_key]['SS_E'][1]
      t_mean_list[seqidx-iMin][2+atomidx] = pacsy_ss_layout[pacsy_key]['SS_T'][0]
      t_dev_list[seqidx-iMin][2+atomidx] = pacsy_ss_layout[pacsy_key]['SS_T'][1]
      g_mean_list[seqidx-iMin][2+atomidx] = pacsy_ss_layout[pacsy_key]['SS_G'][0]
      g_dev_list[seqidx-iMin][2+atomidx] = pacsy_ss_layout[pacsy_key]['SS_G'][1]
      c_mean_list[seqidx-iMin][2+atomidx] = pacsy_ss_layout[pacsy_key]['SS_C'][0]
      c_dev_list[seqidx-iMin][2+atomidx] = pacsy_ss_layout[pacsy_key]['SS_C'][1]
      b_mean_list[seqidx-iMin][2+atomidx] = pacsy_ss_layout[pacsy_key]['SS_B'][0]
      b_dev_list[seqidx-iMin][2+atomidx] = pacsy_ss_layout[pacsy_key]['SS_B'][1]

      resonance_list[seqidx-iMin][2+atomidx] = resonance.frequency
#  except:
#    tkMessageBox.showerror('Error', [pacsy_key, seqidx, atomidx, iMin, iMax])
#    tkMessageBox.showerror('Error', 'Your assignments are not in general format- seg 2')
#    return
  
  try:  
    # start calculate z-score -> keep negative
    for i in range(iMin, iMax+1):
      resonance = resonance_list[i-iMin]
      h_mean = h_mean_list[i-iMin]
      e_mean = e_mean_list[i-iMin]
      c_mean = c_mean_list[i-iMin]
      g_mean = g_mean_list[i-iMin]      
      t_mean = t_mean_list[i-iMin]
      b_mean = b_mean_list[i-iMin]            
      h_dev = h_dev_list[i-iMin]
      e_dev = e_dev_list[i-iMin]
      c_dev = c_dev_list[i-iMin]            
      g_dev = g_dev_list[i-iMin]            
      t_dev = t_dev_list[i-iMin]            
      b_dev = b_dev_list[i-iMin]                              
      
      # H
      zvalue = [i, resonance[1], 0, 0, 0, 0, 0, 0]
      pvalue = [i, resonance[1], 1, 1, 1, 1, 1, 1]
      hprob = 1.0    
      for j in range(2, 8):
        zvalue[j] = abs(get_zscore(resonance[j], h_mean[j], h_dev[j])) * -1.
        #pvalue[j] = z2p(zvalue[j])*2.
        pvalue[j] = normpdf(resonance[j], h_mean[j], h_dev[j])
        hprob = hprob * pvalue[j]
      h_zscore_list.append(zvalue)
      
      # E
      zvalue = [i, resonance[1], 0, 0, 0, 0, 0, 0]
      pvalue = [i, resonance[1], 1, 1, 1, 1, 1, 1]
      eprob = 1.0    
      for j in range(2, 8):
        zvalue[j] = abs(get_zscore(resonance[j], e_mean[j], e_dev[j])) * -1.
        #pvalue[j] = z2p(zvalue[j])*2.      
        pvalue[j] = normpdf(resonance[j], e_mean[j], e_dev[j])
        eprob = eprob * pvalue[j]      
      e_zscore_list.append(zvalue)

      # T
      zvalue = [i, resonance[1], 0, 0, 0, 0, 0, 0]
      pvalue = [i, resonance[1], 1, 1, 1, 1, 1, 1]
      tprob = 1.0    
      for j in range(2, 8):
        zvalue[j] = abs(get_zscore(resonance[j], t_mean[j], t_dev[j])) * -1.
        #pvalue[j] = z2p(zvalue[j])*2.      
        pvalue[j] = normpdf(resonance[j], t_mean[j], t_dev[j])
        tprob = tprob * pvalue[j]      
      t_zscore_list.append(zvalue)
          
      # G
      zvalue = [i, resonance[1], 0, 0, 0, 0, 0, 0]
      pvalue = [i, resonance[1], 1, 1, 1, 1, 1, 1]
      gprob = 1.0    
      for j in range(2, 8):
        zvalue[j] = abs(get_zscore(resonance[j], g_mean[j], g_dev[j])) * -1.
        #pvalue[j] = z2p(zvalue[j])*2.      
        pvalue[j] = normpdf(resonance[j], g_mean[j], g_dev[j])
        gprob = gprob * pvalue[j]      
      g_zscore_list.append(zvalue)      
          
      # C
      zvalue = [i, resonance[1], 0, 0, 0, 0, 0, 0]
      pvalue = [i, resonance[1], 1, 1, 1, 1, 1, 1]
      cprob = 1.0    
      for j in range(2, 8):
        zvalue[j] = abs(get_zscore(resonance[j], c_mean[j], c_dev[j])) * -1.
        #pvalue[j] = z2p(zvalue[j])*2.      
        pvalue[j] = normpdf(resonance[j], c_mean[j], c_dev[j])
        cprob = cprob * pvalue[j]      
      c_zscore_list.append(zvalue)
      
      # B
      zvalue = [i, resonance[1], 0, 0, 0, 0, 0, 0]
      pvalue = [i, resonance[1], 1, 1, 1, 1, 1, 1]
      bprob = 1.0    
      for j in range(2, 8):
        zvalue[j] = abs(get_zscore(resonance[j], b_mean[j], b_dev[j])) * -1.
        #pvalue[j] = z2p(zvalue[j])*2.      
        pvalue[j] = normpdf(resonance[j], b_mean[j], b_dev[j])
        bprob = bprob * pvalue[j]
      b_zscore_list.append(zvalue)

      hprob = hprob + gprob
      eprob = eprob + bprob
      cprob = cprob + tprob
      
      # count
      if (i != iMin) and (i != iMax):
        a1 = resonance_list[i-iMin-1][1]        
        a2 = resonance_list[i-iMin][1]    
        a3 = resonance_list[i-iMin+1][1]        
        if pacsy_tripep_ss_count.has_key(a1+a2+a3):
          ss_count = pacsy_tripep_ss_count[a1+a2+a3]  # H, E, T, C, G, B
          sum_count = sum(ss_count[0:6])
          if sum_count != 0:
            hprob_c = float(ss_count[0]+ss_count[4]) / float(sum_count)
            eprob_c = float(ss_count[1]+ss_count[5]) / float(sum_count)
            cprob_c = float(ss_count[2]+ss_count[3]) / float(sum_count)
            hprob = hprob * hprob_c
            eprob = eprob * eprob_c
            cprob = cprob * cprob_c                    
          
      sumprob = hprob+eprob+cprob
      if sumprob <> 0:
        rprob = [i, resonance[1], hprob / sumprob, eprob / sumprob, cprob / sumprob]
      else:
        rprob = [i, resonance[1], 0,0,0]
      for j in range(2, 5):    
        rprob[j] = rprob[j] - 0.33
        if rprob[j] < 0: rprob[j] = 0.0
        rprob[j] = rprob[j]*100./66.7
        if rprob[j] > 1.0: rprob[j] = 1.0

  #### NO SMOOTHING ##########################
      hec_prob_list.append(rprob)
  #### NO SMOOTHING END ######################
   
  except:
    tkMessageBox.showerror('Error', 'Error occured during probability calculation.')    
    return
    
  try:    
  #### tri-peptide SMOOTHING #################   
    if iMin != iMax:
      rprob1 = hec_prob_list[0]
      rprob2 = hec_prob_list[1]
      smooth = [iMin, rprob1[1],(rprob1[2]+rprob2[2])/2.0,(rprob1[3]+rprob2[3])/2.0,(rprob1[4]+rprob2[4])/2.0]
      smooth_prob_list.append(smooth)
    else:
      smooth_prob_list.append(hec_prob_list[0])
    for i in range(iMin+1, iMax):
      rprob1 = hec_prob_list[i-iMin-1]
      rprob2 = hec_prob_list[i-iMin]
      rprob3 = hec_prob_list[i-iMin+1]
      smooth = [i, rprob2[1],(rprob1[2]+rprob2[2]+rprob3[2])/3.0,(rprob1[3]+rprob2[3]+rprob3[3])/3.0,(rprob1[4]+rprob2[4]+rprob3[4])/3.0]
      smooth_prob_list.append(smooth)
    if iMin != iMax:
      rprob1 = hec_prob_list[-1]
      rprob2 = hec_prob_list[-2]
      smooth = [iMax, rprob1[1],(rprob1[2]+rprob2[2])/2.0,(rprob1[3]+rprob2[3])/2.0,(rprob1[4]+rprob2[4])/2.0]
      smooth_prob_list.append(smooth)
    else:
      smooth_prob_list.append(hec_prob_list[-1])  
  #### SMOOTHING END##########################    
  except:
    tkMessageBox.showerror('Error', 'Error occured during tri-peptide smoothing.')    
    return
  
  try:  
  #### pepta-peptide SMOOTHING #################
    smooth2_prob_list.append(hec_prob_list[0])
    smooth2_prob_list.append(hec_prob_list[1])
    for i in range(iMin+2, iMax-1):
      rprob1 = hec_prob_list[i-iMin-2]
      rprob2 = hec_prob_list[i-iMin-1]
      rprob3 = hec_prob_list[i-iMin]
      rprob4 = hec_prob_list[i-iMin+1]
      rprob5 = hec_prob_list[i-iMin+2]
      smooth2 = [i, rprob3[1],(rprob1[2]+rprob2[2]+rprob3[2]+rprob4[2]+rprob5[2])/5.0,(rprob1[3]+rprob2[3]+rprob3[3]+rprob4[3]+rprob5[3])/5.0,(rprob1[4]+rprob2[4]+rprob3[4]+rprob4[4]+rprob5[4])/5.0]
      smooth2_prob_list.append(smooth2)
    smooth2_prob_list.append(hec_prob_list[-2])
    smooth2_prob_list.append(hec_prob_list[-1])    
  #### SMOOTHING END##########################  
  except:
    tkMessageBox.showerror('Error', 'Error occured during pepta-peptide smoothing.')    
    return
      

  try:      
    # writing - ini
    import os.path
    f = open(os.path.join(os.path.expanduser("~"), 'ndpplot.ini'), 'w')
    f.write('[GENERAL_START]\n')
    f.write('TITLE=GetSBY secondary structure prediction\n')
    f.write('XLABEL=Residue number\n')    
    f.write('YLABEL=Probability\n')        
    f.write('XMIN=%d\n' % iMin)
    f.write('XMAX=%d\n' % iMax)
    f.write('YMIN=-1.0\n')
    f.write('YMAX=1.0\n')
    f.write('XSCALE=INT\n')    
    f.write('[GENERAL_END]\n')
    
    f.write('[SERIES1_START]\n')
    f.write('NAME=Helix\n')
    f.write('PLOTTYPE=BAR\n')
    f.write('COLORCOUNT=10\n')
    f.write('DATACOUNT=%d\n' % len(hec_prob_list))
    for i in range(1, 11):
      f.write('COLOR_%d=%d,%d,%f,%f,%d_255_%d\n' % (i, iMin, iMax, float(i)*0.1-0.1,float(i)*0.1,275-25*i,275-25*i))  

    for i in range(1, len(hec_prob_list)+1):
      ## raw start
      #data = hec_prob_list[i-1]
      ## raw end
      
      ## tripeptide-smooth start
      data = smooth_prob_list[i-1]
      ## tripeptide-smooth end
      
      ## pentapeptide-smooth start
      #data = smooth2_prob_list[i-1]
      ## pentapeptide-smooth end  
        
      if data[1] == 'X':
        f.write('DATA_%d=%d,0,0,%s%d\n' % (i, data[0], data[1],data[0]))    
      else:    
        f.write('DATA_%d=%d,%f,0,%s%d\n' % (i, data[0], data[2],data[1],data[0]))
    f.write('[SERIES1_END]\n')
    f.write('[SERIES2_START]\n')
    f.write('NAME=Strand\n')
    f.write('PLOTTYPE=BAR\n')
    f.write('COLORCOUNT=10\n')
    f.write('DATACOUNT=%d\n' % len(hec_prob_list))
    for i in range(1, 11):
      f.write('COLOR_%d=%d,%d,%f,%f,%d_%d_255\n' % (i, iMin, iMax, -0.1*float(i),0.1-float(i)*0.1,275-25*i,275-25*i))  
    for i in range(1, len(hec_prob_list)+1):
      ## raw start
      #data = hec_prob_list[i-1]
      ## raw end
      
      ## tripeptide-smooth start
      data = smooth_prob_list[i-1]
      ## tripeptide-smooth end
      
      ## pentapeptide-smooth start
      #data = smooth2_prob_list[i-1]
      ## pentapeptide-smooth end  
        
      if data[1] == 'X':
        f.write('DATA_%d=%d,0,0,%s%d\n' % (i, data[0], data[1],data[0]))
      else:  
        f.write('DATA_%d=%d,-%f,0,%s%d\n' % (i, data[0], data[3],data[1],data[0]))    
    f.write('[SERIES2_END]\n')
      
    ## middle line
    f.write('[SERIES3_START]\n')
    f.write('NAME=Middle\n')
    f.write('PLOTTYPE=LINE\n')
    f.write('COLORCOUNT=1\n')
    f.write('DATACOUNT=2\n')  
    f.write('COLOR_1=%d,%d,%f,%f,SILVER\n' % (iMin, iMax, -1.0,1.0))
    f.write('DATA_1=%d,0\n' % (iMin))
    f.write('DATA_2=%d,0\n' % (iMax))  
    f.write('[SERIES3_END]\n')  
    f.close()  

    # writing - csv
    f = open(os.path.join(os.path.expanduser("~"), 'GetSBY_analysis.csv'), 'w')
    f.write('GROUP,SEQ,IDX,H_PROB,E_PROB,H_TRI_SMOOTH_PROB,E_TRI_SMOOTH_PROB,H_PENTA_SMOOTH_PROB,E_PENTA_SMOOTH_PROB\n')
    for i in range(1, len(hec_prob_list)+1):
      data = hec_prob_list[i-1]
      smooth_data = smooth_prob_list[i-1]
      smooth2_data = smooth2_prob_list[i-1]    
      if data[1] == 'X':
        f.write('X%d,X,%d,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f\n' % (data[0], data[0],data[2],data[3],smooth_data[2],smooth_data[3],smooth2_data[2],smooth2_data[3]))    
      else:    
        f.write('%s%d,%s,%d,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f\n' % (data[1], data[0], data[1], data[0],data[2],data[3],smooth_data[2],smooth_data[3],smooth2_data[2],smooth2_data[3]))
    f.close()           
      #tkMessageBox.showinfo('Saved', 'Report file saved: %s' % os.path.join(os.path.dirname(session.project.save_path), 'GetSBY_analysis.csv'))        
  except:
    tkMessageBox.showerror('Error', 'Error occured during writing NDPPlot inputs.')    
    return
    
  
  # copy 
  try:
    import tkutil
    path = tkutil.save_file(session.tk, "Save GetSBY .csv report", "GetSBY_analysis.csv")
    if path: 
      import shutil
      shutil.copyfile(os.path.join(os.path.expanduser("~"), 'GetSBY_analysis.csv'), path)
    import nmrfam
    nmrfam.run_npdplot(session)    
  except:
    tkMessageBox.showerror('Error', 'Error occured during writing analytics.')    
    return
    
  pass
