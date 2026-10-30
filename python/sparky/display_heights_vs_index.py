license="""
IDAP Copyright, License, and Disclaimer
Copyright (c) 2019, Evgenii Kovrigin (ekovrigu@nd.edu)

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""


doc="""Display_interleaved_points
=================
This extension is based on Tom's 'relax.py'.
modified by Evgenii Kovrigin, 02/25/05 to allow simple analysis
of series of spectra.

Specific features:

- uses 'Index' to allow entry of either relaxation times or interleave indices

- Displays noise value entered in the setup dialog on the plot as red and blue bars (+value, -value) give you an idea of significance of the points scatter

- Saves data in simple format with heading containing index values

- Data heights measured by 3x3 grid so - dependent on Zero-Filling!

"""
#-------------------------------------------------------------------------

developer_info="""========  INFORMATION FOR A DEVELOPER ==================
This code contains many unused functions inherited from relax_dialog and
data fitting routines. One can get rid of them.

3/21/19 - dependency on curvefit3.py and residue.py was removed
"""
  


import string
import copy
import math, os
import re
import string
import Tkinter
import tkFileDialog
import tkMessageBox
import pyutil
import sparky
import sputil
import tkutil


# -----------------------------------------------------------------------------
#
class relaxation_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session, title='Fitting of peak intensities decay'):

    self.session = session
    self.spectrum_times = []
    self.last_spectrum_times = []
    self.error_estimate_trials = 50
    self.relative_scale_on_plots= session.selected_spectrum().noise*3

    
    #-- for looking through the fits using arrow keys ---
    self.current_fit_index=-1 # no fit chosen 
    self.my_fit_list=[]
    
    tkutil.Dialog.__init__(self, session.tk, title)

    pl = tkutil.scrolling_list(self.top, heading = '', height = 5)
    pl.frame.pack(side = 'top', fill = 'both', expand = 1)
    pl.listbox.bind('<ButtonRelease-1>', self.show_fit_cb)
    pl.listbox.bind('<KeyPress-Delete>', pl.delete_selected_cb)
    # The following is needed so key press is received by list box.
    pl.listbox.bind('<ButtonPress-1>', pl.set_focus_cb)
    self.peak_list = pl

    pp = tkutil.checkbutton(self.top,
        'Measure heights in all spectra at the ppm position of peaks in the active window', 0)
    self.single_peak_position = pp.variable
    pp.button.pack(side = 'top', anchor = 'w')

    progress_label = Tkinter.Label(self.top, anchor = 'nw')
    progress_label.pack(side = 'top', anchor = 'w')

    br = tkutil.button_row(self.top,
                           ('Setup...', self.setup_cb),
                           ('Save', self.peak_list.save_cb),        # res-R-err heights file
                           ('Append', self.peak_list.append_cb),
                           ('Stop', self.stop_cb), 
                           ('Clear', self.clear_cb),
                           
			   ('Close', self.close_cb),
                           ('Help', self.my_help),
                           ('Show next plot', self.show_next_fit),
			   ('Show prev plot', self.show_previous_fit),
                           )
    br.frame.pack(side = 'top', anchor = 'w')

    tkutil.Stoppable.__init__(self, progress_label, br.buttons[3])

  # ---------------------------------------------------------------------------
  #
  def my_help(self):
    tkMessageBox.showinfo("Help",message=doc)
#    self.session.command_characters('py')
    print doc
  # ---------------------------------------------------------------------------
  #
  
  def show_next_fit(self):

    if self.current_fit_index==-1: return # not initialized yet
    
    if not self.current_fit_index<(len(self.my_fit_list)-1): return # end reached

    self.current_fit_index+=1
    fit=self.my_fit_list[self.current_fit_index]
    curvefit.show_fit(self.session, fit.name, fit, self.relative_scale_on_plots,  self.show_peak_cb)
  
  # ---------------------------------------------------------------------------
  #
  def show_previous_fit(self):

    if self.current_fit_index==-1: return  # no fit chosen yet

    
    if not self.current_fit_index>0: return # start reached

    self.current_fit_index-=1
    fit=self.my_fit_list[self.current_fit_index]
    curvefit.show_fit(self.session, fit.name, fit, self.relative_scale_on_plots,  self.show_peak_cb)
      
    


  # ---------------------------------------------------------------------------
  #


  def setup_cb(self):

    setup_dialog = sputil.the_dialog(relax_setup_dialog, self.session)
    settings = {'spectrum-times': self.spectrum_times,
                
                'relative-scale':self.relative_scale_on_plots}
    setup_dialog.set_parent_dialog(self, settings, self.set_params)
    setup_dialog.show_window(1)

  # ---------------------------------------------------------------------------
  #
  def set_params(self, settings):

    self.spectrum_times = settings['spectrum-times']
    self.relative_scale_on_plots=settings['relative-scale']


  # ---------------------------------------------------------------------------
  #
  def clear_cb(self):

    self.peak_list.clear() # clear long list
    
  # ---------------------------------------------------------------------------
  #
  def show_fit_cb(self, event):

    fit = self.peak_list.event_line_data(event)
    if fit:
      curvefit.show_fit(self.session, fit.name, fit, self.relative_scale_on_plots, self.show_peak_cb)
      self.current_fit_index=self.my_fit_list.index(fit)

  # ---------------------------------------------------------------------------
  #
  def show_peak_cb(self, fit, n):

    sputil.show_spectrum_position(fit.spectrum_times[n][0], fit.peak_position)
    
  # ---------------------------------------------------------------------------
  #
  def show_peak_heights(self):
    if not self.top.winfo_ismapped():
      self.show_window(1)
    if self.spectrum_times:
      if self.spectrum_times != self.last_spectrum_times:
        self.last_spectrum_times = self.spectrum_times
        self.show_heading(self.spectrum_times)
      self.stoppable_call(self.show_peaks,
                          self.session.selected_peaks(),
                          self.spectrum_times)
  # ---------------------------------------------------------------------------
  #
  def show_peaks(self, peaks, spectrum_times):

    single_position = self.single_peak_position.get()
    self.stoppable_loop(' peaks', 1)
    for p in self.session.selected_peaks():
      self.check_for_stop()
      if single_position or not p.is_assigned:
	assignment = None
      else:
	assignment = p.assignment
      th_pairs = self.time_height_pairs(p.position, assignment, spectrum_times)
      fit = self.fit_function(th_pairs, assignment)
      fit.name = p.assignment
      fit.peak_position = p.position
      fit.spectrum_times = spectrum_times
      line = self.peak_line(p, fit)
      self.peak_list.append(line, fit)
      self.peak_list.listbox.see('end')
      #-- append short list for saving and for viewing
      self.my_fit_list.append(fit)
      
  # ---------------------------------------------------------------------------
  #
  #
  def time_height_pairs(self, pos, assignment, spectrum_times):

    th_pairs = []

    for s, t in spectrum_times:
      if assignment:
	# Use position of peak with matching assignment if available
	peak = s.find_peak(assignment)
      else:
	peak = None
      if peak:
	h = self.average_height(s, peak.position)
      else:
	h = self.average_height(s, pos)
      th_pairs.append([t, h])
    return th_pairs
# -------------------------------------------------------------------------  
#
  def average_height(self, spectrum, pos):
   
    xstep = spectrum.spectrum_width[0] / spectrum.data_size[0]
    ystep = spectrum.spectrum_width[1] / spectrum.data_size[1]

    #-- 3x3 grid averaging
##    sum = 0
##    for i in (-1, 0, 1):
##      for j in (-1, 0, 1):
##        p = (pos[0] +i * xstep, pos[1] + j * ystep)
##	sum = sum + spectrum.data_height(p)
##    h = sum / 9.0

    #-- alternative measure: height at one point  
    h = spectrum.data_height(pos)

    return h 

  # ---------------------------------------------------------------------------
  #
  def fit_function(self, th_pairs, assignment):
    
    

    h_values = map(lambda th: th[1], th_pairs)
    h_middle = .5 * (max(h_values) + min(h_values))

    
    params = (h_middle,0)
    trials = self.error_estimate_trials
    epsilon=1e-10

    #-- run my Any_Function object now -----
    func = curvefit3_functions.Exponent_Func2()
    func.set_data(th_pairs)
    func.set_init_params(params)

    #-- try fitting ---   
    try:
      func.fit_data(trials,epsilon)
    except OverflowError:
      self.session.command_characters('py')
      print "\n\nFitting warning!   Assignment %s didn't fit !!!" % assignment
      func.fit.param_sd=[0]*len(func.fit.params)
      return func.fit

    
    #-- try error estimate ---
    try:
      func.set_same_dy(func.fit.point_sd)
      func.fit.estimate_parameter_error(trials)
    except OverflowError:
      self.session.command_characters('py')
      print "\n\nFitting warning!   Error estimate for %s failed !!!" % assignment
      func.fit.param_sd=[0]*len(func.fit.params)

    return func.fit

  # ---------------------------------------------------------------------------
  # The error estimate for T is not the standard deviation over fits with
  # gaussian random y errors added.  I believe such a standard deviation is
  # divergent because the flat fit (T = infinity) case has codimension 1.
  # So instead I take the SD of the rate constant (1/T) and convert this
  # to an equivalent T error.
  #
  def calculate_decay_time(self, fit):

    if fit.converged and fit.params[1] != 0:
      t_decay = -1 / fit.params[1]
      t_sd = abs(t_decay * fit.param_sd[1] /  fit.params[1])
    else:
      t_decay = 0
      t_sd = 0
    
    fit.t_decay = t_decay
    fit.t_sd = t_sd

  # ---------------------------------------------------------------------------
  #
 
class relax_setup_dialog(tkutil.Settings_Dialog):

  def __init__(self, session):

    tkutil.Settings_Dialog.__init__(self, session.tk, 'Spectra series v.1')

    headings = ('Spectrum  ', 'Index')
    st = sputil.spectrum_table(session, self.top, headings,
                               self.add_spectrum, self.remove_spectrum)
    st.frame.pack(side = 'top', anchor = 'w')
    self.spectrum_widgets = {}

    spectra = session.project.spectrum_list()
    def time_param(s, self=self):
      return pyutil.string_to_float(self.default_time_parameter(s), 0)
    spectra = pyutil.sort_by_function_value(spectra, time_param)
    for spectrum in spectra:
      st.add_spectrum(spectrum)



    r = tkutil.entry_field(self.top, 'Relative scale on plots:', '25000', 10, "(3xRMSD is noise peak level)")
    r.frame.pack(side = 'top', anchor = 'w')
    self.relative_scale = r



   
    br = tkutil.button_row(self.top,
                           ('Ok', self.ok_cb),
                           ('Apply', self.apply_cb),                           
                           ('Close', self.close_cb),
			   )
    br.frame.pack(side = 'top', anchor = 'w')

  # ---------------------------------------------------------------------------
  #
  def add_spectrum(self, spectrum, table, row):

    onoff = self.default_onoff(spectrum)

    b = tkutil.checkbutton(table.frame, spectrum.name, onoff)
    b.button.grid(row = row, column = 0, sticky = 'nw')

    ttext = self.default_time_parameter(spectrum)
    e = tkutil.entry_field(table.frame, '', ttext, trailer='')
    e.frame.grid(row = row, column = 1, sticky = 'nw')

    ftext=1

    self.spectrum_widgets[spectrum] = (b, e)

  # ---------------------------------------------------------------------------
  #
  def remove_spectrum(self, spectrum, table):

    b, e = self.spectrum_widgets[spectrum]
    del self.spectrum_widgets[spectrum]
    b.button.destroy()
    e.frame.destroy()
    
  # ---------------------------------------------------------------------------
  #
  def default_onoff(self, spectrum):

    return spectrum.saved_value('relaxation_time_parameter') != None
  
  # ---------------------------------------------------------------------------
  #
  def default_time_parameter(self, spectrum):

    ttext = spectrum.saved_value('relaxation_time_parameter')
    if ttext:
      return ttext
    
    match = re.search('[0-9]+', spectrum.name)
    if match:
      return match.group(0)
    
    return '0'

  # ---------------------------------------------------------------------------
  #
  def show_settings(self, settings):

    stimes = {}
    for s, t in settings['spectrum-times']:
      stimes[s] = (t)
      
    for s, (b, te) in self.spectrum_widgets.items():
      b.variable.set(stimes.has_key(s))
      if stimes.has_key(s) :
	t= stimes[s]
        if pyutil.string_to_float(te.variable.get()) != t:
          te.variable.set('%.5g' % t)
      

    self.relative_scale.variable.set('%d' % settings['relative-scale'])
  # ---------------------------------------------------------------------------
  #
  def get_settings(self):


    
    relative_scale=pyutil.string_to_int(self.relative_scale.variable.get(), 0)
    
    settings = {'spectrum-times': self.spectrum_times(),

                'relative-scale':relative_scale}
    return settings
    
  # ---------------------------------------------------------------------------
  #
  def spectrum_times(self):

    stf = []
    for s, (b, te) in self.spectrum_widgets.items():
      if b.variable.get():
        ttext = te.variable.get()
        t = pyutil.string_to_float(ttext)
        stf.append((s, t))
        s.save_value('relaxation_time_parameter', ttext)
    stf.sort(self.spectrum_time_order)
    return tuple(stf)

  # ---------------------------------------------------------------------------
  #
  def spectrum_time_order(self, st1, st2):

    return cmp(st1[1], st2[1]) or cmp(st1[0].name, st2[0].name)

# -----------------------------------------------------------------------------
#

#=================================================================
#=================================================================

def show_fit(session, heading, fit, relative_scale, callback = None):
  d = sputil.the_dialog(data_display, session)
  d.show_window(1)
  d.plot_fit(heading, fit, relative_scale, callback)

#=================================================================


  def fit_data(self,error_estimate_trials=10, epsilon=1e-6):

      self.fit = no_real_fit(self.data, self, self.init_params, epsilon)
  def parameter_count(self):
    return 1
  
  def value(self, params, x):
    return params

#=================================================================

#======= Code to allow index assignment - no fitting done here!!!
class fit_display(tkutil.Dialog):

  def __init__(self, session):
    
    tkutil.Dialog.__init__(self, session.tk, 'Fit Plot')

    self.top.rowconfigure(1, weight = 1)
    self.top.columnconfigure(0, weight = 1)

    h = Tkinter.Label(self.top)
    h.grid(row = 0, column = 0, sticky = 'w')
    self.heading = h

    c = Tkinter.Canvas(self.top)
    c.grid(row = 1, column = 0, sticky = 'news')
    self.canvas = c
    
    br = tkutil.button_row(self.top,
			   ('Close', self.close_cb),
                           ('Help', sputil.help_cb(session, 'RelaxFit')),
			   )
    br.frame.grid(row = 2, sticky = 'w')

    self.show_window(1)
    
  # ---------------------------------------------------------------------------
  #
  def plot_fit(self, heading, fit,  relative_scale, callback = None):

    mark_height= relative_scale # simple measure of height
    
    self.heading['text'] = heading+ ('   R= %.4f   err= %.4f 1/s'% (-fit.params[1],fit.param_sd[1]))

    x_range, y_range = self.xy_ranges(fit.xy_pairs)

    c = self.canvas
    c.delete('all')
    c.update_idletasks()   # Make sure geometry has been calculated
    w = c.winfo_width()
    h = c.winfo_height()
    r = 5


    #print fit.xy_pairs
    
    if w > 1:
      points = []
      f = fit.fit_function
      for px in range(w):
        
        x = pyutil.map_interval(px, (0,w), x_range)
        y = f.value(fit.params, x)
        py = pyutil.map_interval(y, y_range, (h,0))
        points.append((px,py))
      points = tuple(points)
      apply(c.create_line, points)

    for k in range(len(fit.xy_pairs)):
      x, y, dy = fit.xy_pairs[k]

      px = pyutil.map_interval(x, x_range, (0,w))
      py = pyutil.map_interval(y, y_range, (h,0))
      id = c.create_oval(px-r, py-r, px+r, py+r, fill = 'black')
      

     
      if callback:
        cb = lambda event, fit=fit, k=k, callback=callback: callback(fit, k)
        c.tag_bind(id, '<ButtonPress>', cb)

    yzero=pyutil.map_interval(0, y_range, (h,0))

    #-- prevent the marker going out of range
    if mark_height>y_range[1]:
      ymarkplus=0
    else:
      ymarkplus=pyutil.map_interval(mark_height, y_range, (h,0))

    if mark_height<y_range[0]:
      ymarkminus=h
    else:
      ymarkminus=pyutil.map_interval(-mark_height, y_range, (h,0))

    markplus=c.create_rectangle(0, yzero, 0+2*r, ymarkplus, fill = 'red')
    markminus=c.create_rectangle(0, ymarkminus, 0+2*r, yzero, fill = 'blue')

    c.update_idletasks()
    
  # ---------------------------------------------------------------------------
  #
  def xy_ranges(self, xy_pairs):

    border_padding = .1
    xvalues = tuple(map(lambda xy: xy[0], xy_pairs))
    xrange = self.hard_interval(xvalues, border_padding)
    yvalues = tuple(map(lambda xy: xy[1], xy_pairs))
    yrange = self.hard_interval(yvalues, border_padding)

    return (xrange, yrange)
    
  # ---------------------------------------------------------------------------
##  #
##  def interval(self, values, padding):
##  
##    xmin = apply(min, values)
##    xmax = apply(max, values)
##    if xmax > xmin:
##      border = padding * (xmax - xmin)
##    elif xmin != 0:
##      border = abs(xmin)
##    else:
##      border = 1
##
##    return (xmin - border, xmax + border)
##  
  #
  def hard_interval(self, values, padding):
    'always starts with 0 if the range doesnt cross zero'
  
    xmin = apply(min, values)
    xmax = apply(max, values)
    if xmax > xmin:
      border = padding * (xmax - xmin)
    elif xmin != 0:
      border = abs(xmin)
    else:
      border = 1

    if(xmin>=0 and xmax>0):
      return (0 - border, xmax + border)
    if(xmin<0 and xmax<=0):
      return (xmin - border, 0 + border)
    if(xmin<0 and xmax>0):
      return (xmin - border, xmax + border)


# -----------------------------------------------------------------------------
#
class data_display(fit_display):
  'just to show the array of data'
  # ---------------------------------------------------------------------------
  #
  def plot_fit(self, heading, fit,  relative_scale, callback = None):

    mark_height= relative_scale # simple measure of height
    
    self.heading['text'] = heading

    x_range, y_range = self.xy_ranges(fit.xy_pairs)

    c = self.canvas
    c.delete('all')
    c.update_idletasks()   # Make sure geometry has been calculated
    w = c.winfo_width()
    h = c.winfo_height()
    r = 5
    
  
    for k in range(len(fit.xy_pairs)):
      x, y, dy = fit.xy_pairs[k]

      px = pyutil.map_interval(x, x_range, (0,w))
      py = pyutil.map_interval(y, y_range, (h,0))
      id = c.create_oval(px-r, py-r, px+r, py+r, fill = 'black')
      

     
      if callback:
        cb = lambda event, fit=fit, k=k, callback=callback: callback(fit, k)
        c.tag_bind(id, '<ButtonPress>', cb)

    yzero=pyutil.map_interval(0, y_range, (h,0))

    #-- prevent the marker going out of range
    if mark_height>y_range[1]:
      ymarkplus=0
    else:
      ymarkplus=pyutil.map_interval(mark_height, y_range, (h,0))

    if mark_height<y_range[0]:
      ymarkminus=h
    else:
      ymarkminus=pyutil.map_interval(-mark_height, y_range, (h,0))

    markplus=c.create_rectangle(0, yzero, 0+2*r, ymarkplus, fill = 'red')
    markminus=c.create_rectangle(0, ymarkminus, 0+2*r, yzero, fill = 'blue')

    c.update_idletasks()
    
  # ---------------------------------------------------------------------------
  #


#=================================================================
class least_squares_fit:

  def __init__(self, xy_pairs, fit_function, params, tolerance):

    self.max_steps = 1000
    self.max_cuts = 200
    self.min_fit_error = 1e-6
    
    self.xy_pairs = xy_pairs
    self.fit_function = fit_function
    self.params = params
    self.tolerance = tolerance

    self.fit_error = self.calculate_error(self.params)
    self.error_step = -self.fit_error
    self.step_count = 0
    self.converged = self.find_fit()
    self.point_sd = math.sqrt(self.fit_error / len(xy_pairs))
    
  # ---------------------------------------------------------------------------
  #
  def find_fit(self):

    while (self.fit_error > self.min_fit_error and
           -self.error_step > self.tolerance * self.fit_error and
           self.step_count < self.max_steps and
           self.take_step()):
      self.step_count = self.step_count + 1
      #print self.fit_error

    converged = (self.fit_error <= self.min_fit_error or
                 -self.error_step <= self.tolerance * self.fit_error)
    return converged
    
  # ---------------------------------------------------------------------------
  #
  def take_step(self):

    step = self.linear_step()
#    step = self.newton_step()
    
    if step == None:
      return 0

    cut_count = 0
    while cut_count < self.max_cuts and not self.try_step(step):
      step = pyutil.scale_tuple(step, .5)
      cut_count = cut_count + 1
    if cut_count == self.max_cuts:
      return 0

    return 1

  # ---------------------------------------------------------------------------
  #
  def try_step(self, step):

    new_params = pyutil.add_tuples(self.params, step)
    new_error = self.calculate_error(new_params)
    
    good_step = (new_error < self.fit_error)
    if good_step:
      self.params = new_params
      self.error_step = new_error - self.fit_error
      self.fit_error = new_error

    return good_step


  # ---------------------------------------------------------------------------
  # Find step solving least squares problem with linearized fit function.
  #
  def linear_step(self):

    n = self.fit_function.parameter_count()
    A = zero_matrix(n)
    b = n * [0]
    
    for x, y, dy in self.xy_pairs:
      y_fit = self.fit_function.value(self.params, x)
      g = self.fit_function.parameter_derivatives(self.params, x)
      e = y_fit - y

      for j in range(n):
        Aj = A[j]
        gj = g[j]
        for k in range(n):
          Aj[k] = Aj[k] + gj * g[k]
        b[j] = b[j] - e * gj

    step = solve_positive_system(A, b)

    return step

  # ---------------------------------------------------------------------------
  #
  def calculate_error(self, params):
    'calculates deltaY or deltaY/dy - experimental error'
    esum = 0
    #print self.xy_pairs
    for x, y, dy in self.xy_pairs:
      y_fit = self.fit_function.value(params, x)
      e = y_fit - y
         
      esum = esum + e * e
    return esum
    
  # ---------------------------------------------------------------------------
  # Add Gaussian distributed errors to y values of xy pairs and fit.
  # Do this multiple times and compute standard deviations for the resulting
  # fit parameters.
  #
  def estimate_parameter_error(self, trials):

    trial_params = []
    n = self.fit_function.parameter_count()
    param_sd = n * [0]

    
    if self.converged:

      while len(trial_params) < trials:
        new_xy_pairs = []
        for x, y, dy in self.xy_pairs:
          
          #-- stupid but necessary :(
          if dy=='fake': dy=self.point_sd
          
          new_y = y + random.gauss(0, dy)
          new_xy_pairs.append((x, new_y,dy))

        fit = least_squares_fit(new_xy_pairs, self.fit_function,
                                self.params, self.tolerance)
        if fit.converged:
          trial_params.append(fit.params)


##      for line in trial_params:
##        print string.join(line, '   ')
      
      sum_d2 = n * [0]
      for params in trial_params:
        diff = pyutil.subtract_tuples(params, self.params)
        diff2 = map(lambda d: d*d, diff)
        sum_d2 = pyutil.add_tuples(sum_d2, diff2)
      param_sd = map(lambda d, m=trials: math.sqrt(d/m), sum_d2)

    self.trial_params = trial_params
    self.param_sd = param_sd
  
class no_real_fit(least_squares_fit):
  'just to create the fit object without fitting'
   
  # ---------------------------------------------------------------------------
  def find_fit(self):
     return 1
  # ---------------------------------------------------------------------------
  def calculate_error(self, params):
     return 1
  # ---------------------------------------------------------------------------
  def estimate_parameter_error(self, trials):
     pass
#=================================================================
class Any_Func:
  """
  Parent class for fitting functions (no error weighting!)
  Usage:
  -- make your function ----
  class My_Function(Any_Function):

    def parameter_count(self): return NUMBER_OF_PARAMETERS

    def value(self, params, x):
      'define your function'
      a, b = params
      return a+b*x

  -- use it ---
    a=5
    b=3

    --- setting parameters---    
    ini_params=[a,b]
    
    func = Linear_Func("linear function")
    

    -- data may be (x,y) and then dy is defaulted to 0
    func.set_data(data)
    
    func.set_same_dy(dy=0.7)
    func.set_init_params(ini_params)

    func.fit_data(error_estimate_trials=25,epsilon=1e-6)
    func.results_to_xmgr("test")

  

  """
  def __init__(self, name=""):
    if name=='': self.name=self.__doc__
    else:        self.name=name
    self.have_errors=0
    self.fit=None
  #------------------------------------------------------------------------
  def parameter_count(self):
    raise UserWarning, "\n\nNot implemented in a subclass!!!"
  #------------------------------------------------------------------------  
  def value(self, params, x):
    raise UserWarning, "\n\nNot implemented in a subclass!!!"

  #------------------------------------------------------------------------
  #--- numerical derivatives: redefine it for speed with analytical forms!
  def parameter_derivatives(self, params, x):

    epsilon=1e-6
    derivatives=[]

    
    #--- check for 0 in parameters: numerical derivative wouldn't work!!!
    if 0 in params:
      raise UserWarning, ("\n\n\n!!!!! Warning form function'%s'\nStarting parameters for fitting cannot be zero because numerical\n\
derivative calculation wouldn't work!\nYou should either \n(1) set non-zero values\
for initial parameter estimates or\n\(2) define them analytically (it also makes calculations a lot faster!).\n" % self.__doc__)
    
    for i in range(len(params)):
      #-- step up ---
      temp_params2=list(params)
      temp_params2[i]+=params[i]*epsilon
      #-- step down ---      
      temp_params1=list(params)
      temp_params1[i]-=params[i]*epsilon

      
      dfda=(self.value(temp_params2,x)-self.value(temp_params1,x))/(2*params[i]*epsilon)
      
      derivatives.append(dfda)

  
    return derivatives

  #------------------------------------------------------------------------
  def set_data(self,data):
    'load data'
    #-- here we set errors to 'fake' if they are not supplied 
    self.data=data

    if len(self.data[0])==3:
      self.have_errors=1

    else:
      self.have_errors=0
      if len(self.data[0])==2:
        #--- set errors column --------
        for i in range(len(self.data)):
            self.data[i].append('fake')
      else:
          raise  UserWarning, "Input data for fitting can have 2 or 3 columns, not %d!"% len(self.data[0])
                                                                                             
    
        
  #------------------------------------------------------------------------------
  def set_same_dy(self,dy):
    'set errors to one value'
    N=len(self.data)
    if dy==0:
      raise UserWarning, "\n\n%s: Error dy cannot be 0!" % self.name
    self.have_errors=1
    for i in range(N):
        self.data[i][2]=dy

  #------------------------------------------------------------------------------
  def set_init_params(self,init_params):
    self.init_params=init_params
      

  #------------------------------------------------------------------------
  def fit_data(self,error_estimate_trials=10, epsilon=1e-6):

      self.fit = curvefit3.least_squares_fit(self.data, self, self.init_params, epsilon)
      if self.have_errors:
        self.fit.estimate_parameter_error(error_estimate_trials)
        

  #------------------------------------------------------------------------
  #-- Just wrap-around curvefit3 features ----
      
  def converged(self): return  self.fit.converged
  
  def fitted_params(self): return self.fit.params
  
  def params_sd(self):
    if self.have_errors: return  self.fit.param_sd
    return None
  
  def steps_taken(self): return self.fit.step_count





  #------------------------------------------------------------------------
  def results_to_xmgr(self, fname, graph_title=""):

      

    #---- ideal data -----------
    init_set=[]
    steps=25

    #--- find maximum and minimum
    x_min=0
    x_max=0
    y_min=0
    y_max=0
    for x,y, dy in self.data:
      if x>x_max: x_max=x
      if y>y_max: y_max=y
      if x<x_min: x_min=x
      if y<y_min: y_min=y
      
    x_step=(x_max-x_min)/steps
    x_current=x_min

    for i in range(steps):
        x_current=x_min +i * x_step
        init_set.append([x_current,func.value(ini_params,x_current)])

        
    inifit_dataset=xmgr.Dataset(init_set,"initial approximation")
    inifit_dataset.solid_line()
    inifit_dataset.red_line()
    inifit_dataset.no_sym()


    #--- calculate smooth function ---   
    fitted_set=[]
    for i in range(steps):
        x_current=x_min +i * x_step
        fitted_set.append([x_current,func.value(self.fit.params,x_current)])
        
    fit_dataset=xmgr.Dataset(fitted_set,"final fit")
    fit_dataset.solid_line()
    fit_dataset.no_sym()






    #--- initial dataset ---
    if not self.have_errors :
      #-- remove fake errors
      for i in range(len(self.data)):
        del self.data[i][2]
    int_dataset=xmgr.Dataset(data,"experimental data")



    title=graph_title
    if not title: title="Fitting  "+self.name
    subtitle=""
    if self.have_errors:
      for i in range(len(self.fit.params)):
        subtitle+="%.2g+-%.2g  " % (self.fitted_params()[i], self.params_sd()[i])
    else:
      for i in range(len(self.fit.params)):
        subtitle+="%.2g  " % (self.fitted_params()[i])
      

          
    int_graph=xmgr.Graph(title,subtitle)
    int_graph.add_dataset(int_dataset)
    int_graph.add_dataset(inifit_dataset)
    int_graph.add_dataset(fit_dataset)
    int_graph.set_xaxis("X",x_min, x_max)
    int_graph.set_yaxis("Y",y_min, y_max)
    int_graph.writeout(fname+".xmgr")

  #------------------------------------------------------------------------




  #------------------------------------------------------------------------

#-------------------------------------------------------------------------

class dummy_function(Any_Func):
  'this is a fake function to allow just data display'
  def fit_data(self,error_estimate_trials=10, epsilon=1e-6):

      self.fit = no_real_fit(self.data, self, self.init_params, epsilon)
  def parameter_count(self):
    return 1
  
  def value(self, params, x):
    return params


#====== end of code for index assignment







class display_peak_heights_dialog( relaxation_dialog):
   def __init__(self, session,
                title='Displaying the peak heights vs. interleave index'):
      relaxation_dialog.__init__(self, session, title)
     
 # ---------------------------------------------------------------------------
  #
   def fit_function(self, th_pairs, assignment):

    h_values = map(lambda th: th[1], th_pairs)
    h_middle = .25 * (max(h_values) + min(h_values))

    
    params = (h_middle,-1,5*h_middle,-50)
    trials = self.error_estimate_trials
    epsilon=1e-10

    #-- run my Any_Function object now -----
    func = dummy_function()
    func.set_data(th_pairs)
    func.set_init_params(params)

    #-- try fitting ---   
    func.fit_data(trials,epsilon)
    return func.fit
  # ---------------------------------------------------------------------------
  #
   def show_fit_cb(self, event):

    fit = self.peak_list.event_line_data(event)
    if fit:
      show_fit(self.session, fit.name, fit, self.relative_scale_on_plots, self.show_peak_cb)
      self.current_fit_index=self.my_fit_list.index(fit)
  # ---------------------------------------------------------------------------
  #
   def show_next_fit(self):

    if self.current_fit_index==-1: return # not initialized yet
    
    if not self.current_fit_index<(len(self.my_fit_list)-1): return # end reached

    self.current_fit_index+=1
    fit=self.my_fit_list[self.current_fit_index]
    show_fit(self.session, fit.name, fit, self.relative_scale_on_plots,  self.show_peak_cb)
  
  # ---------------------------------------------------------------------------
  #
   def show_previous_fit(self):

    if self.current_fit_index==-1: return  # no fit chosen yet

    
    if not self.current_fit_index>0: return # start reached

    self.current_fit_index-=1
    fit=self.my_fit_list[self.current_fit_index]
    show_fit(self.session, fit.name, fit, self.relative_scale_on_plots,  self.show_peak_cb)

 
 

#==========================================================================================
   def peak_line(self, peak, fit):

     htext = ''
     for t, h, dh in fit.xy_pairs:
       htext = htext + '%-13.6g ' % h
 
     line = ('%-13s' % (peak.assignment)  + htext)
     return line
#==========================================================================================  
   def show_heading(self, spectrum_times):

     self.peak_list.clear()
     heading = '%-13s' % ('Index:')
     for s, t in spectrum_times:
       st = '%g' %  t 
       heading = heading + '%-13s ' % st
     self.peak_list.heading['text'] = heading
#==========================================================================================
   def show_peaks(self, peaks, spectrum_times):

     single_position = self.single_peak_position.get()
     self.stoppable_loop(' peaks', 1)
     for p in self.session.selected_peaks():
       self.check_for_stop()
       if single_position or not p.is_assigned:
         assignment = None
       else:
	 assignment = p.assignment
       th_pairs = self.time_height_pairs(p.position, assignment, spectrum_times)
       fit = self.fit_function(th_pairs, assignment)
       fit.name = p.assignment
       fit.peak_position = p.position
       fit.spectrum_times = spectrum_times
       line = self.peak_line(p, fit)
       self.peak_list.append(line, fit)
       self.peak_list.listbox.see('end')
       #-- append short list for saving and for viewing
       self.my_fit_list.append(fit)
      

  # ---------------------------------------------------------------------------
#==========================================================================================


def run(session):
  sputil.the_dialog(display_peak_heights_dialog,session).show_peak_heights()
