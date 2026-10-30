# ==============================================================================
# Setup spectra and preferences used for side-chain assignment.
#
import Tkinter
import sparky, axes, sputil, tkutil


# ==============================================================================
# Window to show/change the current settings.
#
class spectra_setup_dialog(tkutil.Settings_Dialog):
    
    def __init__(self, session):
        
        self.session = session
        
        tkutil.Settings_Dialog.__init__(self, session.tk, "Setup Spectra and Preferences")
        
        for i in range(2):
            self.top.rowconfigure(i, weight = 1)
            self.top.columnconfigure(i, weight = 1)
        
        spec_setup.postcheck = self.check_settings
        
        self.noesy = spec_setup(session, self.top,
                                "4D NOESY", ['N','H','CX','HX'])
        self.noesy.frame.grid(sticky = 'news', padx = 3, pady = 3)
        
        self.inverse = Tkinter.IntVar()
        cb = Tkinter.Checkbutton(self.noesy.frame, text = "Inverse sign",
                                 highlightthickness = 0,
                                 variable = self.inverse)
        cb.grid(row = 1, column = 0, sticky = 'w', padx = 2, pady = 2)
        
        self.tocsy = spec_setup(session, self.top,
                                "CCH-TOCSY", ['X','Y','Z'])
        self.tocsy.frame.grid(sticky = 'news', padx = 3, pady = 3)
        
        pp = self.pref_panel(self.top)
        pp.grid(row = 0, rowspan = 2, column = 1,
                sticky = 'news', padx = 3, pady = 3)
        
        br = tkutil.button_row(self.top,
                               (" Ok ", self.ok_cb),
                               ("Apply", self.apply_cb),
                               ("Close", self.close_cb),
                              )
        br.frame.grid(columnspan = 2, padx = 3, pady = 3)
        
        self.ok, self.apply_ = br.buttons[:2]
        self.ok['state'] = 'disabled'
        self.apply_['state'] = 'disabled'
        
        add_spec = session.notify_me('added spectrum to project',
                                     self.check_settings)
        rmv_spec = session.notify_me('removed spectrum from project',
                                     self.check_settings)
        
        self.notices = (add_spec, rmv_spec)
        self.top.bind('<Destroy>', self.cancel_notices, 1)
    
    # --------------------------------------------------------------------------
    #
    def cancel_notices(self, event):
        
        if str(event.widget) == str(self.top):
            if sparky.object_exists(self.session):
                
                for notice in self.notices:
                    self.session.dont_notify_me(notice)
                
                self.notices = ()
    
    # --------------------------------------------------------------------------
    # Create the preference panel for colors and tolerances.
    #
    def pref_panel(self, parent):
        
        panel = Tkinter.LabelFrame(parent, text = "Preferences", padx = 2)
        
        color_picker.postcheck = self.check_colors
        
        self.pos_color = color_picker(panel, "Positive peak region:")
        self.pos_color.frame.pack(fill = 'x', expand = 1, anchor = 'w')
        
        self.neg_color = color_picker(panel, "Nagative peak region:")
        self.neg_color.frame.pack(fill = 'x', expand = 1, anchor = 'w')
        
        self.tols = tol_setup(panel, "Peak match tolerances:",
                              [('N', 1.0, 'ppm'), ('H', 0.1, 'ppm'),
                               ('CAB', 1.0, 'ppm'), ('CGD', 4.0, 'S.D.')])
        self.tols.frame.pack(fill = 'x', expand = 1, anchor = 'w')
        
        return panel
    
    # --------------------------------------------------------------------------
    #
    def show_settings(self, settings):
        
        if hasattr(settings['noesy_spec'], 'name'):
            self.noesy.set_spec(settings['noesy_spec'].name)
            self.noesy.set_axes(settings['noesy_axes'])
            self.inverse.set(settings['inverse'])
        else:
            self.noesy.set_spec("No spectrum")
            self.inverse.set(0)
        
        if hasattr(settings['tocsy_spec'], 'name'):
            self.tocsy.set_spec(settings['tocsy_spec'].name)
            self.tocsy.set_axes(settings['tocsy_axes'])
        else:
            self.tocsy.set_spec("No spectrum")
        
        self.pos_color.set(settings['pos_color'])
        self.neg_color.set(settings['neg_color'])
        
        self.tols.set(settings['tolerances'])
    
    # --------------------------------------------------------------------------
    # Make sure all the required spectra and axes are set.
    #
    def check_settings(self, spectrum = None):
        
        if spectrum:
            self.noesy.spec_menu.update()
            self.tocsy.spec_menu.update()
        
        specs = [self.noesy.get_spec(), self.tocsy.get_spec()]
        axes = self.noesy.get_axes() + self.tocsy.get_axes()
        
        if None in specs + axes:
            self.ok['state'] = 'disabled'
            self.apply_['state'] = 'disabled'
        else:
            self.ok['state'] = 'normal'
            self.apply_['state'] = 'normal'
    
    # --------------------------------------------------------------------------
    #
    def get_settings(self):
        
        return {'noesy_spec': self.noesy.get_spec(),
                'noesy_axes': self.noesy.get_axes(),
                   'inverse': self.inverse.get(),
                'tocsy_spec': self.tocsy.get_spec(),
                'tocsy_axes': self.tocsy.get_axes(),
                 'pos_color': self.pos_color.get(),
                 'neg_color': self.neg_color.get(),
                'tolerances': self.tols.get()}


    # --------------------------------------------------------------------------
    # Once a color is selected, disable its button in other color pickers.
    #
    def check_colors(self):
        
        for color, picker in self.pos_color.pickers.items():
            
            if color == self.neg_color.get():
                picker['state'] = 'disabled'
            else:
                picker['state'] = 'normal'
        
        for color, picker in self.neg_color.pickers.items():
            
            if color == self.pos_color.get():
                picker['state'] = 'disabled'
            else:
                picker['state'] = 'normal'


