# ==============================================================================
# Assign side-chain resonances in uniformly C13,N15-labeled large proteins
# using 4D NOESY and prior assignment of backbone.
#
import os, Tkinter
import sparky, strips, sputil, tkutil, pyutil

import spectra_setup, import_shifts

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

default_settings = {'noesy_spec': None,
                    'noesy_axes': [0, 1, 2, 3],             # (N, H, CX, HX)
                       'inverse': 0,
                    'tocsy_spec': None,
                    'tocsy_axes': [0, 1, 2],                # (X, Y, Z)
                     'pos_color': 'yellow',
                     'neg_color': 'blue',
                    'tolerances': [0.2, 0.02, 0.2, 2]}      # (N, H, CAB, CGD)

view_options = ('positive_levels',
                'negative_levels',
                'axis_order',
                'show_scales',
                'show_scrollbars')

pointer_mode = { 'F1': 'select',
                 'F2': 'center',
                 'F3': 'addGridBoth',
                 'F4': 'addGridHorz',
                 'F5': 'addGridVert',
                 'F6': 'addLabel',
                 'F7': 'addLine',
                 'F8': 'findAddPeak',
                'F10': 'integrate',
                'F11': 'zoom',
                'F12': 'duplicateZoom'}

assignable_CX = ('CA','CB','CG','CG1','CG2','CD','CD1','CD2','CE')


