import sputil
import tkutil
import nmrfam

nmrfam_protein_nmr_lectures =   (("NMRFAM-SPARKY basics by Grant Hisao", 
    "https://youtu.be/BYSJceYBwT8?t=2883"), 
  ("Backbone assignment by Szymon Ciesielski", 
    "https://youtu.be/BYSJceYBwT8?t=7782"), 
  ("Aliphatic sidechain assignment using transfer-and-simulate tool by Marco Tonelli", 
    "https://youtu.be/MFfmpXCB5Ms?t=2048"), 
  ("Aromatic sidechain assignment using transfer-and-simulate tool by Marco Tonelli", 
    "https://youtu.be/MFfmpXCB5Ms?t=23555"), 
  ("Automated peak picking strategy using APES by Woonghee Lee", 
    "https://youtu.be/roZxxhx_epo?t=2550"), 
  ("Automated assignment using I-PINE by Kumaran Baskaran", 
    "https://youtu.be/roZxxhx_epo?t=8251"), 
  ("Chemical shift validation using ARECA by Valeriu Bortnov", 
    "https://youtu.be/roZxxhx_epo?t=14889"), 
  ("Structure calculation basics by Gabriel Cornilescu", 
    "https://youtu.be/roZxxhx_epo?t=18405"), 
  ("TALOS-N hands-on by Gabriel Cornilescu", 
    "https://youtu.be/roZxxhx_epo?t=21748"), 
  ("Automated structure calculation using PONDEROSA-C/S by Gabriel Cornilescu", 
    "https://youtu.be/roZxxhx_epo?t=26096"), 
  ("Structural restraints validation using PONDEROSA-C/S by Valeriu Bortnov", 
    "https://youtu.be/XPoEI0txsxY?t=1119"), 
  ("Nuclear Overhauser Effect (NOE) basics by Milo Westler", 
    "https://youtu.be/XPoEI0txsxY?t=12550"), 
  ("Fully automated assignments and structure calculation using I-PINE by Woonghee Lee", 
    "https://youtu.be/XPoEI0txsxY?t=13980"), 
  ("Structure validation using MolProbity by Kumaran Baskaran", 
    "https://youtu.be/zk_inVBqj7I?t=1829"), 
  ("Data deposition to BMRB by Kumaran Baskaran", 
    "https://youtu.be/zk_inVBqj7I?t=7202"))

class protein_nmr_lecture_dialog(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
    self.session = session
    tkutil.Dialog.__init__(self, session.tk, 'NMRFAM-SPARKY Basics')
    vlist = tkutil.scrolling_list(self.top, '* Double-click to watch a lecture video\n' + \
                                    ' given by NMRFAM staffs', 10, True)
    vlist.listbox['selectmode'] = 'single'
    vlist.frame.pack(side='top', fill = 'both', expand = 1)
    vlist.listbox.bind('<Double-Button-1>', self.watch_cb)
    self.vlist = vlist

    import tkFont
    tmp_fntfam = tkFont.families()
    suggested_fonts = ['Arial', 'NotoSans', 'Ubuntu', 'SegoeUI', 'Helvetica', 
                      'Calibri', 'Verdana', 'DejaVuSans', 'FreeSans']
    for fnt in suggested_fonts:
      if fnt in tmp_fntfam:
        vlist.listbox['font'] = (fnt, 10)
        vlist.heading['font'] = (fnt, 10)
        break
    self.update_vlist()
    vlist.listbox['height'] = min(max(len(self.vlist.line_data), 5), 30)
    
  def update_vlist(self):
    self.vlist.clear()
    max_width = 30
    for i in range(len(nmrfam_protein_nmr_lectures)):
      video_name, video_url = nmrfam_protein_nmr_lectures[i][0], \
                              nmrfam_protein_nmr_lectures[i][1]
      self.vlist.append(video_name, [video_name, video_url])
      max_width = max(len(video_name), max_width)
    self.vlist.listbox['width'] = max_width
  def watch_cb(self, event):
    data_list = self.vlist.selected_line_data()
    if len(data_list) == 0: return
    nmrfam.openURL(data_list[0][1])

def show_protein_nmr_lecture_dialog(session):
  sputil.the_dialog(protein_nmr_lecture_dialog, session).show_window(1)