# ==============================================================================
# Grouped option menus for user to select a spectrum
# and define the corresponding axis for each of its nuclei.
#
class spec_setup:
    
    postcheck = None
    
    def __init__(self, session, parent, title, axes):
        
        self.session = session
        
        self.frame = Tkinter.LabelFrame(parent, text = title, padx = 2, pady = 2)
        self.frame.columnconfigure(0, weight = 1, minsize = 120)
        
        self.spec_menu = spec_menu(session, self.frame, len(axes))
        self.spec_menu.frame.grid(sticky = 'we')
        self.spec_menu.add_callback(self.update_axes)
        
        self.axis_menus = []
        
        for i, axis in enumerate(axes):
            
            menu = axis_menu(self.frame, axis + ":", i)
            menu.frame.grid(row = i, column = 1, padx = 2, pady = 2)
            menu.add_callback(lambda selection, index = i:
                              self.is_repeat(selection, index))
            
            self.axis_menus.append(menu)
    
    # --------------------------------------------------------------------------
    # Update all axis menus to show axes of the currently selected spectrum;
    # if no spectrum available, highlight spectrum menu in red.
    #
    def update_axes(self, selection):
        
        spectrum = sputil.name_to_spectrum(selection, self.session)
        
        for menu in self.axis_menus:
            menu.update(spectrum)
        
        if spectrum:
            self.spec_menu.menu.master['fg'] = 'black'
        else:
            self.spec_menu.menu.master['fg'] = 'red'
        
        self.__class__.postcheck()
    
    # --------------------------------------------------------------------------
    # Check for repeated selection of the same axis.
    #
    def is_repeat(self, selection, index):
        
        for menu in self.axis_menus:
            if menu.get() == selection and menu.index != index:
                menu.set("")
                menu.label['fg'] = 'red'
            elif menu.get() != "":
                menu.label['fg'] = 'black'
        
        self.__class__.postcheck()
    
    # --------------------------------------------------------------------------
    #
    def get_spec(self):
        return self.spec_menu.spectrum()
    
    def set_spec(self, name):
        self.spec_menu.set(name)
    
    # --------------------------------------------------------------------------
    #
    def get_axes(self):
        return [menu.chosen_axis() for menu in self.axis_menus]
    
    def set_axes(self, axes):
        for menu, axis in zip(self.axis_menus, axes):
            menu.set_axis(axis)


# ==============================================================================
# An option menu for spectrum selection.
#
class spec_menu(sputil.spectrum_menu):
    
    def __init__(self, session, parent, dimension):
        
        self.dimension = dimension
        
        sputil.spectrum_menu.__init__(self, session, parent, None)
        
        self.label.destroy()
        
        self.menu.master.config(anchor = 'w', highlightthickness = 0)
        self.menu.master.pack(fill = 'x', expand = 1, padx = 2, pady = 2)
        self.menu['postcommand'] = self.update
    
    # --------------------------------------------------------------------------
    # Update menu entries to list only spectra with the given dimension.
    #
    def update(self):
        
        entries = []
        self.remove_all_entries()
        
        for name in self.spectrum_names():
            spectrum = sputil.name_to_spectrum(name, self.session)
            if spectrum.dimension == self.dimension:
                self.add_entry(name)
                entries.append(name)
        
        if self.get() not in entries:
            if entries:
                self.set(entries[0])
            else:
                self.set("No spectrum")