# ==============================================================================
# The main GUI for assigning side-chain resonances.
#
class sidechain_assign_dialog(tkutil.Dialog):
    
    def __init__(self, session):
        
        self.session = session
        self.shifts = [{'group':x} for x in ('X1','X2','X3')]
        self.settings = default_settings
        self.strip_data = {}
        self.lines = []
        
        tkutil.Dialog.__init__(self, session.tk, "Assign Side-Chain Resonances")
        
        self.top.columnconfigure(0, weight = 1)
        self.top.rowconfigure(1, weight = 1)
        
        self.top.bind_all('<KeyPress>', self.sparky_cmd)
        self.top.bind('<FocusIn>', self.refresh)
        self.top.bind('<Destroy>', self.clean_noesy, 1)
        self.top.bind('<Destroy>', self.clean_plot, 1)
        
        ts = self.triplet_selector(self.top)
        ts.grid(row = 0, sticky = 'we', padx = 3)
        
        pl = peak_list(self.top)
        pl.frame.grid(row = 1, sticky = 'news', padx = 3, pady = 3)
        pl.listbox.bind('<ButtonRelease-1>', self.list_goto_peak)
        pl.listbox.bind('<Shift-ButtonRelease-1>', self.list_toggle_assign)
        pl.listbox.bind('<ButtonRelease-3>', self.CCH_strip)
        self.peak_list = pl
        
        self.peak_tracer = peak_tracer()
        
        self.status = Tkinter.Label(self.top, anchor = 'w', relief = 'ridge', text =
                      "To begin, please setup spectra and import chemical shifts.")
        self.status.grid(row = 2, stick = 'we', padx = 3)
        
        br = tkutil.button_row(self.top,
                               ("Setup ...", self.setup_cb),
                               ("Import shifts ...", self.import_shifts_cb),
                               ("Close", self.close_cb)
                              )
        br.frame.grid(row = 3, padx = 3, pady = 3)
        
        n1 = session.notify_me('removed spectrum from project', self.check_spec)
        n2 = session.notify_me('selection changed', self.peak_list.rebuild)
        n3 = session.notify_me('dragged peak', self.sync_with_peak)
        
        self.notices = (n1, n2, n3)
        self.top.bind('<Destroy>', self.cancel_notices, 1)
    
    # --------------------------------------------------------------------------
    #
    def sparky_cmd(self, event):
        
        if self.dialog_destroyed: return
        
        if str(self.top) in str(event.widget):
            
            if event.keysym == 'Delete':
                self.session.command_characters(chr(127))
            elif event.keysym in pointer_mode:
                self.session.pointer_mode = pointer_mode[event.keysym]
            else:
                self.session.command_characters(event.char)
        
        self.refresh(event)
    
    # --------------------------------------------------------------------------
    # Refresh peak list, strip plot, etc. upon specific event to
    # keep their display up-to-date.
    #
    def refresh(self, event):
        
        if event.keysym == 'Delete':
            
            diff = self.peak_list.rebuild()
            if diff:
                self.status['text'] = ("%s deleted near %s."
                % (count_peaks(diff), self.N_H_CX))
            
            self.del_strips()
            self.peak_tracer.rebuild()
        
        else:
            changed_peaks = self.peak_tracer.check()
            if changed_peaks:
                
                self.peak_list.rebuild()
                self.replot_strips(changed_peaks)
                
                for peak in changed_peaks:
                    update_peak_label(peak)
    
    # --------------------------------------------------------------------------
    #
    def clean_noesy(self, event = None):
        
        if event and str(event.widget) != str(self.top): return
        
        for line in self.lines:
            sparky_del(self.session, line)
        
        self.lines = []
    
    # --------------------------------------------------------------------------
    #
    def clean_plot(self, event = None):
        
        if event and str(event.widget) != str(self.top): return
        
        if hasattr(self, 'strip_plot'):
            plot = self.strip_plot
            
            if not plot.dialog_destroyed:
                plot.delete_strips(self.strip_data.keys())
                
                if not plot.strips:
                    plot.top.destroy()
    
    # --------------------------------------------------------------------------
    #
    def check_spec(self, spec):
        
        if spec == self.settings['noesy_spec']:
            self.status['text'] = "4D NOESY '%s' closed!" % spec.name
            
            self.peak_list.reset()
            self.peak_tracer.reset()
            self.clean_plot()
        
        if spec == self.settings['tocsy_spec']:
            self.status['text'] = "CCH-TOCSY '%s' closed!" % spec.name
    
    # --------------------------------------------------------------------------
    # Delete strips whose associated NOE peak no longer exists.
    #
    def del_strips(self):
        
        for strip, data in self.strip_data.items():
            
            peak = data[0]
            
            if not sparky.object_exists(peak):
                
                line = data[3]
                sparky_del(self.session, line)      # delete line in the strip
                del self.strip_data[strip]
                
                self.strip_plot.delete_strips([strip])
    
    # --------------------------------------------------------------------------
    # Replot strips for the given NOE peaks.
    #
    def replot_strips(self, peaks):
        
        for strip, data in self.strip_data.items():
            
            peak, NH_id, CX_id, line = data
            
            if peak in peaks:
                
                freq = self.strip_freq(peak, NH_id, CX_id)
                spec = self.settings['tocsy_spec']
                strip.center = sputil.alias_onto_spectrum(freq, spec)
                
                label = self.strip_label(freq, CX_id)
                strip.label_text = label
                
                if strip.label:
                    strip.label['text'] = label
                
                sparky_del(self.session, line)
                line = self.strip_line(freq)
                
                self.strip_data[strip] = (peak, NH_id, CX_id, line)
                
                self.strip_plot.set_y_scale(strip)
                self.show_strip(strip)
    
    # --------------------------------------------------------------------------
    #
    def sync_with_peak(self, peak):
        
        if peak in self.peak_list.line_data:
            self.peak_list.rebuild()
        
        self.top.after_idle(self.replot_strips, [peak])
        sputil.select_peak(peak)
    
    # --------------------------------------------------------------------------
    #
    def cancel_notices(self, event):
        
        if str(event.widget) == str(self.top):
            if sparky.object_exists(self.session):
                
                for notice in self.notices:
                    self.session.dont_notify_me(notice)
                
                self.notices = ()
    
    # --------------------------------------------------------------------------
    # Display protein sequence in fragments of three consecutive residues.
    # User can scroll to view any fragment, and define a N-H-CX spin triplet
    # among its residues as the criteria for finding possible peaks.
    #
    def triplet_selector(self, parent):
        
        frame = Tkinter.Frame(parent)
        frame.columnconfigure(1, weight = 1)
        
        self.NH_var = Tkinter.StringVar()
        self.CX_var = Tkinter.StringVar()
        
        residue_menu.postcmd = self.find_peaks
        self.menus = {}
        
        for col in range(3):
            self.menus[col] = residue_menu(frame, self.NH_var, self.CX_var)
            self.menus[col].grid(row = 0, column = col, pady = 3)
        
        self.scale = Tkinter.Scale(frame, showvalue = 0, to = 0,
                                   highlightthickness = 0,
                                   orient = 'horizontal',
                                   command = self.update_menus)
        self.scale.grid(row = 1, columnspan = 3, sticky = 'we', pady = 3)
        
        return frame
    
    # --------------------------------------------------------------------------
    #
    def update_menus(self, index):
        
        for col, menu in self.menus.items():
            menu.update(self.shifts[int(index) + col])
    
    # --------------------------------------------------------------------------
    #
    def find_peaks(self):
        
        self.update_menus(self.scale.get())
        self.peak_list.reset()
        self.peak_tracer.reset()
        self.clean_noesy()                  # delete previously drawn lines
        
        NH_id = self.NH_var.get()
        CX_id = self.CX_var.get()
        
        if NH_id == "" or CX_id == "": return
        
        spec = self.settings['noesy_spec']
        axes = self.settings['noesy_axes']
        
        if not hasattr(spec, 'name'):
            self.status['text'] = "Please setup 4D NOESY."
            return
        
        #
        # Trace the strip-associated peaks.
        #
        peaks = [data[0] for data in self.strip_data.values()]
        self.peak_tracer.trace(peaks)
        
        self.status['text'] = "Finding possible peaks ..."
        self.status.update_idletasks()
        
        ref_view, view = dual_view(spec)
        self.show_ref_plane(NH_id, CX_id, ref_view)
        regions = self.show_peak_region(NH_id, CX_id, view)
        
        for region, line in zip(regions, self.lines):
            
            #
            # Find only peaks with the correct sign.
            #
            if line.color == self.settings['pos_color']:
                peaks = peak_search(spec, view, region, '+')
            else:
                peaks = peak_search(spec, view, region, '-')
            
            self.peak_list.append_peaks(peaks)
            self.peak_tracer.trace(peaks)
        
        axis_name = ('N', 'H', 'CX', 'HX')
        axis_name = pyutil.unpermute(axis_name, axes)
        self.peak_list.show_heading(axis_name)
        
        total = self.peak_list.listbox.size()
        self.status['text'] = ("%s found near %s."
        % (count_peaks(total), self.N_H_CX))
        
        self.top.focus_set()
    
    # --------------------------------------------------------------------------
    # For N(i)-H(i)-CX(i), show CX-HX plane defined by N(i+1)-H(i+1)
    # (or i-1 if i is the last residue) as the reference plane;
    # for N(i)-H(i)-CX(j), show CX-HX plane defined by N(j)-H(j) as
    # the reference plane.
    #
    def show_ref_plane(self, NH_id, CX_id, ref_view):
        
        spec = self.settings['noesy_spec']
        N, H, CX, HX = self.settings['noesy_axes']
        freq = [0, 0, 0, 0]
        
        i = int(NH_id.split()[0][1:]) - 1
        j = int(CX_id.split()[0][1:]) - 1
        last = len(self.shifts) - 1
        
        if i != j:
            freq[N], freq[H] = self.shifts[j]['NH']
        elif i == last:
            freq[N], freq[H] = self.shifts[i-1]['NH']
        else:
            freq[N], freq[H] = self.shifts[i+1]['NH']
        
        if None in (freq[N], freq[H]):          # preceding NH shifts unknown
            ref_view.center = (0, 0, 0, 0)
        else:
            freq[CX], freq[HX] = plane_center(spec, CX, HX)
            ref_view.center = sputil.alias_onto_spectrum(freq, spec)
        
        zoom_full_view(ref_view)
    
    # --------------------------------------------------------------------------
    #
    def show_peak_region(self, NH_id, CX_id, view):
        
        spec = self.settings['noesy_spec']
        N, H, CX, HX = self.settings['noesy_axes']
        freq = [0, 0, 0, 0]
        
        freq[N], freq[H] = self.get_shifts(NH_id)
        freq[CX], freq[HX] = plane_center(spec, CX, HX)
        
        view.center = sputil.alias_onto_spectrum(freq, spec)
        zoom_full_view(view)
        
        #
        # Draw lines to highlight possible peak region.
        #
        mean, sd = self.get_shifts(CX_id)
        tols = self.settings['tolerances']
        
        self.N_H_CX = "N:%.4g, H:%.4g, CX:%.4g" % (freq[N], freq[H], mean)
        
        if sd < 0:
            CX_range = (mean - tols[2], mean + tols[2])
        else:
            CX_range = (mean - tols[3] * sd, mean + tols[3] * sd)
        
        for freq[CX] in CX_range:
            self.lines.append(axis_line(spec, HX, freq))
            
            #
            # Color the lines according to peak sign.
            #
            folds = alias_folds(spec, freq, N, CX)
            
            if (folds + self.settings['inverse']) % 2 == 0:
                self.lines[-1].color = self.settings['pos_color']
            else:
                self.lines[-1].color = self.settings['neg_color']
        
        #
        # Calculate peak picking region.
        #
        # If not folded, in between the two lines; if folded, split into two
        # parts (from the 1st line to the upper boundary of CX-HX plane, and
        # from the lower boundary of CX-HX plane to the 2nd line).
        #
        offset = [0, 0, 0, 0]
        offset[N], offset[H] = tols[0], tols[1]
        
        start = pyutil.subtract_tuples(self.lines[0].start, offset)
        end = pyutil.add_tuples(self.lines[1].end, offset)
        
        if self.lines[0].color == self.lines[1].color:
            return [(start, end)]
        
        else:
            freq[CX] = spec.region[1][CX]
            freq[HX] = spec.region[1][HX]
            ppm_max = pyutil.add_tuples(freq, offset)
            
            freq[CX] = spec.region[0][CX]
            freq[HX] = spec.region[0][HX]
            ppm_min = pyutil.subtract_tuples(freq, offset)
            
            return [(start, ppm_max), (ppm_min, end)]
    
    # --------------------------------------------------------------------------
    #
    def get_shifts(self, atom_id):
        
        group, atom = atom_id.split()
        index = int(group[1:]) - 1
        
        return self.shifts[index][atom]
    
    # --------------------------------------------------------------------------
    #
    def get_assignment(self, NH_id, CX_id):
        
        NH_group = NH_id.split()[0]
        CH_group, CX = CX_id.split()
        HX = 'H' + CX[1:]
        
        axes = self.settings['noesy_axes']
        groups = (NH_group, NH_group, CH_group, CH_group)
        atoms = ('N', 'H', CX, HX)
        
        return zip(axes, groups, atoms)
    
    # --------------------------------------------------------------------------
    #
    def get_alias(self, peak, NH_id, CX_id):
        
        if peak.alias != (0, 0, 0, 0):
            return peak.alias
        
        #
        # Calculate the expected peak frequency.
        #
        N_shift, H_shift = self.get_shifts(NH_id)
        
        CH_group, CX = CX_id.split()
        CH_index = int(CH_group[1:]) - 1
        HX = 'H' + CX[1:]
        
        CX_shift = self.shifts[CH_index][CX][0]
        HX_shift = self.shifts[CH_index][HX]
        
        freq = (N_shift, H_shift, CX_shift, HX_shift)
        freq = pyutil.unpermute(freq, self.settings['noesy_axes'])
        
        return closest_alias(peak, freq)
    
    # --------------------------------------------------------------------------
    #
    def list_goto_peak(self, event):
        
        peak = self.peak_list.event_peak(event)
        if peak:
            
            for strip, data in self.strip_data.items():
                
                if peak == data[0]:
                    self.show_strip(strip)
                        
            ref_view, view = dual_view(peak.spectrum)
            
            NH_id = self.NH_var.get()
            CX_id = self.CX_var.get()
            self.show_ref_plane(NH_id, CX_id, ref_view)
            
            if ref_view.center != (0, 0, 0, 0):
                ref_view.set_crosshair_position(peak.position)
            
            goto_peak(view, peak)
            self.top.focus_set()
    
    # --------------------------------------------------------------------------
    # Assign NOE peak in the peak list;
    # if the peak is previously assigned, unassign it.
    #
    def list_toggle_assign(self, event):
        
        peak = self.peak_list.event_peak(event)
        if peak:
            
            NH_id = self.NH_var.get()
            CX_id = self.CX_var.get()
            
            if peak.is_assigned:
                unassign_peak(peak)
            else:
                assignment = self.get_assignment(NH_id, CX_id)
                assign_peak(peak, assignment)
            
            self.update_alias(peak, NH_id, CX_id)
            self.list_goto_peak(event)
    
    # --------------------------------------------------------------------------
    # Alias only fully assigned peak.
    #
    def update_alias(self, peak, NH_id, CX_id):
        
        if peak.is_assigned:
            peak.alias = self.get_alias(peak, NH_id, CX_id)
        else:
            peak.alias = (0, 0, 0, 0)
    
    # --------------------------------------------------------------------------
    #
    def CCH_strip(self, event):
        
        peak = self.peak_list.event_peak(event)
        if peak and peak.selected:
            
            spec = self.settings['tocsy_spec']
            axes = self.settings['tocsy_axes']
            
            if not hasattr(spec, 'name'):
                self.status['text'] = "Please setup CCH-TOCSY."
                return
            
            plot = strips.strip_dialog(self.session)
            
            if not hasattr(self, 'strip_plot'):
                is_new_plot = 1
            elif self.strip_plot is not plot:
                is_new_plot = 1
            else:
                is_new_plot = 0
            
            if is_new_plot:
                
                plot.top.geometry('320x640')
                
                plot.top.bind('<Double-ButtonRelease-1>', self.strip_goto_peak)
                plot.top.bind('<Shift-ButtonRelease-1>', self.strip_toggle_assign)
                plot.top.bind('<Destroy>', self.del_strip_data, 1)
                
                menu_bar = plot.top.winfo_children()[0]
                self.auto_alias = Tkinter.IntVar()
                cb = Tkinter.Checkbutton(menu_bar, highlightthickness = 0,
                                         text = "Auto-alias",
                                         variable = self.auto_alias)
                cb.pack(side = 'right', padx = 20)
                cb.select()
            
            plot.show_window(1)
            plot.top.update_idletasks()
            
            NH_id = self.NH_var.get()
            CX_id = self.CX_var.get()
            
            freq = self.strip_freq(peak, NH_id, CX_id)
            label = self.strip_label(freq, CX_id)
            line = self.strip_line(freq)
            
            center = sputil.alias_onto_spectrum(freq, spec)
            strip = plot.spectrum_strip(spec, axes, center, label)
            plot.top.after_idle(self.add_strip, strip)
            
            self.strip_data[strip] = (peak, NH_id, CX_id, line)
            self.strip_plot = plot
    
    # --------------------------------------------------------------------------
    # Calculate its corresponding frequency in CCH-TOCSY for
    # the selected NOE peak.
    #
    def strip_freq(self, peak, NH_id, CX_id):
        
        X, Y, Z = self.settings['tocsy_axes']
        N, H, CX, HX = self.settings['noesy_axes']
        
        if self.auto_alias.get():
            peak_alias = self.get_alias(peak, NH_id, CX_id)
            peak_freq = pyutil.add_tuples(peak.position, peak_alias)
        else:
            peak_freq = peak.frequency
        
        freq = [0, 0, 0]
        freq[X] = peak_freq[HX]
        freq[Y] = freq[Z] = peak_freq[CX]
        
        return freq
    
    # --------------------------------------------------------------------------
    #
    def strip_label(self, freq, CX_id):
        
        X, Y, Z = self.settings['tocsy_axes']
        group, atom = CX_id.split()
        label = "%.4g\n%.4g\n%s" % (freq[Z], freq[X], group + atom[1:])
        
        return label
    
    # --------------------------------------------------------------------------
    # Draw a line to show its CX position in CCH-TOCSY for
    # the selected NOE peak.
    #
    def strip_line(self, freq):
        
        spec = self.settings['tocsy_spec']
        X, Y, Z = self.settings['tocsy_axes']
        
        return axis_line(spec, X, freq)
    
    # --------------------------------------------------------------------------
    #
    def add_strip(self, strip):
        
        self.strip_plot.add_strips([strip])
        self.strip_plot.update_vertical_scrollbar()
        
        self.show_strip(strip)
    
    # --------------------------------------------------------------------------
    #
    def show_strip(self, strip):
        
        plot = self.strip_plot
        plot.show_window(1)
        
        count = plot.visible_strip_count()
        
        first = plot.first_strip_index          # index of 1st visible strip
        last = first + count - 1
        
        index = plot.strip_position(strip)
        
        if index < first:
            plot.first_strip_index = index
        
        if index > last:
            plot.first_strip_index = index - count + 1
        
        plot.change_visible_strips()
        self.focus_strip(strip)
    
    # --------------------------------------------------------------------------
    # Give input focus to the strip,
    # so it will be selected and show the focus highlight.
    #
    def focus_strip(self, strip):
        
        tcl = strip.view.session.tk.tk.call
        tcl('focus', strip.view.frame + '.drawing')
        
    # --------------------------------------------------------------------------
    #
    def strip_goto_peak(self, event):
        
        data = self.event_strip_data(event)
        if data:
            
            peak, NH_id, CX_id = data[:3]
            ref_view, view = dual_view(peak.spectrum)
            
            self.show_ref_plane(NH_id, CX_id, ref_view)
            
            if ref_view.center != (0, 0, 0, 0):
                ref_view.set_crosshair_position(peak.position)
            
            goto_peak(view, peak)
    
    # --------------------------------------------------------------------------
    # Assign NOE peak associated to the strip;
    # if the peak is previously assigned, unassign it.
    #
    def strip_toggle_assign(self, event):
        
        data = self.event_strip_data(event)
        if data:
            
            peak, NH_id, CX_id = data[:3]
            
            if peak.is_assigned:
                unassign_peak(peak)
            else:
                assignment = self.get_assignment(NH_id, CX_id)
                assign_peak(peak, assignment)
            
            self.update_alias(peak, NH_id, CX_id)
            
            if peak in self.peak_list.line_data:
                self.peak_list.rebuild()
            
            self.strip_goto_peak(event)
    
    # --------------------------------------------------------------------------
    # Return data entry of the strip where event occurs.
    #
    def event_strip_data(self, event):
        
        for strip, data in self.strip_data.items():
            
            if not strip.view_exists():
                continue
            
            if str(event.widget) == strip.view.frame + '.drawing':
                return data
        
        return None
    
    # --------------------------------------------------------------------------
    # Delete data entry of the strip that no longer exists.
    #
    def del_strip_data(self, event):
        
        plot = self.strip_plot
        
        if plot.dialog_destroyed:
            plot.strips = []
        
        for strip, data in self.strip_data.items():
            
            if strip not in plot.strips:
                line = data[3]
                sparky_del(self.session, line)      # delete line in the strip
                del self.strip_data[strip]
    
    # --------------------------------------------------------------------------
    # Show "Setup Spectra and Preferences" dialog.
    #
    def setup_cb(self):
        
        dialog = sputil.the_dialog(spectra_setup.spectra_setup_dialog, self.session)
        dialog.set_parent_dialog(self, self.settings, self.new_settings)
        dialog.show_window(1)
    
    # --------------------------------------------------------------------------
    #
    def new_settings(self, settings):
        
        if settings != self.settings:
            self.settings = settings
            noesy = settings['noesy_spec'].name
            tocsy = settings['tocsy_spec'].name
            self.status['text'] = "Using spectra '%s' and '%s'." % (noesy, tocsy)
            self.find_peaks()
    
    # --------------------------------------------------------------------------
    # Show "Import Chemical Shifts" dialog.
    #
    def import_shifts_cb(self):
        
        dialog = sputil.the_dialog(import_shifts.import_shifts_dialog, self.session)
        dialog.set_parent_dialog(self, None, self.new_shifts)
        dialog.show_window(1)
    
    # --------------------------------------------------------------------------
    #
    def new_shifts(self, shifts, file_path):
        
        if shifts != self.shifts:
            self.shifts = shifts
            self.scale['to'] = len(shifts) - 3
            self.scale.set(0)
            self.NH_var.set("")
            self.CX_var.set("")
            self.status['text'] = "Using shifts from '%s'." % file_path
            self.find_peaks()
    
    # --------------------------------------------------------------------------
    # Close the dialog window and all its setting dialog windows if any.
    #
    # A bug fix to the default method in class "Dialog" in module "tkutil.py",
    # where closing the dialog window may cause "TclError: bad window path name"
    # as a result of trying to close some of its setting dialog windows that
    # have previously been destroyed.
    #
    def close_cb(self):
        
        if hasattr(self, 'setting_dialogs'):
            for settings_dialog in self.setting_dialogs:
                
                #
                # "parent_destroyed()" will check whether "settings_dialog"
                # has been destroyed before trying to close it.
                #
                settings_dialog.parent_destroyed()
        
        self.clean_noesy()
        self.clean_plot()
        self.top.withdraw()


