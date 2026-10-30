# -----------------------------------------------------------------------------
# Simulation of chemical shift by PACSY
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: July 22, 2014
# 
# 
# -----------------------------------------------------------------------------
import string
import types
import Tkinter

import atoms
import pyutil
import sparky
import pinelayout
import pacsylayout
import pacsyweight
import tan
import talos
import pecan
import tkMessageBox
import myseq

# -----------------------------------------------------------------------------
def TupleIndex(tupleTarget, strTarget):
    for i in range(len(tupleTarget)):
        if tupleTarget[i] == strTarget:
            return i
    return i    
# ----------------------------------------------------------------------------
# from statistics
def GetSimFreq(session, tan_diag, group, szAtom):
    if group == None:
      return 9999, 9999, 0
    szGroupAtom = '%s_%s' % (group.symbol[0], szAtom)

    mean = []
    stddev = []
    count = []
    stat_type = []
    src_type = []    
    all_layout_set = []
    if pacsylayout.pacsy_all_layout.has_key(szGroupAtom):
      layout = pacsylayout.pacsy_all_layout[szGroupAtom]
      all_layout_set = layout["All"]
    else:
      # try bmrb
      import shiftstats
      ast = shiftstats.atom_statistics(group.symbol[0], szAtom)
      if ast == None:      return 9999, 9999, 0
      return ast.average_shift, ast.shift_deviation, 0
      
    if (tan_diag.COND_cb.state() == 0) and (tan_diag.PECAN_cb.state() == 0) and (tan_diag.TALOS_cb.state() == 0):      
      # find in bmrb
      dCS = myseq.GetExternalFreq(session, group.number, group.symbol[0], szAtom, tan_diag.bmrb_list)
      if dCS < 1000:
        return dCS, all_layout_set[1], all_layout_set[2]
      # find in shiftx2
      dCS = myseq.GetExternalFreq(session, group.number, group.symbol[0], szAtom, tan_diag.shiftx_list)
      if dCS < 1000:
        return dCS, all_layout_set[1], all_layout_set[2]
      return all_layout_set[0], all_layout_set[1], all_layout_set[2]

    prev_group = tan_diag.get_group(group.number-1)
    if prev_group != None:
      szPrev = 'PREV_' + prev_group.symbol
    else:
      szPrev = 'PREV_X'
    next_group = tan_diag.get_group(group.number+1)
    if next_group != None:
      szNext= 'NEXT_' + next_group.symbol
    else:
      szNext = 'NEXT_X'
    
    # PH
    layout = pacsylayout.pacsy_ph_layout
    #om_selection = tan_diag.ph_list.index(tan_diag.PH_om.get())
    om_selection = TupleIndex(tan_diag.ph_list, tan_diag.PH_om.get() )
    stat_type.append('ph')
    src_type.append('user')
    if om_selection == 0:
      mean.append(9999)
      stddev.append(9999)
      count.append(0)
    else:
      if not layout.has_key(szGroupAtom):
        mean.append(9999)
        stddev.append(9999)
        count.append(0)
      else:
        szKey = tan_diag.ph_list2[om_selection]
        layout2 = layout[szGroupAtom]
        if not layout2.has_key(szKey):
          mean.append(9999)
          stddev.append(9999)
          count.append(0)                                        
        else:
          layout3 = layout2[szKey]
          mean.append(layout3[0])
          stddev.append(layout3[1])
          count.append(layout3[2])
    # TEMP
    layout = pacsylayout.pacsy_temp_layout
    #om_selection = list(tan_diag.temp_list).index(tan_diag.TEMP_om.get())
    om_selection = TupleIndex(tan_diag.temp_list, tan_diag.TEMP_om.get() )
    stat_type.append('temp')
    src_type.append('user')
    if om_selection == 0:
      mean.append(9999)
      stddev.append(9999)
      count.append(0)
    else:
      if not layout.has_key(szGroupAtom):
        mean.append(9999)
        stddev.append(9999)
        count.append(0)       
      else:
        szKey = tan_diag.temp_list2[om_selection]
        layout2 = layout[szGroupAtom]
        if not layout2.has_key(szKey):
          mean.append(9999)
          stddev.append(9999)
          count.append(0)                
        else:
          layout3 = layout2[szKey]
          mean.append(layout3[0])
          stddev.append(layout3[1])
          count.append(layout3[2])    
    # OTHER
    # PHI
    layout = pacsylayout.pacsy_phi_layout
    #om_selection = list(tan_diag.TA_list).index(tan_diag.PHI_om.get())
    om_selection = TupleIndex(tan_diag.TA_list, tan_diag.PHI_om.get() )    
    stat_type.append('phi')
    src_type.append('user')
    if om_selection == 0:
      mean.append(9999)
      stddev.append(9999)
      count.append(0)
    elif tan_diag.COND_cb.state() == 1:
      if not layout.has_key(szGroupAtom):
        mean.append(9999)
        stddev.append(9999)
        count.append(0)      
      else:
        szKey = tan_diag.TA_list2[om_selection]
        layout2 = layout[szGroupAtom]
        if not layout2.has_key(szKey):
          mean.append(9999)
          stddev.append(9999)
          count.append(0)                
        else:
          layout3 = layout2[szKey]
          mean.append(layout3[0])
          stddev.append(layout3[1])
          count.append(layout3[2])    
    # PSI
    layout = pacsylayout.pacsy_psi_layout
    #om_selection = list(tan_diag.TA_list).index(tan_diag.PSI_om.get())
    om_selection = TupleIndex(tan_diag.TA_list, tan_diag.PSI_om.get() )  
    stat_type.append('psi')
    src_type.append('user')      
    if om_selection == 0:
      mean.append(9999)
      stddev.append(9999)
      count.append(0)
    elif tan_diag.COND_cb.state() == 1:
      if not layout.has_key(szGroupAtom):
        mean.append(9999)
        stddev.append(9999)
        count.append(0)      
      else:
        szKey = tan_diag.TA_list3[om_selection]
        layout2 = layout[szGroupAtom]
        if not layout2.has_key(szKey):
          mean.append(9999)
          stddev.append(9999)
          count.append(0)                
        else:
          layout3 = layout2[szKey]
          mean.append(layout3[0])
          stddev.append(layout3[1])
          count.append(layout3[2])    
    # SS
    layout = pacsylayout.pacsy_ss_layout
    #om_selection = list((tan_diag.SS_list).index(tan_diag.SS_om.get())
    om_selection = TupleIndex(tan_diag.SS_list, tan_diag.SS_om.get() )        
    stat_type.append('ss')
    src_type.append('user')  
    if om_selection == 0:
      mean.append(9999)
      stddev.append(9999)
      count.append(0)
    elif tan_diag.COND_cb.state() == 1:
      if not layout.has_key(szGroupAtom):
        mean.append(9999)
        stddev.append(9999)
        count.append(0)   
      else:
        szKey = tan_diag.SS_list2[om_selection]
        layout2 = layout[szGroupAtom]
        if not layout2.has_key(szKey):
          mean.append(9999)
          stddev.append(9999)
          count.append(0)          
        else:
          layout3 = layout2[szKey]
          mean.append(layout3[0])
          stddev.append(layout3[1])
          count.append(layout3[2])    
    # BURIEDNESS          
    layout = pacsylayout.pacsy_core_layout
    #om_selection = list(tan_diag.core_list).index(tan_diag.CORE_om.get())
    om_selection = TupleIndex(tan_diag.core_list, tan_diag.CORE_om.get() )        
    stat_type.append('buriedness')
    src_type.append('user')  
    if om_selection == 0:
      mean.append(9999)
      stddev.append(9999)
      count.append(0)
    elif tan_diag.COND_cb.state() == 1:
      if not layout.has_key(szGroupAtom):
        mean.append(9999)
        stddev.append(9999)
        count.append(0)        
      else:
        szKey = tan_diag.core_list2[om_selection]
        layout2 = layout[szGroupAtom]
        if not layout2.has_key(szKey):
          mean.append(9999)
          stddev.append(9999)
          count.append(0)                
        else:
          layout3 = layout2[szKey]
          mean.append(layout3[0])
          stddev.append(layout3[1])
          count.append(layout3[2])   
                  
    # PREV
    layout = pacsylayout.pacsy_prev_layout
    #om_selection = list(tan_diag.AA_list).index(tan_diag.PREV_om.get())
    om_selection = TupleIndex(tan_diag.AA_list, tan_diag.PREV_om.get() ) 
    stat_type.append('prev')
    src_type.append('user')
    if om_selection == 0:
      mean.append(9999)
      stddev.append(9999)
      count.append(0)
    elif tan_diag.COND_cb.state() == 1:
      if not layout.has_key(szGroupAtom):
        mean.append(9999)
        stddev.append(9999)
        count.append(0)       
      else:
        szKey = tan_diag.AA_list2[om_selection]
        if om_selection == 21:
          szKey = szPrev
        layout2 = layout[szGroupAtom]
        if not layout2.has_key(szKey):
          mean.append(9999)
          stddev.append(9999)
          count.append(0)                
        else:
          layout3 = layout2[szKey]
          mean.append(layout3[0])
          stddev.append(layout3[1])
          count.append(layout3[2])
    # NEXT
    layout = pacsylayout.pacsy_next_layout
    #om_selection = list(tan_diag.AA_list).index(tan_diag.NEXT_om.get())
    om_selection = TupleIndex(tan_diag.AA_list, tan_diag.NEXT_om.get() )            
    stat_type.append('next')
    src_type.append('user')
    if om_selection == 0:
      mean.append(9999)
      stddev.append(9999)
      count.append(0)
    elif tan_diag.COND_cb.state() == 1:
      if not layout.has_key(szGroupAtom):
        mean.append(9999)
        stddev.append(9999)
        count.append(0)       
      else:
        szKey = tan_diag.AA_list2[om_selection]
        if om_selection == 21:
          szKey = szNext
        #szKey = tan_diag.AA_list2[om_selection]
        layout2 = layout[szGroupAtom]
        if not layout2.has_key(szKey):
          mean.append(9999)
          stddev.append(9999)
          count.append(0)   
        else:
          layout3 = layout2[szKey]
          mean.append(layout3[0])
          stddev.append(layout3[1])
          count.append(layout3[2])  
          
    # EXTERNAL INFORMATION
    # PECAN: SEQUENCE, SS      
    # TALOS: SEQUENCE, PHI, PSI
    # PECAN
    #szGroupAtom = '%s_%s' % (group.symbol, szAtom)   
    # sequence index: group.numbeself.groupsr
    # s 
    # {1: ("MET", "M", helix prob, strand prob, loop prob),
    if tan_diag.PECAN_cb.state() == 1:
      pecan_dict = pecan.ReadPecan(tan_diag.pecan_file.get())     
      if pecan_dict.has_key(group[1]):
        pecan_result = pecan_dict[group[1]]
        # ss
        szA = pecan_result[1]
        dHelixProb = pecan_result[2]
        dSheetProb = pecan_result[3]        
        dLoopProb = pecan_result[4]
        
        layout = pacsylayout.pacsy_ss_layout
        if layout.has_key(szGroupAtom):
          layout2 = layout[szGroupAtom]
          if layout2.has_key("SS_H"):
            layout3 = layout2["SS_H"]
            mean.append(layout3[0])
            stddev.append(layout3[1])
            count.append(int(dHelixProb * layout3[2]))       
            stat_type.append('ss')
            src_type.append('pecan')
            
          if layout2.has_key("SS_E"):
            layout3 = layout2["SS_E"]
            mean.append(layout3[0])
            stddev.append(layout3[1])
            count.append(int(dSheetProb * layout3[2]))
            stat_type.append('ss')
            src_type.append('pecan')
                      
          if layout2.has_key("SS_C"):
            layout3 = layout2["SS_C"]
            mean.append(layout3[0])
            stddev.append(layout3[1])
            count.append(int(dLoopProb * layout3[2]))   
            stat_type.append('ss')
            src_type.append('pecan')
        
        # prev
        if pecan_dict.has_key(group[0]-1):
          pecan_result_prev = pecan_dict[group[1]-1]
          layout = pacsylayout.pacsy_prev_layout          
          if layout.has_key(szGroupAtom):
            layout2 = layout[szGroupAtom]                      
            prev_key = "PREV_" + pecan_result_prev[1]            
            if layout2.has_key(prev_key):
              layout3 = layout2[prev_key]
              mean.append(layout3[0])
              stddev.append(layout3[1])
              count.append(layout3[2])         
              stat_type.append('prev')
              src_type.append('pecan')
          
        # next
        if pecan_dict.has_key(group.number+1):
          pecan_result_next = pecan_dict[group.number+1]
          layout = pacsylayout.pacsy_next_layout          
          if layout.has_key(szGroupAtom):
            layout2 = layout[szGroupAtom]                      
            next_key = "NEXT_" + pecan_result_next[1]            
            if layout2.has_key(next_key):
              layout3 = layout2[next_key]
              mean.append(layout3[0])
              stddev.append(layout3[1])
              count.append(layout3[2])          
              stat_type.append('next')
              src_type.append('pecan')
    # TALOS
    # 1: ("MET", "M", phi, psi, dphi, dpsi, "Strong")    
    TA_list2 = ('PHI_-180_-150', 'PHI_-165_-135', 'PHI_-150_-120', 'PHI_-135_-105', 'PHI_-120_-90', 'PHI_-105_-75', 'PHI_-90_-60', 'PHI_-75_-45', 'PHI_-60_-30', 'PHI_-45_-15', 'PHI_-30_0', 'PHI_-15_15', 'PHI_0_30', 'PHI_15_45', 'PHI_30_60', 'PHI_45_75', 'PHI_60_90', 'PHI_75_105', 'PHI_90_120', 'PHI_105_135', 'PHI_120_150', 'PHI_135_165', 'PHI_150_180')    
    TA_list3 = ('PSI_-180_-150', 'PSI_-165_-135', 'PSI_-150_-120', 'PSI_-135_-105', 'PSI_-120_-90', 'PSI_-105_-75', 'PSI_-90_-60', 'PSI_-75_-45', 'PSI_-60_-30', 'PSI_-45_-15', 'PSI_-30_0', 'PSI_-15_15', 'PSI_0_30', 'PSI_15_45', 'PSI_30_60', 'PSI_45_75', 'PSI_60_90', 'PSI_75_105', 'PSI_90_120', 'PSI_105_135', 'PSI_120_150', 'PSI_135_165', 'PSI_150_180')      
    if tan_diag.TALOS_cb.state() == 1:
      talos_dict = talos.ReadTalos(tan_diag.talos_file.get())     
                
      if talos_dict.has_key(group.number):
        talos_result = talos_dict[group.number]

        if (talos_result[6] == "Strong") or (talos_result[6] == "Good") or (talos_result[6] == "Generous"):
          iPhiIdx = int((talos_result[2] + 180.0) / 15.0)
          iPsiIdx = int((talos_result[3] + 180.0) / 15.0)
          # phi          
          if (iPhiIdx > -1) and (iPhiIdx < 23) and (pacsylayout.pacsy_phi_layout.has_key(szGroupAtom)):
            szKey = TA_list2[iPhiIdx]
            layout = pacsylayout.pacsy_phi_layout[szGroupAtom]
            if layout.has_key(TA_list2[iPhiIdx]):
              layout2 = layout[TA_list2[iPhiIdx]]
              mean.append(layout2[0])
              stddev.append(layout2[1])
              count.append(layout2[2])    
              stat_type.append('phi')
              src_type.append('talos')
            
          # psi        
          if (iPsiIdx > -1) and (iPsiIdx < 23) and (pacsylayout.pacsy_psi_layout.has_key(szGroupAtom)):
            szKey = TA_list3[iPsiIdx]
            layout = pacsylayout.pacsy_psi_layout[szGroupAtom]
            if layout.has_key(TA_list3[iPsiIdx]):
              layout2 = layout[TA_list3[iPsiIdx]]
              mean.append(layout2[0])
              stddev.append(layout2[1])
              count.append(layout2[2]) 
              stat_type.append('psi')         
              src_type.append('talos')      
                                
        # prev
        if talos_dict.has_key(group.number-1):
          talos_result_prev = talos_dict[group.number-1]
          layout = pacsylayout.pacsy_prev_layout          
          if layout.has_key(szGroupAtom):
            layout2 = layout[szGroupAtom]                      
            prev_key = "PREV_" + talos_result_prev[1]            
            if layout2.has_key(prev_key):
              layout3 = layout2[prev_key]
              mean.append(layout3[0])
              stddev.append(layout3[1])
              count.append(layout3[2])  
              stat_type.append('prev') 
              src_type.append('talos')      
          
        # next
        if talos_dict.has_key(group.number+1):
          talos_result_next = talos_dict[group.number+1]
          layout = pacsylayout.pacsy_next_layout          
          if layout.has_key(szGroupAtom):
            layout2 = layout[szGroupAtom]                      
            next_key = "NEXT_" + talos_result_next[1]            
            if layout2.has_key(next_key):
              layout3 = layout2[next_key]
              mean.append(layout3[0])
              stddev.append(layout3[1])
              count.append(layout3[2])
              stat_type.append('next')  
              src_type.append('talos')

    sumMean = 0.0
    sumStdDev = 0.0
    sumCount = 0
          
    for i in range(len(mean)):
      if (count[i] < 30) or (mean[i] > 9000) :     # drop irregular
        continue
      sumMean = sumMean + mean[i] * float(count[i])
      sumCount = sumCount + count[i]
      sumStdDev = sumStdDev + stddev[i] * float(count[i])
    if sumCount == 0:
      return all_layout_set[0], all_layout_set[1], all_layout_set[2]
      
    return sumMean / float(sumCount), sumStdDev / float(sumCount), sumCount  
      
        
    # average per type
    #prev, curr, next, ss, phi, psi, buriedness, temp, ph, total
    """type_count = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    type_sum = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    type_avg = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    
    # curr    
    type_count[1] = all_layout_set[2]
    type_sum[1] = all_layout_set[0] * all_layout_set[2]
    type_avg[2] = all_layout_set[0]
    if pacsyweight.pacsy_weight_layout.has_key(szAtom):
      curr_pacsy_weight = pacsyweight.pacsy_weight_layout[szAtom]
    else:
      curr_pacsy_weight = pacsyweight.pacsy_weight_layout['other']
      #szAtom[0]+'X'
    sumCount = 0
    for i in range(len(mean)):
      if (count[i] < 30) or (mean[i] > 9000) :     # drop irregular
        count[i] = 0
      if count[i] == 0: continue
      type_index = pacsyweight.pacsy_weight_type.index(stat_type[i])
      type_count[type_index] = type_count[type_index] + count[i]
      type_sum[type_index] = type_sum[type_index] + mean[i] * count[i]
      sumCount = sumCount + count[i]
      #szText = '%s,%s,%f\n' % (src_type[i], stat_type[i], mean[i])
      #tkMessageBox.showinfo('mid', szText)
    sumRelInf = 0.0
    for i in range(8):
      if type_count[i] == 0: continue
      type_avg[i] = type_sum[1] / type_count[1]    # avg for each type
      sumRelInf = sumRelInf + curr_pacsy_weight[i]
    if sumRelInf < 0.1:
      return all_layout_set[0], all_layout_set[1], all_layout_set[2]

    sumMean = 0.0
    sumStdDev = 0.0

    for i in range(8):
      sumMean = sumMean + type_avg[i] * curr_pacsy_weight[i]
    #szText = '%f,%d\n' % (sumMean / sumRelInf, sumCount)
    #tkMessageBox.showinfo('sim', szText)
    return sumMean / sumRelInf, 0, sumCount  """
    

