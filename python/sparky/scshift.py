# -----------------------------------------------------------------------------
# Secondary Chemical Shift Analysis
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: March 1, 2016
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
import os
import tkutil
import sputil
import Tkinter
import tkFileDialog
import tkMessageBox
import myseq
import pacsylayout

singleline_aa = 'ARNDCQEGHILKMFPSTWYV'

# -----------------------------------------------------------------------------
#
class scshift_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    tkutil.Dialog.__init__(self, session.tk, 'Secondary Chemical Shift Analysis')
    self.session = session

    self.text1_text = Tkinter.StringVar()    
    self.text1 = Tkinter.Label(self.top, textvariable = self.text1_text, anchor = 'w', justify = 'left')		
    self.text1.pack(side = 'top', anchor = 'w')
    self.text1_text.set("PACSY DB is used to reference coil chemical shifts.")
  
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')    
    
    self.text1_text = Tkinter.StringVar()    
    self.text1 = Tkinter.Label(self.top, textvariable = self.text1_text, anchor = 'w', justify = 'left')		
    self.text1.pack(side = 'top', anchor = 'w')
    self.text1_text.set("ddCS = dCS1 - dCS2, while dCS = CS(obs) - CS(coil)")
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')    
    
    # observable_list
    self.observable_list = ("dH", "dN", "dC", "dCA", "dCB", "dHA/HA2", "dHB/HB2", "Zero")
    self.observable_list2 = ("H", "N", "C", "CA", "CB", "HA", "HB", "Zero")
    
    # CS1
    self.obs1 = tkutil.option_menu(self.top, "dCS1: ", self.observable_list, "dCA")    
    self.obs1.frame.pack(side = 'top', fill = 'both')    
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    # CS2
    self.obs2 = tkutil.option_menu(self.top, "dCS2: ", self.observable_list, "dCB")
    self.obs2.frame.pack(side = 'top', fill = 'both')    
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
            
    # Buttons
    self.br = tkutil.button_row(self.top, 
          ('Analyze', self.analyze_cb),
          ('Plot...', self.plot_cb),
          ('Export to CSV', self.export_cb),
          ('Close', self.close_cb),
          )
    self.br.frame.pack(side = 'top', fill = 'both')      
    
    # Analyzed Data
    # scroll_list
    self.listbox = tkutil.scrolling_list(self.top, 'Analyzed Data', 10)    
    self.listbox.frame.pack(side = 'top', fill = 'both', expand = 1)

    # file names
    self.ini_path = os.path.join(os.path.expanduser("~"), 'ndpplot.ini')
    self.csv_path = os.path.join(os.path.expanduser("~"), 'ndpplot.csv')
    
  # -----------------------------------------------------------------------------
  #        
  def analyze_cb(self):
    self.listbox.clear()
    
    # sequence
    seqgroup_list = myseq.BuildSequence(self.session, 3)
    seqgroup_list = myseq.CheckSequence(seqgroup_list) # sort and fill the gap
    
    # group.number, aaa, atom.name, atom_type, isotope, frequency, deviation
    resonancegroup_list = myseq.BuildResonance(self.session)
    if len(resonancegroup_list) < 2:
      tkMessageBox.showerror("Error", "Not enough assignment available.")      
      return 0
      
    iFirst = resonancegroup_list[0][0]
    iLast = resonancegroup_list[-1][0]
    iSize = iLast - iFirst + 1
    
    if iSize < 2:
      tkMessageBox.showerror("Error", "Not enough assignment available.")      
      return 0
      
    # initialize two dimensional array
    self.obs_mat = [[0 for x in range(10)] for x in range(iSize)]     # [seq][atom], 0: seq, 1: index, 2....
    self.coil_mat = [[0 for x in range(10)] for x in range(iSize)]    # [seq][atom], 0: seq, 1: index, 2.... 
    self.diff_mat = [[0 for x in range(10)] for x in range(iSize)]    # [seq][atom], 0: seq, 1: index, 2.... 
            
    # fill matrix
    # ("dH", "dN", "dC", "dCA", "dCB", "dHA/HA2", "dHB/HB2", "0")
    # coil first
                  #pacsy_ss_layout = {
                  #  "A_N": {
                  #    "SS_H":( 121.81,   3.61,   9573,   8.69, 261.31), #avg,std,n,skew,kurt
                  #    "SS_E":( 124.88,   4.19,   3285,  -0.29,   0.79), #avg,std,n,skew,kurt
                  #    "SS_T":( 123.74,   4.22,   4524,  -5.53, 162.49), #avg,std,n,skew,kurt
                  #    "SS_C":( 124.61,   4.94,   3339,  -8.89, 255.36), #avg,std,n,skew,kurt

    for i in range(iSize):
      seqidx = seqgroup_list[i][0]
      seq = seqgroup_list[i][1]
      
      self.coil_mat[i][0] = seq
      self.coil_mat[i][1] = seqidx
      self.obs_mat[i][0] = seq
      self.obs_mat[i][1] = seqidx
      self.diff_mat[i][0] = seq
      self.diff_mat[i][1] = seqidx            
      
      skey = 'SS_C'
      for atom in self.observable_list2:
        atomidx = self.observable_list2.index(atom)
        akey = '%s_%s' % (seq, atom)
        if atom == 'HA':  akey2 = '%s_HA2'
        elif atom == 'HB':  akey2 = '%s_HB2'
        else: akey2 = '----'
                  
        if pacsylayout.pacsy_ss_layout.has_key(akey):
          pacsy_key = pacsylayout.pacsy_ss_layout[akey]
        elif pacsylayout.pacsy_ss_layout.has_key(akey2):
          pacsy_key = pacsylayout.pacsy_ss_layout[akey2] 
        else: continue

        self.coil_mat[i][2+atomidx] = pacsy_key[skey][0]
        
    # observed
    # Seq ID, Seq ID, Seq, Atom, Atom type, Isotop, CS, CS_Dev, 2
    for group in resonancegroup_list:
      [groupnumber, aaa, atomname, atomtype, isotope, cs, dev] = group
      iPriority = 1
      if atomname[0] == 'Q' or atomname[0] == 'M': atomname = 'H' + atomname[1:] # pseudoatom
      try:
        atomidx = self.observable_list2.index(atomname)
      except:
        if atomname == 'HA2': atomidx = 5
        elif atomname == 'HB2': atomidx = 6
        iPriority = 0
        continue
          
      if (self.obs_mat[groupnumber-iFirst][atomidx+2] == 0) or (iPriority == 1):
        self.obs_mat[groupnumber-iFirst][atomidx+2] = cs
    
    # fill diff mat
    for i in range(len(self.diff_mat)):
      for j in range(len(self.diff_mat[0])):
        if j < 2: continue      
        if self.obs_mat[i][j] == 0: continue
        self.diff_mat[i][j] = self.obs_mat[i][j] - self.coil_mat[i][j]
      
    obs1 = self.obs1.get()
    obs2 = self.obs2.get()     
    
    obs1_idx = self.observable_list.index(obs1)+2  
    obs2_idx = self.observable_list.index(obs2)+2
         
    # genearte ndpplot.csv and ndpplot.ini
    # GROUP, SEQ, IDX, dCS1, dCS2, ddCS
    # fill scrolling list
    f = open(self.csv_path, 'w')
    g = open(self.ini_path, 'w')    
    f.write('GROUP,SEQ,IDX,%s,%s,ddCS\n' % (obs1, obs2))
    self.listbox.append('GROUP,SEQ,IDX,%s,%s,ddCS' % (obs1, obs2))
    g.write('[GENERAL_START]\n')
    g.write('TITLE=Secondary Chemical Shift Analysis\n')
    g.write('XLABEL=Sequence Index\n')
    g.write('YLABEL=ddCS[%s-%s]\n' % (obs1, obs2))
    g.write('XMIN=%d\n' % (iFirst))
    g.write('XMAX=%d\n' % (iLast))
    if obs1[1] != 'H':
      g.write('YMIN=-10\n')
      g.write('YMAX=10\n')
    else:    
      g.write('YMIN=-1\n')
      g.write('YMAX=1\n')    
    g.write('XSCALE=INT\n')  
    g.write('[GENERAL_END]\n')
    g.write('[SERIES1_START]\n')    
    g.write('NAME=Secondary Shift\n')
    g.write('PLOTTYPE=BAR\n')    
    g.write('COLORCOUNT=20\n')
    g.write('DATACOUNT=%d\n' % len(self.diff_mat))
    
    if obs1[1] != 'H':
      g.write('COLOR_1=1,10000,-1000,-9,0_0_255\n')   # Sheet ?
      g.write('COLOR_2=1,10000,-9,-8,25_25_255\n')
      g.write('COLOR_3=1,10000,-8,-7,50_50_255\n')
      g.write('COLOR_4=1,10000,-7,-6,75_75_255\n')
      g.write('COLOR_5=1,10000,-6,-5,100_100_255\n')
      g.write('COLOR_6=1,10000,-5,-4,125_125_255\n')
      g.write('COLOR_7=1,10000,-4,-3,150_150_255\n')
      g.write('COLOR_8=1,10000,-3,-2,175_175_255\n')
      g.write('COLOR_9=1,10000,-2,-1,200_200_255\n')
      g.write('COLOR_10=1,10000,-1,0,225_225_255\n')
      g.write('COLOR_11=1,10000,0,1,225_255_225\n')   # Helix ?
      g.write('COLOR_12=1,10000,1,2,200_255_200\n')
      g.write('COLOR_13=1,10000,2,3,175_255_175\n')
      g.write('COLOR_14=1,10000,3,4,150_255_150\n')
      g.write('COLOR_15=1,10000,4,5,125_255_125\n')
      g.write('COLOR_16=1,10000,5,6,100_255_100\n')
      g.write('COLOR_17=1,10000,6,7,75_255_75\n')
      g.write('COLOR_18=1,10000,7,8,50_255_50\n')
      g.write('COLOR_19=1,10000,8,9,25_255_25\n')      
      g.write('COLOR_20=1,10000,9,1000,0_255_0\n')
    else:      
      g.write('COLOR_1=1,10000,-1000,-0.9,0_0_255\n')   # Sheet ?
      g.write('COLOR_2=1,10000,-0.9,-0.8,25_25_255\n')
      g.write('COLOR_3=1,10000,-0.8,-0.7,50_50_255\n')
      g.write('COLOR_4=1,10000,-0.7,-0.6,75_75_255\n')
      g.write('COLOR_5=1,10000,-0.6,-0.5,100_100_255\n')
      g.write('COLOR_6=1,10000,-0.5,-0.4,125_125_255\n')
      g.write('COLOR_7=1,10000,-0.4,-0.3,150_150_255\n')
      g.write('COLOR_8=1,10000,-0.3,-0.2,175_175_255\n')
      g.write('COLOR_9=1,10000,-0.2,-0.1,200_200_255\n')
      g.write('COLOR_10=1,10000,-0.1,0,225_225_255\n')
      g.write('COLOR_11=1,10000,0,0.1,225_255_225\n')   # Helix ?
      g.write('COLOR_12=1,10000,0.1,0.2,200_255_200\n')
      g.write('COLOR_13=1,10000,0.2,0.3,175_255_175\n')
      g.write('COLOR_14=1,10000,0.3,0.4,150_255_150\n')
      g.write('COLOR_15=1,10000,0.4,0.5,125_255_125\n')
      g.write('COLOR_16=1,10000,0.5,0.6,100_255_100\n')
      g.write('COLOR_17=1,10000,0.6,0.7,75_255_75\n')
      g.write('COLOR_18=1,10000,0.7,0.8,50_255_50\n')
      g.write('COLOR_19=1,10000,0.8,0.9,25_255_25\n')      
      g.write('COLOR_20=1,10000,0.9,1000,0_255_0\n')
              
    for i in range(len(self.diff_mat)):
      dCS1 = self.diff_mat[i][obs1_idx]
      dCS2 = self.diff_mat[i][obs2_idx]
      ddCS = dCS1-dCS2
      szLine = '%s%d,%s,%d,%.3f,%.3f,%.3f' % (self.diff_mat[i][0],self.diff_mat[i][1],self.diff_mat[i][0],self.diff_mat[i][1],dCS1,dCS2,ddCS)
      f.write(szLine+'\n')
      self.listbox.append(szLine)
      
      g.write('DATA_%d=%d,%f,0,%s%d\n' % (i+1,i+iFirst,ddCS,self.diff_mat[i][0],self.diff_mat[i][1]))
    g.write('[SERIES1_END]\n')
    
    # middle line  
    g.write('[SERIES2_START]\n')
    g.write('NAME=Middle\n')
    g.write('PLOTTYPE=LINE\n')
    g.write('COLORCOUNT=1\n')
    g.write('DATACOUNT=2\n')  
    g.write('COLOR_1=%d,%d,%f,%f,SILVER\n' % (iFirst, iLast, -1000,1000))
    g.write('DATA_1=%d,0\n' % (iFirst))
    g.write('DATA_2=%d,0\n' % (iLast))  
    g.write('[SERIES2_END]\n')      
      
    f.close()  
    g.close()
    
    pass
  # -----------------------------------------------------------------------------
  #     
  def plot_cb(self):
    if self.analyze_cb() == 0: 
      tkMessageBox.showerror("Error", "Data analysis failed.")
      return
    import nmrfam
    nmrfam.run_npdplot(self.session)  
    pass
  # -----------------------------------------------------------------------------
  #     
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
    pass    
    
# -----------------------------------------------------------------------------
#
def show_scshift(session):
  sputil.the_dialog(scshift_dialog,session).show_window(1)