# ==============================================================================
# A pull-down menu for selecting atoms in a residue.
#
class residue_menu(Tkinter.Menubutton):
    
    postcmd = None
    
    def __init__(self, parent, NH_var, CX_var):
        
        self.var_list = [('NH', NH_var)]
        self.var_list += [(CX, CX_var) for CX in assignable_CX]
        
        Tkinter.Menubutton.__init__(self, parent, width = 10, anchor = 'w',
                                    indicatoron = 1, relief = 'raised')
        
        self.menu = Tkinter.Menu(self, tearoff = 0)
        self['menu'] = self.menu
    
    # --------------------------------------------------------------------------
    # Update menu state, label and entries.
    #
    def update(self, shifts):
        
        self['text'] = shifts['group']
        self.menu.delete(0, 'end')
        
        if "X" in self['text']:
            self['state'] = 'disable'       # disable menu for unknown residue
            return
        else:
            self['state'] = 'normal'
        
        for atom, var in self.var_list:
            
            if atom not in shifts: continue
            
            #
            # Highlight in red if empirical range is used for CA or CB.
            #
            if atom in ('CA', 'CB') and shifts[atom][1] != -1:
                color = 'red'
            else:
                color = 'black'
            
            self.menu.add_radiobutton(label = atom, variable = var,
                                      foreground = color,
                                      value = shifts['group'] + " " + atom,
                                      command = self.__class__.postcmd)
            
            #
            # Show name of the selected atom in menu label.
            #
            if self.menu.entrycget('end', 'value') == var.get():
                self['text'] += " " + atom
            
            #
            # Disable an entry if its atom's shift is None (i.e. unknown).
            #
            if None in shifts[atom]:
                self.menu.entryconfig('end', state = 'disabled')
        
        self.menu.insert_separator(1)


