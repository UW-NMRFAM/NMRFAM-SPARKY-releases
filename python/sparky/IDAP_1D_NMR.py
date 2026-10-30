license="""
IDAP Copyright, License, and Disclaimer
Copyright (c) 2019, Evgenii Kovrigin (ekovrigu@nd.edu)

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

# ---------- IDAP 1D NMR  -----------------------------------------
# (C) Evgenii Kovrigin
# 09/25/09-3/20/2019
#
# Bugs and fixes
# 2/26/09 - lists of points are sorted 
# 9/25/09 - output of noise rmsd scaled accordingly to a number of integrated traces added (as Y error column)
# 10/1/09 - accurate output of values from the grid is added
# 03/20/2019 - adapted for inclusion with NMRFAM Sparky suite



version='1.2.3'
program_name='IDAP 1D NMR  ver. %s' % version
# Additional info
bugs_and_fixes="""
"""
# Help document
doc="""
Extract a series of one-dimensional slices from multiple 2D spectra for analysis of NMR line shapes
-----------------------------
Quick reference (for more details see
http://lineshapekin.net/Global_Analysis/IDAP/docs/NMRLineShapes1D/IDAP_1D_NMR_Sparky_extension.htm)

[Assign indices] - enter numerical values for every spectrum to use as a serial index for 1D slices in fitting

[Set current peak] - select a peak and click this button to begin building a set of 1D slices

Now you can drag a box to define a region to integrate. Try to take as narrow region as possible so to have maximum S/N

Integrate the box to leave the long dimension as 1D spectral axis:

[Remove w2] - sum all points along w2

[Remove w1] - same for w1

[Save dataset name] - save the name of the current dataset (=selected peak label) into  'matlab_peaklist.txt'



(C) Evgenii Kovrigin,    3/30/2008-03/20/2019
Based on original regionrmsd and relax extensions.
""" 


import sputil
import tkutil
import tkMessageBox, tkFileDialog
import display_heights_vs_index

#import curvefit
#import xmgr, 
import os
from math import *
# -----------------------------------------------------------------------------
#
#--- this is a parameter used for naming the files. Use 'es' to set it ====
INDEX_PARAMETER='relaxation_time_parameter'

dims={ 'w1':0,  # numerical order of dimensions in arrays
       'w2':1
     }


class region_rmsd_dialog(tkutil.Dialog):
  # storage for mean RMSD value
  _current_spectrum=None
  _mean_rmsd=0
  _number_of_runs=0
  def __init__(self, session):

    

    self.session = session
    self.drag_notice = None

    #--- Matlab data handling
    self.current_peak_name=''
    self.current_peak_name_saved=''
    self.matlab_path='None'

    #-- remember last spectrum where you dragged last rectangle
    self.last_spectrum=None

    #--- remember the resonance to associate all extracted datasets with
    self.current_resonance='>>> Hit  [Set current peak]'

    self.my_region=None
    
    tkutil.Dialog.__init__(self, session.tk, '%s' % program_name)

    self.top.columnconfigure(0, weight = 1)

    import Tkinter

    #--- 1st row label

    r = Tkinter.Label(self.top, text='  Drag around a peak to select a peak label  ',justify = 'left')
    r.grid(row = 0, column = 0, sticky = 'nw')
    self.result_label = r

    #-- second row buttons
    br = tkutil.button_row(self.top,
                           ('Assign indices', self.run_es),
                           ('Set current peak', self.set_current_resonance),
    			   )
    br.frame.grid(row = 1, column = 0, sticky = 'nw')

    #--- third row separator
    explain = ('-----------------------------------------------')
    w = Tkinter.Label(self.top, text = explain, justify = 'left')
    w.grid(row = 2, column = 0, sticky = 'nw')

    explain = ('  Drag a box to define the region to integrate  ')
    w = Tkinter.Label(self.top, text = explain, justify = 'left')
    w.grid(row = 3, column = 0, sticky = 'nw')

    #--- third row separator
    explain = ('-----------------------------------------------')
    w = Tkinter.Label(self.top, text = explain, justify = 'left')
    w.grid(row = 4, column = 0, sticky = 'nw')
    
    #--- fourth row text
    explain = ('  Integrate SAME region in all spectra at once  ')
    w = Tkinter.Label(self.top, text = explain, justify = 'left')
    w.grid(row = 5, column = 0, sticky = 'nw')

    #--- 5th row labels
    br = tkutil.button_row(self.top,
                           ('Remove w2', self.region_w2),
                           ('Remove w1', self.region_w1),                           
 			   )
    br.frame.grid(row = 6, column = 0, sticky = 'nw')


    #--- 6th row separator
    explain = ('-----------------------------------------------')
    w = Tkinter.Label(self.top, text = explain, justify = 'left')
    w.grid(row = 7, column = 0, sticky = 'nw')
    
    #--- 7th row text
    explain = ('  Integrate region in ONE spectrum at time  ')
    w = Tkinter.Label(self.top, text = explain, justify = 'left')
    w.grid(row = 8, column = 0, sticky = 'nw')

    #--- 8th row labels
    br = tkutil.button_row(self.top,
                           ('Remove w2', self.region_w2_single_spectrum),
                           ('Remove w1', self.region_w1_single_spectrum),                           
 			   )
    br.frame.grid(row = 9, column = 0, sticky = 'nw')

    #--- 9th row separator
    explain = ('-----------------------------------------------')
    w = Tkinter.Label(self.top, text = explain, justify = 'left')
    w.grid(row = 10, column = 0, sticky = 'nw')
    #-- 10th row buttons
    br = tkutil.button_row(self.top,
                            ('Save dataset name', self.append_resname),                           
                            ('Close', self.close_cb),
                            ('Help', self.help),
			   )
    br.frame.grid(row = 11, column = 0, sticky = 'nw')


    self.register_callback(1)
    self.top.bind('<Map>', lambda e, s=self: s.register_callback(1))
    self.top.bind('<Unmap>', lambda e, s=self: s.register_callback(0))



  # ---------------------------------------------------------------------------
  def help(self):
    tkMessageBox.showinfo(program_name,message=doc)
  # ---------------------------------------------------------------------------
  def run_es(self):
    display_heights_vs_index.run(self.session)
    #self.session.command_characters('es')
  # ---------------------------------------------------------------------------
  #
  def register_callback(self, register):

    if register:
      if self.drag_notice == None:
        self.drag_notice = self.session.notify_me('drag region',
                                                  self.region_selected_cb)
    else:
      if self.drag_notice:
        self.session.dont_notify_me(self.drag_notice)
        self.drag_notice = None

  # ---------------------------------------------------------------------------
  #
  def region_selected_cb(self, region):

    if self.is_window_destroyed():
      self.register_callback(0)
      return

    #--ek
    self.my_region=region

    s = self.session.selected_spectrum()

    #--- remember the spectrum where I defined last region
    self.last_spectrum=s
    print 'Region defined in %s' % s.name


    if s == None:
      self.result_label['text'] = 'No spectrum selected'
      return
    #print region
    rmin, rmax = region
    ranges = map(lambda vmin, vmax: '%.4g-%.4g' % (vmin, vmax), rmin, rmax)
    import string
    rtext = '[ ' + string.join(ranges, ', ') + ' ]'

    self.current_peak_name=''
    self.current_peak_name_saved=''

    self.showinfo(rtext)
        

  def showinfo(self,text):
    'to refresh info window'
    #-----------------------------------------------------------------------
    msg = ('Current peak    %s\n' % self.current_resonance +
            'Current index: %s\n' % self.last_spectrum.saved_value(INDEX_PARAMETER) +
           'Current region      %s\n' % text +
           'Saved as: %s\n%s' %(self.current_peak_name, self.current_peak_name_saved))
    self.result_label['text'] = msg

  # ---------------------------------------------------------------------------

  def set_current_resonance(self):
      'choose a resonance to associate data sets with'
      selected_peaks=self.session.selected_peaks()
      if len(selected_peaks)==1:
                self.current_resonance=selected_peaks[0].assignment
      self.showinfo('')
    
      

  # ---------- integrate SAME region in ALL  spectra -----------------------------------------------------------------
  #
  def region_w1(self):
    'integrate dimension w1'
#    print self.integrate_region(self.session.selected_spectrum(),self.my_region, 'w2')
    all_spectra=self.session.project.spectrum_list()
    self.integrate_all_spectra(all_spectra, self.my_region, 'w2')
    
  def region_w2(self):
    'integrate dimension w2'
    #print self.integrate_region(self.session.selected_spectrum(),self.my_region, 'w1')
    all_spectra=self.session.project.spectrum_list()
    self.integrate_all_spectra(all_spectra, self.my_region, 'w1')

  # -------- integrate the region in ONE SPECTRUM ---------------------------------------------------------------------
  #
  def region_w2_single_spectrum(self):
    'integrate dimension w2 in ONE spectrum'    
    self.integrate_all_spectra([self.last_spectrum], self.my_region, 'w1')

  def region_w1_single_spectrum(self):
    'integrate dimension w1 in ONE spectrum'    
    self.integrate_all_spectra([self.last_spectrum], self.my_region, 'w2')




  # ------------ DO INTEGRATION OF THE REGION -----------------------------------------------------------------
  def integrate_all_spectra(self, selected_spectra, region, X_axis):

 

    path=os.path.dirname(self.session.project.save_path)
    matlab_datapath=os.path.join(path,"Data_for_IDAP") #-- goes into a current directory
    if not os.path.isdir(matlab_datapath):   os.mkdir(matlab_datapath)


    #--- make a name of folder to hold data for specific residue ---
    peaks=self.current_resonance
    peaks+="_x_"+X_axis
    peaks_path=os.path.join(matlab_datapath,peaks)
    if not os.path.isdir(peaks_path):   os.mkdir(peaks_path)


    #--- paths for MatLab data ---
    matlab_fullpath=matlab_datapath
    #--- current peak filename
    matlab_fname=peaks
    matlab_peaklist='matlab_peaklist.txt'



    
    #-- name for a file with a list of spectra
    points_fname=os.path.join(peaks_path,'points_list.txt')

    #--- Check if all spectra were integrated/exported first
    if len(selected_spectra)==1:
        if not os.path.isfile(points_fname):
              tkMessageBox.showerror("LineShapeKin","You should do integration of all spectra with the SAME region first and then do individual extraction of desired points!\n")
        
    points_file=open(points_fname,'w')
    # need to save points sorted while the spectral list is not ordered by values
    point_indices=[]
    #-- collect all indices 
    for spectrum in self.session.project.spectrum_list():
      new_index=int(spectrum.saved_value(INDEX_PARAMETER))
      if new_index in point_indices:
              tkMessageBox.showerror("LineShapeKin","Duplicate indices found: '%s' !!!\n" % new_index)
      #-- collect new index  
      point_indices.append(new_index)
      
    #-- save names of the spectra in the project in ascending order
    Npoints=len(point_indices)
    for counter in range(Npoints):
      point=min(point_indices)
      #-- save it
      points_file.write("%s\n" % point)
      #-- remove it
      point_indices.remove(point)

    points_file.close()


 
   
    #--- run integration
    y_maxs=[]
    y_mins=[]
    datastrings=[] #-- for matlab output
    

    for spectrum in selected_spectra:

      print 'Export data from: %s' % spectrum.name

      print region

 
      # Integrate region   
      integrated, min_X, max_X, min_Y, max_Y, error_flag = self.integrate_region(spectrum,region, X_axis)
      # don't proceed if there were errors.
      if error_flag==1:
          return
        
      y_maxs.append(max_Y)
      y_mins.append(min_Y)
      
      #--- plain output ----
      if spectrum.saved_value(INDEX_PARAMETER):
          fname=spectrum.saved_value(INDEX_PARAMETER)+'.txt'
      else:
          fname=spectrum.name+".no_index_assigned"
      file=open(os.path.join(peaks_path,fname),'w')


      #-- collect and write out the spectral data as X, Y and Yrmsd
      for line in integrated:
         file.write("%f\t%f\t%f\n" % (spectrum.hz_per_ppm[dims[X_axis]]*float(line[0]), line[1], line[2]))
      file.close()
      

      #-- make sure spectrum has a point number assigned
      if spectrum.saved_value(INDEX_PARAMETER):
          index=spectrum.saved_value(INDEX_PARAMETER)
      else:
          tkMessageBox.showerror('Integrate Regions',
                                 'Need INDEX value set in each spectrum!  "%s" does not have it! '%spectrum.name)
          return
     
    

      
         


    #--- save name of exported residue to use in Matlab notebooks ---
    self.current_peak_name=matlab_fname
    self.current_peak_name_saved=''
    self.matlab_path=os.path.join(matlab_fullpath,matlab_peaklist)

    self.showinfo('')



  #------ INTEGRATE
  def integrate_region(self,spectrum, region, X_axis='w1'):
    """ This procedure performs extraction of spectral data from the raw data matrix.
    The key problem is that all data is only defined for specific grid 
    points but we don't have means to directly access grid coordinates. 
    Therefore we need to recalculate grid coordinates and for the desired 
    region around the peak select closest grid points. The data is further integrated
    along the requested dimension.
    """

    # flag for the caller function to know about problems
    error_flag=0;
    
    if spectrum.dimension!=2:
        tkMessageBox.showwarning("Integrate Region","Cannot work with %d dimensions!" % spectrum.dimension)
    
    ppm_per_index = map(lambda w,s: float(w)/s,
                        spectrum.spectrum_width, spectrum.data_size)

    #--- assign dimensions
    primary_dimension=dims[X_axis]
    secondary_dimension= not primary_dimension


    
    curr_point=[0,0]

    #--- go along main dimension, integrate secondary
    
    integrated=[]

    
    
    
    
    #============ DETERMINE REGION IN TERMS OF THE DATA GRID POINTS =============
    

    # Extract proton dimension as X, nitrogen as Y"
    Xdim=primary_dimension
    Ydim=secondary_dimension
    
    
    #-- determine frequency difference between the grid points
    dw_grid = map(lambda w,s: float(w)/s,
                        spectrum.spectrum_width, spectrum.data_size)

    #-- find index corresponding to the lower boundary of the region around the peak
    ind_min=[0,0]
    ind_min[Xdim]=(region[0][Xdim] - spectrum.region[0][Xdim])/dw_grid[Xdim] +1
    ind_min[Ydim]=(region[0][Ydim]  - spectrum.region[0][Ydim])/dw_grid[Ydim] +1
    

    #--- calculate closest grid point (integer)
    i_grid_min=[0,0]
    i_grid_min[Xdim]=int(round(ind_min[Xdim]))
    i_grid_min[Ydim]=int(round(ind_min[Ydim]))
    
    #---- calculate frequency of the grid point closest to the lower boundary
 
    min_X = spectrum.region[0][Xdim] + dw_grid[Xdim]*(i_grid_min[Xdim] - 1)
    min_Y = spectrum.region[0][Ydim] + dw_grid[Ydim]*(i_grid_min[Ydim] - 1)



    #---- calculate index corresponding the upper boundary of the reqion around the peak
    ind_max=[0,0]
    ind_max[Xdim]=(region[1][Xdim] - spectrum.region[0][Xdim])/dw_grid[Xdim] +1
    ind_max[Ydim]=(region[1][Ydim] - spectrum.region[0][Ydim])/dw_grid[Ydim] +1
    # make sure lower boundary does not go outside of the spectrum
    if ind_max[Xdim]>spectrum.data_size[Xdim]: ind_max[Xdim]=spectrum.data_size[Xdim]
    if ind_max[Ydim]>spectrum.data_size[Ydim]: ind_max[Xdim]=spectrum.data_size[Ydim]
     
    #--- calculate closest grid point (integer)
    i_grid_max=[0,0]
    i_grid_max[Xdim]=int(round(ind_max[Xdim]))
    i_grid_max[Ydim]=int(round(ind_max[Ydim]))

    
    #---- calculate frequency of the grid point closest to the lower boundary
 
    max_X = spectrum.region[0][Xdim] + dw_grid[Xdim]*(i_grid_max[Xdim] - 1)
    max_Y = spectrum.region[0][Ydim] + dw_grid[Ydim]*(i_grid_max[Ydim] - 1)





    #======= EXTRACT REGION ===================================================
    
    X_steps=int((max_X  - min_X)  / ppm_per_index[primary_dimension])
    # plus 1 (below) because we always take the initial grid point plus any extra
    Y_steps=int((max_Y  - min_Y)/ ppm_per_index[secondary_dimension]) + 1
       
    # report
    tkMessageBox.showinfo(program_name, 'Spectrum: %s\n%d traces integrated.\n' % (spectrum.name, Y_steps))
    
    # calculate noise RMSD for the integrated trace out of N traces
    # as sqrt(N)
    Ystderr=spectrum.noise*sqrt(Y_steps);

    # just for xmgr scaling
    max_y=spectrum.data_height(curr_point)/Y_steps 
    min_y=max_y

    for i in range(X_steps):
      
      curr_X=min_X + ppm_per_index[primary_dimension]*i
      curr_point[primary_dimension]=curr_X
      
      sum=0

      for j in range(0,Y_steps):

          curr_Y=min_Y + ppm_per_index[secondary_dimension]*j
          curr_point[secondary_dimension]=curr_Y
                     
          height=spectrum.data_height(curr_point)
                     
          sum+=height

      Y_point= sum
      integrated.append([curr_X,Y_point, Ystderr])
                     
      if Y_point>max_y: max_y=Y_point
      if Y_point<min_y: min_y=Y_point

    #--- ranges for plotting ---
    min_x=min_X
    max_x=min_x + ppm_per_index[primary_dimension] * (X_steps-1)
    
    
    return integrated, min_x, max_x, min_y, max_y, error_flag



#---- APPEND RESIDUE NAME TO A PEAK LIST -----
  def append_resname(self):
    'appends the name to matlab peaklist'
    if not self.current_peak_name:
        return
    #--- save name of exported residue to use in Matlab notebooks ---
    file=open(self.matlab_path,'a')
    file.write("%s\n" % self.current_peak_name)
    file.close()
    self.current_peak_name_saved='Appended to MatLab peaklist'
    self.showinfo('')
#---------------------------------------------------------------------------------------

#-------------------------------------------------------------
  def fit_integrated(self,integrated_region, fit_func):
    'fit region to two peaks'
    pass
    
  
#

def run(session):

  sputil.the_dialog(region_rmsd_dialog,session).show_window(1)