# ==============================================================================
# An option menu for axis selection.
#
class axis_menu(axes.axis_menu):
    
    def __init__(self, parent, title, index):
        
        self.index = index
        self.spectrum = "No spectrum"
        
        tkutil.option_menu.__init__(self, parent, title, [])
        
        self.label.config(width = 3, anchor = 'e')
        self.menu.master.config(width = 6, anchor = 'w', highlightthickness = 0)
    
    # --------------------------------------------------------------------------
    # Update menu entries to list axes of the given spectrum.
    #
    def update(self, spectrum):
        
        if spectrum is not self.spectrum:
            self.spectrum = spectrum
            self.remove_all_entries()
            
            if spectrum:
                for i in range(spectrum.dimension):
                    self.add_entry(self.axis_text(i))
                self.set_axis(self.index)
                self.menu.master['state'] = 'normal'
            else:
                self.set("w%d ---" % (self.index+1))
                self.menu.master['state'] = 'disabled'


# ==============================================================================
# An array of color labeled radiobuttons.
# User can choose a color by clicking the respective button.
#
class color_picker:
    
    postcheck = None
    
    def __init__(self, parent, title):
        
        self.frame = Tkinter.Frame(parent)
        self.color_chosen = Tkinter.StringVar()
        
        label = Tkinter.Label(self.frame, text = title)
        label.grid(columnspan = 7, sticky = 'w')
        
        colors = ('red','green','blue','cyan','yellow','magenta','white')
        self.pickers = {}
        
        for i, color in enumerate(colors):
            
            picker = Tkinter.Radiobutton(self.frame, indicatoron = 0,
                                         fg = color, selectcolor = color,
                                         text = color[0].capitalize(),
                                         value = color, width = 2,
                                         variable = self.color_chosen,
                                         command = self.update_fg,
                                         offrelief = 'ridge',
                                         overrelief = 'raised')
            picker.grid(row = 1, column = i, padx = 2, pady = 4)
            self.frame.columnconfigure(i, weight = 1)
            
            self.pickers[color] = picker
    
    # --------------------------------------------------------------------------
    # When a button is selected, change its font color to black to keep
    # the caption visible. Reset color to original once deselected.
    #
    def update_fg(self):
        
        for color, picker in self.pickers.items():
            
            if color == self.color_chosen.get():
                picker['fg'] = 'black'
            else:
                picker['fg'] = color
        
        self.__class__.postcheck()
    
    # --------------------------------------------------------------------------
    #
    def get(self):
        return self.color_chosen.get()
    
    def set(self, color):
        self.pickers[color].invoke()


# ==============================================================================
# A table of spinboxs (2 per row) for tolerances setting.
#
class tol_setup:
    
    def __init__(self, parent, title, tol_max):
        
        self.frame = Tkinter.Frame(parent)
        
        for col in range(4):
            self.frame.columnconfigure(col, weight = 1)
        
        label = Tkinter.Label(self.frame, text = title)
        label.grid(columnspan = 4, sticky = 'w')
        
        self.tols = []
        
        for i, (axis, max_, unit) in enumerate(tol_max):
            
            tol_var = Tkinter.DoubleVar()
            row = 2 * (i // 2) + 1
            col = 2 * (i % 2)
            
            axis_label = Tkinter.Label(self.frame, text = axis)
            axis_label.grid(row = row, column = col)
            
            tol_box = Tkinter.Spinbox(self.frame, width = 5,
                                      from_ = 0, to = max_,
                                      increment = max_ / 20,
                                      textvariable = tol_var,
                                      state = 'readonly',
                                      readonlybackground = '')
            tol_box.grid(row = row + 1, column = col)
            
            unit_label = Tkinter.Label(self.frame, text = unit)
            unit_label.grid(row = row + 1, column = col + 1, sticky = 'w')
            
            self.tols.append(tol_var)
    
    # --------------------------------------------------------------------------
    #
    def get(self):
        return [tol.get() for tol in self.tols]
    
    def set(self, values):
        for tol, value in zip(self.tols, values):
            tol.set(value)