# ==============================================================================
#
class peak_list(sputil.peak_listbox):
    
    def __init__(self, parent):
        
        sputil.peak_listbox.__init__(self, parent)
        
        self.heading.config(font = monospace_font, bd = 0, padx = 3)
        self.listbox.config(font = monospace_font, height = 10, width = 50)
    
    # --------------------------------------------------------------------------
    #
    def show_heading(self, axes):
        
        heading = ""
        for i, axis in enumerate(axes):
            heading += ("w%d %s" % (i+1, axis)).rjust(9)
        heading += "D.H.".rjust(12)
        
        self.heading['text'] = heading[2:]
    
    # --------------------------------------------------------------------------
    #
    def append_peaks(self, peaks):
        
        for peak in sort_peaks(peaks):
            
            #
            # Display peak frequency and data height;
            # indicate assigned peaks with asterick mark.
            #
            peak_info = ("%9.3f" * len(peak.frequency) % peak.frequency +
                         "%12d" % sputil.peak_height(peak) +
                         "  *" * peak.is_assigned)
            self.append(peak_info[2:], peak)
            
            if peak.selected:
                self.listbox.selection_set('end')
                self.listbox.activate('end')
    
    # --------------------------------------------------------------------------
    # Remove obsolete peaks from the list and update peak info.
    #
    def rebuild(self):
        
        anchor = self.listbox.index('@1,1')         # record position
        
        old_peaks = self.line_data
        peaks = filter(sparky.object_exists, old_peaks)
        self.clear()
        self.append_peaks(peaks)
        
        self.listbox.yview(anchor)                  # restore position
        
        if self.listbox.curselection():
            self.listbox.see('active')              # show selection if any
        
        return len(old_peaks) - len(peaks)
    
    # --------------------------------------------------------------------------
    #
    def reset(self):
        
        self.heading['text'] = ""
        self.clear()


