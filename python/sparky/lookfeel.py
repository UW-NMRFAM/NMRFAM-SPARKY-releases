import colormap
import Tkinter
import tkFont
import os
import sparky
import platform
import tkutil
import sputil
import pyutil
import shutil
import tkMessageBox
import tkColorChooser

locales = ['[US] American English', 
           '[CN] Chinese by Huan Du (Kaifeng Hu group)',
           '[IN] Hindi by Adilakshimi Dwarasala (Woonghee Lee group)',
           '[IR] Farsi by Mehdi Rahimi (Woonghee Lee group)',
           '[KR] Korean by Woonghee Lee',
           '[VN] Vietnamese by Huong Thai-Thanh Nguyen (Woonghee Lee group)',
           ]

cfg_keys = ("!SPARKY_MOUSEWHEEL",
            "!SPARKY_HOMEDIRECTORY",
            "!SPARKY_LOCALE",
            "Sparky*background:",
            "Sparky*foreground:",
            "Sparky.normalFont:",
            "Sparky.fixedWidthFont:",
            "Sparky.scalableFont:",
            "Sparky.geometry:",
            "Sparky.text.height:",
            "Sparky.text.width:",
            "Sparky*View.xScale.height:",
            "Sparky*View.yScale.width:",
            "Sparky*View.xResPanel.height:",
            "Sparky*View.yResPanel.width:",
            "Sparky*View.xSlicePanel.height:",
            "Sparky*View.ySlicePanel.width:")
default_cfg = {"!SPARKY_MOUSEWHEEL": "1",
        "!SPARKY_HOMEDIRECTORY": '',
        "!SPARKY_LOCALE": '[US] American English',
        "Sparky*background:": "#d8f1dc",
        "Sparky*foreground:": "black",
        "Sparky.normalFont:": "-family sans -size 10",
        "Sparky.fixedWidthFont:": "-family monospace -size 10",
        "Sparky.scalableFont:": "-family sans -size 10",
        "Sparky.geometry:": "+30+80",
        "Sparky.text.height:": "15",
        "Sparky.text.width:": "60",
        "Sparky*View.xScale.height:": "35",
        "Sparky*View.yScale.width:": "50",
        "Sparky*View.xResPanel.height:": "100",
        "Sparky*View.yResPanel.width:": "100",
        "Sparky*View.xSlicePanel.height:": "100",
        "Sparky*View.ySlicePanel.width:": "100"}
if platform.system() == 'Windows':
  default_cfg["Sparky.fixedWidthFont:"] = "-family courier -size 10"
  