# ==============================================================================
# Trace changes made to peak (e.g. aliased, assigned).
#
class peak_tracer:
    
    def __init__(self):
        
        self.traced_attrs = ('position', 'alias', 'is_assigned')
        self.traced_peaks = {}
    
    # --------------------------------------------------------------------------
    # Add peaks that need to be traced.
    #
    def trace(self, peaks):
        
        for peak in peaks:
            
            attrs = [getattr(peak, attr) for attr in self.traced_attrs]
            self.traced_peaks[peak] = attrs
    
    # --------------------------------------------------------------------------
    # Find peaks that have changes in the traced attributes.
    #
    def check(self):
        
        changed_peaks = []
        
        for peak in self.traced_peaks:
            
            attrs = [getattr(peak, attr) for attr in self.traced_attrs]
            
            if self.traced_peaks[peak] != attrs:
                changed_peaks.append(peak)
        
        if changed_peaks:
            self.rebuild()
        
        return changed_peaks
    
    # --------------------------------------------------------------------------
    # Stop tracing peaks that no longer exist
    # and update the traced attributes to the current value.
    #
    def rebuild(self):
        
        old_peaks = self.traced_peaks.keys()
        peaks = filter(sparky.object_exists, old_peaks)
        self.reset()
        self.trace(peaks)
    
    # --------------------------------------------------------------------------
    #
    def reset(self):
        
        self.traced_peaks = {}


# ==============================================================================
# Return two views of the given spectrum.
#
def dual_view(spec):
    
    views = filter(lambda view, spec = spec:
                   view.spectrum == spec and view.is_top_level_window,
                   spec.session.project.view_list())
    
    while len(views) < 2:
        views += [spec.session.create_view(None, spec)]
        
        for attr in view_options:
            value = getattr(views[0], attr)
            setattr(views[-1], attr, value)         # copy view options
    
    for view in views[:2]:
        raise_view_window(view)
    
    return views[:2]


# ==============================================================================
# Raise the view window above all windows on the screen.
#
def raise_view_window(view):
    
    tcl = view.session.tk.tk.call
    tcl('wm', 'deiconify', view.frame)
    tcl('raise', view.frame)
    tcl('focus', view.frame + '.drawing')       # set focus to drawing region


# ==============================================================================
#
def zoom_full_view(view):
    
    #
    # Determine geometry of the view drawing region.
    #
    tcl = view.session.tk.tk.call
    tcl('update', 'idletasks')
    width = tcl('winfo', 'width', view.frame + '.drawing')
    height = tcl('winfo', 'height', view.frame + '.drawing')
    
    X, Y = view.axis_order[:2]
    X_pixel_size = view.spectrum.sweep_width[X] / width
    Y_pixel_size = view.spectrum.sweep_width[Y] / height
    
    #
    # Determine zoom factor such that the entire range of both axes
    # can be covered in the view.
    #
    X_zoom = X_pixel_size / view.pixel_size[X]
    Y_zoom = Y_pixel_size / view.pixel_size[Y]
    zoom_factor = max(X_zoom, Y_zoom)
    
    view.pixel_size = pyutil.scale_tuple(view.pixel_size, zoom_factor)