def read_config():
  szUserHome = os.path.expanduser("~")
  szConfig = os.path.join(szUserHome, ".sparky.cfg")
  szDefaultHome = os.path.join(szUserHome, "Sparky")
  cfg = default_cfg.copy()
  cfg['!SPARKY_HOMEDIRECTORY'] = szDefaultHome
  if os.path.exists(szConfig):
    f = open(szConfig, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
      sp = line.strip().split()
      if sp[0] == '!SPARKY_LOCALE':
        cfg['!SPARKY_LOCALE'] = pyutil.join(' ', sp[1:])
      elif sp[0] == 'Sparky*background:': 
        cfg['Sparky*background:'] = pyutil.join(' ', sp[1:])
      elif sp[0] == 'Sparky*foreground:': 
        cfg['Sparky*foreground:'] = pyutil.join(' ', sp[1:])
      elif sp[0] == 'Sparky.normalFont:': 
        cfg['Sparky.normalFont:'] = pyutil.join(' ', sp[1:])
      elif sp[0] == 'Sparky.fixedWidthFont:': 
        cfg['Sparky.fixedWidthFont:'] = pyutil.join(' ', sp[1:])
      elif sp[0] == 'Sparky.scalableFont:': 
        cfg['Sparky.scalableFont:'] = pyutil.join(' ', sp[1:])
      elif sp[0] == 'Sparky*geometry:': 
        cfg['Sparky*geometry:'] = pyutil.join(' ', sp[1:])
      elif sp[0] == 'Sparky.text.height:': 
        cfg['Sparky.text.height:'] = pyutil.join(' ', sp[1:])
      elif sp[0] == 'Sparky.text.width:': 
        cfg['Sparky.text.width:'] = pyutil.join(' ', sp[1:])
      elif sp[0] == 'Sparky*View.xScale.height:': 
        cfg['Sparky*View.xScale.height:'] = pyutil.join(' ', sp[1:])
      elif sp[0] == 'Sparky*View.yScale.width:': 
        cfg['Sparky*View.yScale.width:'] = pyutil.join(' ', sp[1:])
      elif sp[0] == 'Sparky*View.xResPanel.height:': 
        cfg['Sparky*View.xResPanel.height:'] = pyutil.join(' ', sp[1:])
      elif sp[0] == 'Sparky*View.yResPanel.width:': 
        cfg['Sparky*View.yResPanel.width:'] = pyutil.join(' ', sp[1:])
      elif sp[0] == 'Sparky*View.xSlicePanel.height:': 
        cfg['Sparky*View.xSlicePanel.height:'] = pyutil.join(' ', sp[1:])
      elif sp[0] == 'Sparky*View.ySlicePanel.width:': 
        cfg['Sparky*View.ySlicePanel.width:'] = pyutil.join(' ', sp[1:])
  return cfg

def write_config(cfg):
  lines = ''
  szUserHome = os.path.expanduser("~")
  szConfig = os.path.join(szUserHome, ".sparky.cfg")
  szDefaultHome = os.path.join(szUserHome, "Sparky")
  bSuccess = True
  try:
    for key in cfg_keys:
      values = cfg[key]
      lines = lines + key + ' ' + values + '\n'
  except:
    lines = ''
    for key in cfg_keys:
      values = default_cfg[key]
      if key == '!SPARKY_HOMEDIRECTORY': values = szDefaultHome
      lines = lines + key + ' ' + values + '\n'
    bSuccess = False
  f = open(szConfig, 'w')
  f.write(lines)
  f.close()
  return bSuccess

def get_sparkyhome():
  cfg = read_config()
  return cfg['!SPARKY_HOMEDIRECTORY']
# -----------------------------------------------------------------------------
def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
# -----------------------------------------------------------------------------
#
class look_and_feel_dialog(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
    self.session = session
    tmp_fntfam = tkFont.families()
    fntfam = []
    for fnt in tmp_fntfam: fntfam.append(fnt.replace(' ', ''))
    fntfam.sort()
    tkutil.Dialog.__init__(self, session.tk, 'Look and feel dialog')
    initcolors = list(colormap.supported_colors)
    colors = []
    for clr in initcolors:
      if ' ' not in clr:
        colors.append(clr)
    self.cfg = read_config()
    bgco = self.cfg['Sparky*background:']
    fgco = self.cfg['Sparky*foreground:']
    if not bgco in colors: colors.insert(0, bgco)
    if not fgco in colors: colors.insert(0, fgco)
    colors = f7(colors)

    #buttons
    self.br = tkutil.button_row(self.top,
         ('Default', self.default_cb),
         ('Apply', self.apply_cb),
         ('Cancel', self.cancel_cb),)
    self.br.frame.pack(side = 'top', anchor = 'w')
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')

    #background
    self.bg_om = tkutil.option_menu(self.top, "Background: ", colors, bgco, 
                                    alphabet = True)
    self.bg_om.add_entry('Custom', forceroot=True)
    self.bg_om.frame.pack(side = 'top', anchor = 'nw')
    self.bg_om.menu.bind("<<MenuSelect>>", self.update_color_cb)
    
    #foreground
    self.fg_om = tkutil.option_menu(self.top, "Foreground: ", colors, fgco, 
                                    alphabet = True)
    self.fg_om.frame.pack(side = 'top', anchor = 'nw')
    self.fg_om.add_entry('Custom', forceroot=True)
    self.fg_om.menu.bind("<<MenuSelect>>", self.update_color_cb)

    #locale
    self.lc_om = tkutil.option_menu(self.top, "Locale: ", locales, self.cfg['!SPARKY_LOCALE'])
    self.lc_om.frame.pack(side = 'top', anchor = 'nw')
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')

    #font
    nf = self.cfg['Sparky.normalFont:'].split()[1]
    fwf = self.cfg['Sparky.fixedWidthFont:'].split()[1]
    sf = self.cfg['Sparky.scalableFont:'].split()[1]
    nf_size = int(self.cfg['Sparky.normalFont:'].split()[3])
    fwf_size = int(self.cfg['Sparky.fixedWidthFont:'].split()[3])
    sf_size = int(self.cfg['Sparky.scalableFont:'].split()[3])

    # default font in case not exist
    dnf = default_cfg['Sparky.normalFont:'].split()[1]
    dfwf = default_cfg['Sparky.fixedWidthFont:'].split()[1]
    dsf = default_cfg['Sparky.scalableFont:'].split()[1]
    if not dnf in fntfam: fntfam.insert(1, dnf)
    if not dfwf in fntfam: fntfam.insert(1, dfwf)
    if not dsf in fntfam: fntfam.insert(1, dsf)

    fntfam = f7(fntfam)
    #normal
    self.nf_om = tkutil.option_menu(self.top, "Normal Font: ", fntfam, nf, 
                                    alphabet = True)
    self.nf_om.frame.pack(side = 'top', anchor = 'nw', fill='both', expand=1)
    self.nf_om.add_entry(nf, forceroot = True)
    if nf != dnf:
      self.nf_om.add_entry(dnf, forceroot = True)
    self.nf_sc = Tkinter.Scale(self.top, from_=7, to=30, orient='horizontal')
    self.nf_sc.pack(side = 'top', anchor = 'nw', fill='both', expand=1)
    self.nf_sc.set(nf_size)
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    #fixed width
    self.fwf_om = tkutil.option_menu(self.top, "Fixed Width Font: ", fntfam, 
                                    fwf, alphabet = True)
    self.fwf_om.frame.pack(side = 'top', anchor = 'nw', fill='both', expand=1)
    self.fwf_om.add_entry(fwf, forceroot = True)
    if fwf != dfwf:
      self.fwf_om.add_entry(dfwf, forceroot = True)
    self.fwf_sc = Tkinter.Scale(self.top, from_=7, to=30, orient='horizontal')
    self.fwf_sc.pack(side = 'top', anchor = 'nw', fill='both', expand=1)
    self.fwf_sc.set(fwf_size)
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    #scalable
    self.sf_om = tkutil.option_menu(self.top, "Scalable Font: ", fntfam, 
                                  sf, alphabet = True)
    self.sf_om.frame.pack(side = 'top', anchor = 'nw', fill='both', expand=1)
    self.sf_om.add_entry(sf, forceroot = True)
    if sf != dsf:
      self.sf_om.add_entry(dsf, forceroot = True)
    self.sf_sc = Tkinter.Scale(self.top, from_=7, to=30, orient='horizontal')
    self.sf_sc.pack(side = 'top', anchor = 'nw', fill='both', expand=1)
    self.sf_sc.set(sf_size)
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    #xscale height
    Tkinter.Label(self.top, text = 'XScale Height').pack()
    self.xh_sc = Tkinter.Scale(self.top, from_=20, to=250, orient='horizontal')
    self.xh_sc.pack(side = 'top', anchor = 'nw', fill='both', expand=1)
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    self.xh_sc.set(self.cfg['Sparky*View.xScale.height:'])
    #yscale width
    Tkinter.Label(self.top, text = 'YScale Width').pack()
    self.yw_sc = Tkinter.Scale(self.top, from_=20, to=150, orient='horizontal')
    self.yw_sc.pack(side = 'top', anchor = 'nw', fill='both', expand=1)
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    self.yw_sc.set(self.cfg['Sparky*View.yScale.width:'])
    #x resonance panel height
    Tkinter.Label(self.top, text = 'X Resonance Panel Height').pack()
    self.xrph_sc = Tkinter.Scale(self.top, from_=80, to=300, orient='horizontal')
    self.xrph_sc.pack(side = 'top', anchor = 'nw', fill='both', expand=1)
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    self.xrph_sc.set(self.cfg['Sparky*View.xResPanel.height:'])
    #y resonance panel width
    Tkinter.Label(self.top, text = 'Y Resonance Panel Width').pack()
    self.yrpw_sc = Tkinter.Scale(self.top, from_=80, to=300, orient='horizontal')
    self.yrpw_sc.pack(side = 'top', anchor = 'nw', fill='both', expand=1)
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    self.yrpw_sc.set(self.cfg['Sparky*View.yResPanel.width:'])
    #x slice panel height
    Tkinter.Label(self.top, text = 'X Slice Panel Height').pack()
    self.xsph_sc = Tkinter.Scale(self.top, from_=80, to=300, orient='horizontal')
    self.xsph_sc.pack(side = 'top', anchor = 'nw', fill='both', expand=1)
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    self.xsph_sc.set(self.cfg['Sparky*View.xSlicePanel.height:'])
    #y slice panel width
    Tkinter.Label(self.top, text = 'Y Slice Panel Width').pack()
    self.yspw_sc = Tkinter.Scale(self.top, from_=80, to=300, orient='horizontal')
    self.yspw_sc.pack(side = 'top', anchor = 'nw', fill='both', expand=1)
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    self.yspw_sc.set(self.cfg['Sparky*View.ySlicePanel.width:'])

  def update_color_cb(self, event):
    cl = self.bg_om.get()
    if cl == 'Custom':
      rgbTuplet, colorString = tkColorChooser.askcolor(parent=self.top, 
        title='Pick a background color', 
        initialcolor=self.cfg['Sparky*background:'])
      try:  
        cl2 = '#%02x%02x%02x' % (rgbTuplet[0], rgbTuplet[1], rgbTuplet[2])
      except:
        self.bg_om.set(self.cfg['Sparky*background:'])
        return
      self.bg_om.add_entry(cl2)
      self.bg_om.set(cl2) 
      self.bg_om.menubutton['bg'] = cl2
    else:
      self.bg_om.menubutton['bg'] = cl
    cl = self.fg_om.get()
    if cl == 'Custom':
      rgbTuplet, colorString = tkColorChooser.askcolor(parent=self.top, 
        title='Pick a foreground color', 
        initialcolor=self.cfg['Sparky*foreground:'])
      try:  
        cl2 = '#%02x%02x%02x' % (rgbTuplet[0], rgbTuplet[1], rgbTuplet[2])  
      except:
        self.fg_om.set(self.cfg['Sparky*foreground:'])
        return
      self.fg_om.add_entry(cl2)
      self.fg_om.set(cl2) 
      self.fg_om.menubutton['bg'] = cl2
    else:
      self.fg_om.menubutton['bg'] = cl

  def set_cfg(self, cfg):
    self.lc_om.set(cfg['!SPARKY_LOCALE'])
    self.bg_om.set(cfg['Sparky*background:'])
    self.fg_om.set(cfg['Sparky*foreground:'])
    nf = cfg['Sparky.normalFont:'].split()[1]
    fwf = cfg['Sparky.fixedWidthFont:'].split()[1]
    sf = cfg['Sparky.scalableFont:'].split()[1]
    nf_size = int(cfg['Sparky.normalFont:'].split()[3])
    fwf_size = int(cfg['Sparky.fixedWidthFont:'].split()[3])
    sf_size = int(cfg['Sparky.scalableFont:'].split()[3])

    self.nf_om.set(nf)
    self.nf_sc.set(nf_size)
    self.fwf_om.set(fwf)
    self.fwf_sc.set(fwf_size)
    self.sf_om.set(sf)
    self.sf_sc.set(sf_size)
    self.xh_sc.set(int(cfg['Sparky*View.xScale.height:']))
    self.yw_sc.set(int(cfg['Sparky*View.yScale.width:']))
    self.xrph_sc.set(int(cfg['Sparky*View.xResPanel.height:']))
    self.yrpw_sc.set(int(cfg['Sparky*View.yResPanel.width:']))
    self.xsph_sc.set(int(cfg['Sparky*View.xSlicePanel.height:']))
    self.yspw_sc.set(int(cfg['Sparky*View.ySlicePanel.width:']))

  def default_cb(self):
    self.set_cfg(default_cfg.copy())
    
  def apply_cb(self):
    # apply config
    cfg = read_config()
    bgco = self.bg_om.get()
    cfg['Sparky*background:'] = bgco
    fgco = self.fg_om.get()
    cfg['Sparky*foreground:'] = fgco
    tmp = '-family %s -size %d' % (self.nf_om.get(), self.nf_sc.get())
    cfg['Sparky.normalFont:'] = tmp
    tmp = '-family %s -size %d' % (self.fwf_om.get(), self.fwf_sc.get())
    cfg['Sparky.fixedWidthFont:'] = tmp
    tmp = '-family %s -size %d' % (self.sf_om.get(), self.sf_sc.get())
    cfg['Sparky.scalableFont:'] = tmp
    cfg['Sparky*View.xScale.height:'] = str(self.xh_sc.get())
    cfg['Sparky*View.yScale.width:'] = str(self.yw_sc.get())
    cfg['Sparky*View.xResPanel.height:'] = str(self.xrph_sc.get())
    cfg['Sparky*View.yResPanel.width:'] = str(self.yrpw_sc.get())
    cfg['Sparky*View.xSlicePanel.height:'] = str(self.xsph_sc.get())
    cfg['Sparky*View.ySlicePanel.width:'] = str(self.yspw_sc.get())
    cfg['!SPARKY_LOCALE'] = self.lc_om.get()
    locale_file = os.path.join(sparky.installation_path(), 'locale', 'sparky_locale_%s' % (cfg['!SPARKY_LOCALE'][1:3]))
    user_locale_file = os.path.join(os.path.expanduser("~"), '.sparky.locale')
    try:
      shutil.copyfile(locale_file, user_locale_file)
    except:
      pass
    write_config(cfg)
    tkMessageBox.showinfo('Setting changed', \
                          'Changes will be applied in next run.')
    self.close_cb()
    pass

  def cancel_cb(self):
    # revert config
    write_config(self.cfg)
    self.close_cb()
    pass  

# -----------------------------------------------------------------------------
#
def show_look_and_feel(session):
  sputil.the_dialog(look_and_feel_dialog, session).show_window(1)

from bidi.algorithm import get_display
from arabic_reshaper import ArabicReshaper
reshaper = ArabicReshaper()

def reshape_arabic_label(lbl):
  reshaped_lbl = reshaper.reshape(lbl)
  bidi_lbl = get_display(reshaped_lbl)
  return bidi_lbl

def bidi_resource_fix(session):
  s = session
  szUserHome = os.path.expanduser("~")
  szLocale = os.path.join(szUserHome, ".sparky.locale")
  if not os.path.exists(szLocale): 
    return # failed to find locale file

  import codecs
  f = codecs.open(szLocale, encoding='utf-8', mode = 'r')
  #f = open(szLocale, 'r')
  lines = f.readlines()
  f.close()

  for line in lines:
    ln = line.strip()
    if len(ln) < 7: continue
    if ln[:6] != 'Sparky': continue
    colonidx = ln.find(':')
    if colonidx < 7 or len(ln) < colonidx+1: continue
    optname = ln[:colonidx]
    optvalue = ln[colonidx+1:]
    bi_optvalue = reshape_arabic_label(optvalue)
    tkutil.tk_call(s.tk, 'option', 'add', optname, bi_optvalue)

def handle_arabic(session):
  cfg = read_config()
  s = session
  # arabic, farsi
  # current made forms and menus first
  if cfg['!SPARKY_LOCALE'][1:3] in ['IR']:
    w_list = list(tkutil.tk_call(s.tk, 'winfo', 'children', '.'))
    for item in w_list:
      w_list2 = list(tkutil.tk_call(s.tk, 'winfo', 'children', str(item)))
      w_list.extend(w_list2)

    for w in w_list:
      if str(w).find('.menuBar') != -1:
        try:
          last_index = tkutil.tk_call(s.tk, str(w), 'index', 'end')
          for i in range(last_index+1):
            try:
              lbl = tkutil.tk_call(s.tk, str(w), 'entrycget', str(i), '-label')
              bidi_lbl = reshape_arabic_label(lbl)
              tkutil.tk_call(s.tk, str(w), 'entryconfigure', str(i), '-label', \
                            bidi_lbl)
            except:
              continue
        except:
          pass
      try:
        lbl = tkutil.tk_call(s.tk, str(w), 'cget', '-text')
        bidi_lbl = reshape_arabic_label(lbl)
        tkutil.tk_call(s.tk, str(w), 'configure', '-text', bidi_lbl)
      except:
        pass
      try:
        lbl = tkutil.tk_call(s.tk, str(w), 'cget', '-label')
        bidi_lbl = reshape_arabic_label(lbl)
        tkutil.tk_call(s.tk, str(w), 'configure', '-label', bidi_lbl)
      except:
        pass
    # we need to fix resource as well. How?
    bidi_resource_fix(s)