# ==============================================================================
# Get the center coordinates of the specified 2D plane
# in a multi-dimensional spectrum.
#
def plane_center(spec, X, Y):
    
    if spec.dimension >= 2:
        
        ppm_min, ppm_max = spec.region
        
        X_center = (ppm_min[X] + ppm_max[X]) / 2
        Y_center = (ppm_min[Y] + ppm_max[Y]) / 2
        
        return X_center, Y_center


# ==============================================================================
# Draw a line through the specified frequency, from edge to edge
# along a spectrum axis (similar to grid).
#
def axis_line(spec, axis, freq):
    
    freq = list(freq)
    ppm_min, ppm_max = spec.region
    
    freq[axis] = ppm_min[axis]
    start = sputil.alias_onto_spectrum(freq, spec)
    freq[axis] = ppm_max[axis]
    end = sputil.alias_onto_spectrum(freq, spec)
    
    line = sparky.Line(spec, start, end)
    line.selected = 0
    
    return line


# ==============================================================================
#
def peak_search(spec, view, region, sign):
    
    threshold = (view.negative_levels.lowest, view.positive_levels.lowest)
    linewidth = spec.pick_minimum_linewidth
    drop_off = spec.pick_minimum_drop_factor
    
    #
    # Sparky will pick up a new peak (i.e. not in the peak list)
    # as long as part of it falls inside the region.
    #
    new_peaks = spec.pick_peaks(region, threshold, linewidth, drop_off)
    
    matched_peaks = []
    
    for peak in spec.peak_list():       # search among both new and existing peaks
        
        c1 = is_in_region(peak, region)
        c2 = is_above_threshold(peak, threshold)
        c3 = peak_sign(peak) == sign
        
        if c1 and c2 and c3:
            matched_peaks.append(peak)
        
        elif peak in new_peaks:
            sparky_del(spec.session, peak)      # delete unmatched new peak
    
    return matched_peaks


# ==============================================================================
# Check whether the peak center is in the region.
#
def is_in_region(peak, region):
    
    ppm_min, ppm_max = region
    
    for p, min_, max_ in zip(peak.position, ppm_min, ppm_max):
        if p < min_ or p > max_:
            return 0
    
    return 1


# ==============================================================================
# Check whether the peak intensity is above the threshold.
#
def is_above_threshold(peak, threshold):
    
    data_height = sputil.peak_height(peak)
    
    if data_height <= threshold[0] or data_height >= threshold[1]:
        return 1
    else:
        return 0


# ==============================================================================
# Classify peak as positive or negative by data height.
#
def peak_sign(peak):
    
    if sputil.peak_height(peak) > 0:
        return '+'
    else:
        return '-'


# ==============================================================================
#
def goto_peak(view, peak):
    
    view.center = peak.position
    view.set_crosshair_position(peak.position)
    
    sputil.select_peak(peak)


# ==============================================================================
#
def assign_peak(peak, assignment):
    
    for axis, group, atom in assignment:
        peak.assign(axis, group, atom)
    
    update_peak_label(peak)


# ==============================================================================
#
def unassign_peak(peak):
    
    for axis in range(peak.spectrum.dimension):
        peak.assign(axis, "", "")
    
    update_peak_label(peak)


# ==============================================================================
# Show assignment label only for fully assigned peak.
#
def update_peak_label(peak):
    
    label = peak.label
    session = peak.spectrum.session
    
    if peak.is_assigned:                    # all axes assigned
        peak.show_assignment_label()
    
    elif label and label.shows_assignment:
        sparky_del(session, label)


# ==============================================================================
# Sort peaks by intensity, from highest to lowest.
#
def sort_peaks(peaks):
    
    sorted_peaks = tkutil.sort_by_key(peaks, peak_intensity)
    sorted_peaks.reverse()
    
    return sorted_peaks


# ==============================================================================
# Estimate peak (or peak group) intensity using data height.
#
def peak_intensity(peak):
    
    data_height = sputil.peak_height(peak)
    
    return abs(data_height)


# ==============================================================================
#
def count_peaks(amount):
    
    if amount > 1:
        return "%d peaks" % amount
    elif amount == 1:
        return "1 peak"
    elif amount == 0:
        return "No peak"


# ==============================================================================
# Calculate the total number of folds required on given axes to alias
# frequency onto spectrum.
#
def alias_folds(spec, freq, *axes):
    
    ppm_min = spec.region[0]
    sw = spec.sweep_width
    
    folds = 0
    
    for axis in axes:
        folds += abs((freq[axis] - ppm_min[axis]) // sw[axis])
    
    return folds


# ==============================================================================
# Find alias for the peak such that the aliased peak will be closest to
# the reference frequency.
#
def closest_alias(peak, ref_freq):
    
    sweep_width = peak.spectrum.sweep_width
    position = peak.position
    alias = []
    
    for p, rf, sw in zip(position, ref_freq, sweep_width):
        
        down_dev = (rf - p) % sw
        up_dev = sw - down_dev
        
        if down_dev < up_dev:
            alias.append(rf - down_dev - p)
        else:
            alias.append(rf + up_dev - p)
    
    return alias


# ==============================================================================
# Delete a sparky object (e.g. peak, line, label).
#
def sparky_del(session, object):
    
    if sparky.object_exists(session) and sparky.object_exists(object):
        
        selected_ornaments = session.selected_ornaments()
        
        session.unselect_all_ornaments()
        object.selected = 1
        session.command_characters(chr(127))
        
        for ornament in selected_ornaments:
            if sparky.object_exists(ornament):
                ornament.selected = 1


# ==============================================================================
#
def show_sidechain_assign_dialog(session):
    
    dialog = sputil.the_dialog(sidechain_assign_dialog, session)
    dialog.show_window(1)
