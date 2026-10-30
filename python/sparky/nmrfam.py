# -----------------------------------------------------------------------------
# About NMRFAM-SPARKY.....
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Jan 10, 2020
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
#
import string

import sparky
import sputil
import tkutil
import tkMessageBox
import os
import os.path
import platform
import webbrowser

# -----------------------------------------------------------------------------
#
def check_install_date(sparky_rel_file):
  import time
  import os.path
  try:
    sparky_file = os.path.realpath(sparky_rel_file)
    inst_sec = os.path.getmtime(sparky_file)
    sparky_year = time.gmtime(inst_sec).tm_year
    sparky_mon = time.gmtime(inst_sec).tm_mon
    sparky_mday = time.gmtime(inst_sec).tm_mday  
    return 'Installed on %d/%d/%d\n' % (sparky_mon, sparky_mday, sparky_year)        
  except:
    return 'Not detected\n'
  return 'Not detected\n'
# -----------------------------------------------------------------------------
#
def get_nmrfam_sparky_root_path(session):
  this_script_path = os.path.realpath(__file__) # /nmrfam-sparky-linux/python/sparky/nmrfam.py
  return os.path.dirname(os.path.dirname(os.path.dirname(this_script_path)))    # /nmrfam-sparky-linux
# -----------------------------------------------------------------------------
#
def get_nmrfam_sparky_ground_path(session):
  this_script_path = os.path.realpath(__file__) # /nmrfam-sparky-linux/python/sparky/nmrfam.py
  return os.path.dirname(get_nmrfam_sparky_root_path(session))    # /
# -----------------------------------------------------------------------------
#
def get_nmrfam_sparky_bin_path(session):
  nmrfam_sparky_root_path = get_nmrfam_sparky_root_path(session)
  return os.path.join(nmrfam_sparky_root_path, 'bin')   # /nmrfam-sparky-linux/bin
# -----------------------------------------------------------------------------
#
def get_nmrfam_sparky_lookup_path(session):
  paths = os.environ["PATH"].split(os.pathsep)
  paths.append(get_nmrfam_sparky_bin_path(session))
  paths.append(".")
  paths.append(os.path.expanduser("~"))
  paths.append(get_nmrfam_sparky_ground_path(session))
  if platform.system() == 'Darwin':
    paths.append(os.path.dirname(os.path.dirname(get_nmrfam_sparky_ground_path(session))))
  return paths
# -----------------------------------------------------------------------------
#
def run_ponderosa_client(session):
  paths = get_nmrfam_sparky_lookup_path(session)
  for p in paths:
    if os.path.exists(os.path.join(p, 'PonderosaClient')):
      os.system(os.path.join(p, 'PonderosaClient'))
      return
    elif os.path.exists(os.path.join(p, 'PonderosaClient.app')):
      os.system('open ' + os.path.join(p, 'PonderosaClient.app'))
      return      
    elif os.path.exists(os.path.join(p, 'PonderosaClient.exe')):
      os.system(os.path.join(p, 'PonderosaClient.exe'))
      return
  mac_path='/Applications/PonderosaClient.app/Contents/MacOS/PonderosaClient'
  if os.path.exists(mac_path):
   os.system(mac_path)
   return
  tkMessageBox.showerror("Connection Error", "PonderosaClient is not in PATH. " + \
                    "Tip: you can place the program in your home directory as well.") 
  if tkMessageBox.askokcancel('Installation','Do you want to download the program?'):  
    webbrowser.open('http://pine.nmrfam.wisc.edu/download_packages.html')  
# -----------------------------------------------------------------------------
#
def run_stride(session):
  webbrowser.open('http://webclu.bio.wzw.tum.de/cgi-bin/stride/stridecgi.py')
# -----------------------------------------------------------------------------
#
def run_psipred(session):
  webbrowser.open('http://bioinf.cs.ucl.ac.uk/psipred_new/')
# -----------------------------------------------------------------------------
#
def run_pine2sparky(session):
  # find if any spectrum is opened.
  if session.project != None and len(session.project.spectrum_list()) != 0:
    tkMessageBox.showerror("PROJECT Error", "Please close your project before running pine2sparky.")        
  paths = get_nmrfam_sparky_lookup_path(session)
  for p in paths:
    if os.path.exists(os.path.join(p, 'pine2sparky')):
      os.system(os.path.join(p, 'pine2sparky'))
      return
    elif os.path.exists(os.path.join(p, 'pine2sparky.app')):
      os.system(os.path.join(p, 'open pine2sparky.app'))
      return      
    elif os.path.exists(os.path.join(p, 'pine2sparky.exe')):
      os.system(os.path.join(p, 'pine2sparky.exe'))
      return
  mac_path='/Applications/pine2sparky.app/Contents/MacOS/pine2sparky'
  if os.path.exists(mac_path):   
    os.system(mac_path)
    return
  mac_path=mac_path+'_mac'
  if os.path.exists(mac_path):                                               
    os.system(mac_path)
    return
  mac_path='/Applications/nmrfam-sparky-mac/pine2sparky.app/Contents/MacOS/pine2sparky'
  if os.path.exists(mac_path):   
    os.system(mac_path)
    return
  mac_path=mac_path+'_mac'
  if os.path.exists(mac_path):                                               
    os.system(mac_path)
    return        
  tkMessageBox.showerror("Connection Error", "pine2sparky is not in PATH. " + \
                      "Tip: you can place the program in your home directory as well.")    
  if tkMessageBox.askokcancel('Installation','Do you want to download the program?'):  
    webbrowser.open('http://pine.nmrfam.wisc.edu/download_packages.html') 
# -----------------------------------------------------------------------------
#
def run_pipe2ucsf(session):
  # find if any spectrum is opened.
  paths = get_nmrfam_sparky_lookup_path(session)
  for p in paths:
    if os.path.exists(os.path.join(p, 'easy_pipe2ucsf')):
      os.system(os.path.join(p, 'easy_pipe2ucsf'))
      return
    elif os.path.exists(os.path.join(p, 'easy_pipe2ucsf.app')):
      os.system('open ' + os.path.join(p, 'easy_pipe2ucsf.app'))
      return      
    elif os.path.exists(os.path.join(p, 'easy_pipe2ucsf.exe')):
      os.system(os.path.join(p, 'easy_pipe2ucsf.exe'))
      return
  mac_path='/Applications/easy_pipe2ucsf.app/Contents/MacOS/easy_pipe2ucsf'
  if os.path.exists(mac_path):   
    os.system(mac_path)
    return
  mac_path='/Applications/nmrfam-sparky-mac/easy_pipe2ucsf.app/Contents/MacOS/easy_pipe2ucsf'
  if os.path.exists(mac_path):   
    os.system(mac_path)
    return    
  tkMessageBox.showerror("Connection Error", "easy_pipe2ucsf is not in PATH. " + \
                  "Tip: you can place the program in your home directory as well.")    
# -----------------------------------------------------------------------------
#
def run_bruk2ucsf(session):
  # find if any spectrum is opened.
  paths = get_nmrfam_sparky_lookup_path(session)
  for p in paths:
    if os.path.exists(os.path.join(p, 'easy_bruk2ucsf')):
      os.system(os.path.join(p, 'easy_bruk2ucsf'))
      return
    elif os.path.exists(os.path.join(p, 'easy_bruk2ucsf.exe')):
      os.system(os.path.join(p, 'easy_bruk2ucsf.exe'))
      return      
    elif os.path.exists(os.path.join(p, 'easy_bruk2ucsf.app')):
      os.system('open ' + os.path.join(p, 'easy_bruk2ucsf.app'))
      return
  mac_path='/Applications/easy_bruk2ucsf.app/Contents/MacOS/easy_bruk2ucsf'
  if os.path.exists(mac_path):   
    os.system(mac_path)
    return
  mac_path='/Applications/nmrfam-sparky-mac/easy_bruk2ucsf.app/Contents/MacOS/easy_bruk2ucsf'
  if os.path.exists(mac_path):   
    os.system(mac_path)
    return    
  tkMessageBox.showerror("Connection Error", "easy_bruk2ucsf is not in PATH. " + \
                  "Tip: you can place the program in your home directory as well.")   
# -----------------------------------------------------------------------------
#
def run_ucsfdata(session):
  # find if any spectrum is opened.
  paths = get_nmrfam_sparky_lookup_path(session)
  for p in paths:
    if os.path.exists(os.path.join(p, 'easy_ucsfdata')):
      os.system(os.path.join(p, 'easy_ucsfdata'))
      return
    elif os.path.exists(os.path.join(p, 'easy_ucsfdata.exe')):
      os.system(os.path.join(p, 'easy_ucsfdata.exe'))
      return      
    elif os.path.exists(os.path.join(p, 'easy_ucsfdata.app')):
      os.system('open ' + os.path.join(p, 'easy_ucsfdata.app'))
      return
  mac_path='/Applications/nmrfam-sparky-mac/easy_ucsfdata.app/Contents/MacOS/easy_ucsfdata'
  if os.path.exists(mac_path):   
    os.system(mac_path)
    return    
  mac_path='/Applications/easy_ucsfdata.app/Contents/MacOS/easy_ucsfdata'
  if os.path.exists(mac_path):   
    os.system(mac_path)
    return
  tkMessageBox.showerror("Connection Error", "easy_bruk2ucsf is not in PATH. " + \
                  "Tip: you can place the program in your home directory as well.")   
# -----------------------------------------------------------------------------
#
def run_npdplot(session):
  # find if any spectrum is opened.
  paths = get_nmrfam_sparky_lookup_path(session)
  paths.append('/Applications/nmrfam-sparky-mac/ndpplot.app/Contents/MacOS')

  import subprocess
  for p in paths:
    if os.path.exists(os.path.join(p, 'ndpplot')):
      #os.system(os.path.join(p, 'npdplot'))
      #if p.find('ndpplot.app') != -1:
      #  subprocess.Popen(['open', os.path.join(p, 'ndpplot')])
      #else:
      subprocess.Popen([os.path.join(p, 'ndpplot')])            
      return
    elif os.path.exists(os.path.join(p, 'ndpplot.exe')):
      #os.system(os.path.join(p, 'npdplot.exe'))
      subprocess.Popen([os.path.join(p, 'ndpplot.exe')])      
      return      
    #elif os.path.exists(os.path.join(p, 'ndpplot.app')):
      #os.system('open ' + os.path.join(p, 'npdplot.app'))
    #  subprocess.Popen(['open', os.path.join(p, 'ndpplot.app')])      
    #  return
  #mac_path='/Applications/nmrfam-sparky-mac/ndpplot.app/Contents/MacOS/ndpplot'
  #if os.path.exists(mac_path):   
    #os.system(mac_path)
  #  subprocess.Popen(['open', '/Applications/nmrfam-sparky-mac/ndpplot.app'])    
  #  return    
  #mac_path='/Applications/nmrfam-sparky-mac/ndpplot.app/Contents/MacOS/npdplot'
  #if os.path.exists(mac_path):   
    #os.system(mac_path)
  #  subprocess.Popen(['open', '/Applications/nmrfam-sparky-mac/ndpplot.app'])    
  #  return      
  #mac_path='/Applications/ndpplot.app/Contents/MacOS/npdplot'
  #if os.path.exists(mac_path):   
    #os.system(mac_path)
  #  subprocess.Popen(['open', '/Applications/ndpplot.app'])
  #  return
  tkMessageBox.showerror("Connection Error", 
    "ndpplot is not in PATH. Tip: you can place the program in your home directory as well.")  
# -----------------------------------------------------------------------------
#
def run_ndpplot(session):
  run_npdplot(session)
# -----------------------------------------------------------------------------
#
def run_pymol(session, pdb_path, verbose=True):
  real_pdb_path = os.path.realpath(pdb_path)
  pdb_dir = os.path.dirname(real_pdb_path)
  pdb_file = os.path.basename(real_pdb_path)
  if not os.path.exists(real_pdb_path):
    if verbose:
      tkMessageBox.showerror('Error', \
          'PDB file not found.' % (real_pdb_path))
    return False

  import subprocess
  paths = get_nmrfam_sparky_lookup_path(session)
    # pymol, pymol.app blah blah
  paths.insert(0, '/Applications/PyMOL.app/Contents/MacOS')
  paths.insert(1, '/Applications/MacPyMOL.app/Contents/MacOS')
  paths.insert(2, '/Applications/MacPyMOLX11Hybrid.app/Contents/MacOS')
  paths.insert(3, 'C:\\Program Files\\PyMOL')
  paths.insert(4, 'C:\\Program Files (x86)\\PyMOL')
  paths.insert(5, 'C:\\Python27')
  paths.insert(6, 'C:\\Python38')
  exe_names = ['pymol', 'PyMOL', 'MacPyMOL', 'PyMOL.exe', 'pymol.exe', 
              'Python38\\PyMOL.exe', 'Python27\\PyMOL.exe']
  for i in range(len(paths)):
    p = paths[i]
    for exe in exe_names:
      check_path = os.path.join(p, exe)
      if os.path.exists(check_path):
        if i < 2: # mac
          #subprocess.Popen(['open', check_path, 'chesca.pdb'], \
          #                cwd=self.chesca_job_dir)
          check_path2 = 'cd %s; %s %s' % (pdb_dir, check_path, pdb_file) 
          subprocess.Popen([check_path2], \
                          cwd=pdb_dir)
        else:
          subprocess.Popen([check_path, pdb_file], cwd=pdb_dir)                
        return True
  if verbose:
    tkMessageBox.showwarning('PyMOL not found', 
      'PyMOL is not installed or not in environment path. Please run it manually.')
  return False

  
# -----------------------------------------------------------------------------
#   
def run_nessy(session):
  # find if any spectrum is opened.
  paths = get_nmrfam_sparky_lookup_path(session)
  import subprocess
  for p in paths:
    if os.path.exists(os.path.join(p, 'nessy')):
      subprocess.Popen([os.path.join(p, 'nessy')])            
      return
    elif os.path.exists(os.path.join(p, 'nessy-master/nessy')):  
      subprocess.Popen([os.path.join(p, 'nessy-master/nessy')])            
      return    
    elif os.path.exists(os.path.join(p, 'nessy.bat')):
      #os.system(os.path.join(p, 'npdplot.exe'))
      subprocess.Popen([os.path.join(p, 'nessy.bat')])      
      return    
    elif os.path.exists(os.path.join(p, 'nessy-master/nessy.bat')):  
      subprocess.Popen([os.path.join(p, 'nessy-master/nessy.bat')])            
      return            
    elif os.path.exists(os.path.join(p, 'nessy.sh')):
      subprocess.Popen(['open', os.path.join(p, 'nessy.sh')])      
      return
    elif os.path.exists(os.path.join(p, 'nessy-master/nessy.sh')):
      subprocess.Popen(['open', os.path.join(p, 'nessy-mater/nessy.sh')])
      return      
  tkMessageBox.showerror("Connection Error", "nessy is not in PATH. " + \
                "Tip: you can place the program in your home directory as well.")
# -----------------------------------------------------------------------------
# changed to support .sparky.cfg
def change_sparkyhome(session):
  options = {}
  options['title'] = 'Select a directory to set as SPARKYHOME.'
  import lookfeel
  options['initialdir'] = lookfeel.get_sparkyhome()
  import tkFileDialog
  path = tkFileDialog.askdirectory(**options)
  if (path) and (os.path.isdir(path)):
    cfg = lookfeel.read_config()
    cfg['!SPARKY_HOMEDIRECTORY'] = path
    os.environ['SPARKYHOME'] = path
    lookfeel.write_config(cfg)
    #tkMessageBox.showinfo('SPARKYHOME', 'SPARKYHOME has been changed. It will affect after next run.')
    proj_dir = os.path.join(path, 'Projects')
    save_dir = os.path.join(path, 'Save')
    list_dir = os.path.join(path, 'Lists')    
    
    if not os.path.exists(proj_dir):
      #result =  tkMessageBox.askyesno("New directory", "Do you want to create Project directories?")
      #if result is True:
      try:
        if not os.path.exists(proj_dir):
          os.mkdir(proj_dir, 0755)
      except:
        tkMessageBox.showinfo('Error', 'Failed to create %s.' % (proj_dir) )
      try:                    
        if not os.path.exists(save_dir):
          os.mkdir(save_dir, 0755)
      except:
        tkMessageBox.showinfo('Error', 'Failed to create %s.' % (save_dir) )
      try:                        
        if not os.path.exists(list_dir):
          os.mkdir(list_dir, 0755)            
      except:
        tkMessageBox.showinfo('Error', 'Failed to create %s.' % (list_dir) )
    tkMessageBox.showinfo('SPARKYHOME', 'SPARKYHOME has been changed. '
          + 'Please restart the program.')
    return
  tkMessageBox.showinfo('SPARKYHOME', 'SPARKYHOME has not been changed.')    
  
# -----------------------------------------------------------------------------
#    
def retrieve_nmrfam_news(news_file):
  try:
    import urllib2
  except:
    return ''
  nmrfam_news_url = 'http://pine.nmrfam.wisc.edu/nmrfam_news.txt'
  try: 
    nmrfam_news = urllib2.urlopen(nmrfam_news_url, timeout=2)
    your_build = check_install_date(__file__)
    msg =  nmrfam_news.read()
    msg += your_build
  except:
    return ''
  return msg
# -----------------------------------------------------------------------------
#
def import_reference_view(session):
  import errno
  import shutil
  
  # copy ucsf and save into
  ucsf_list = ['ref_13C_empty.ucsf', 'ref_13C_bb_empty.ucsf', 'ref_1H_empty.ucsf']
  save_list = ['ref_13C.save', 'ref_1H.save', 'ref_13C_backbone.save']
  
  save_path_list = []

  ref_dir = os.path.join(sparky.installation_path(), session.project.sparky_directory, 'Ref')  
  if not os.path.exists(ref_dir):
    try:
      os.makedirs(ref_dir)
    except OSError as exception:
      if exception.errno != errno.EEXIST:
        tkMessageBox.showerror("Error", ref_dir + " could not be generated.")
        return
          
  for i in range(len(ucsf_list)):
    ucsf_path = os.path.join(sparky.installation_path(), 'example', 'data', ucsf_list[i])
    save_path = os.path.join(sparky.installation_path(), 'example', 'Save', save_list[i])
    
    ucsf_path2 = os.path.join(ref_dir, ucsf_list[i])
    save_path2 = os.path.join(ref_dir, save_list[i])    
    save_path_list.append(save_path2)
    
    try:
      shutil.copyfile(ucsf_path, ucsf_path2)
      shutil.copyfile(save_path, save_path2)
    except OSError as exception:
      if exception.errno != errno.EEXIST:
        tkMessageBox.showerror("Error", "Reference could not be generated.")
        return      
    # modify save file
    f = open(save_path2, 'r')
    lines = f.readlines()
    f.close()
  
    f = open(save_path2, 'w')
    for line in lines:
      if line.find('pathname'):
        f.write(line)
        continue
      new_line = line.replace('../data/','../Ref/')
      f.write(new_line)  
    f.close()
  
  # open spectra
  for save_path in save_path_list:
    session.open_file(save_path)    


# -----------------------------------------------------------------------------
#
def deposit_data(session):
  tkMessageBox.showinfo("Deposit Chemical Shifts", "BMRB deposition page will be opened. You can make an acceptable chemical shift file by two-letter-code 'es'.")
  webbrowser.open('http://deposit.bmrb.wisc.edu/')
# -----------------------------------------------------------------------------
#
def go_ponderosamodel(session):
  webbrowser.open('http://ponderosa.nmrfam.wisc.edu/model.html')  
# -----------------------------------------------------------------------------
#
def go_haddock(session):
  webbrowser.open('http://haddock.science.uu.nl/services/HADDOCK2.2/haddock.php')    
# -----------------------------------------------------------------------------
#
def sparkyforum(session):
  webbrowser.open('https://groups.google.com/forum/#!forum/nmr-sparky')        
# -----------------------------------------------------------------------------
#
def about_pine(session):
  webbrowser.open('http://pine.nmrfam.wisc.edu')
# -----------------------------------------------------------------------------
#
def about_lacs(session):
  webbrowser.open('http://pine.nmrfam.wisc.edu/LACS')  
# -----------------------------------------------------------------------------
#
def about_areca(session):
  webbrowser.open('http://areca.nmrfam.wisc.edu')  
# -----------------------------------------------------------------------------
#
def about_pinesparky(session):
  webbrowser.open('http://pine.nmrfam.wisc.edu/PINE-SPARKY')
# -----------------------------------------------------------------------------
#
def about_pecan(session):
  webbrowser.open('http://pine.nmrfam.wisc.edu/PECAN')  
# -----------------------------------------------------------------------------
#
def about_nmrfam(session):
  webbrowser.open('http://www.nmrfam.wisc.edu')
# -----------------------------------------------------------------------------
#
def about_nmrfamsparky(session):
  webbrowser.open('http://www.nmrfam.wisc.edu/nmrfam-sparky-distribution.htm')
# -----------------------------------------------------------------------------
#
def videotutorial_nmrfam(session):
  webbrowser.open('https://www.youtube.com/playlist?list=PLmYqoarOFAZ-aInZ5uM2pV63e7yMSHSuZ')
# -----------------------------------------------------------------------------
#
def download_nmrfam(session):
  webbrowser.open('http://pine.nmrfam.wisc.edu/download_packages.html')  
# -----------------------------------------------------------------------------
#
def about_ponderosa(session):
  webbrowser.open('http://ponderosa.nmrfam.wisc.edu')
# -----------------------------------------------------------------------------
#
def about_bmrb(session):
  webbrowser.open('http://bmrb.wisc.edu')  
# -----------------------------------------------------------------------------
#
def about_shiftx2(session):
  webbrowser.open('http://www.shiftx2.ca')
# -----------------------------------------------------------------------------
#
def about_SCAssign(session):
  #webbrowser.open('http://yangdw.science.nus.edu.sg/Software&Scripts/SCAssign/index.html')
  webbrowser.open('http://blog.nus.edu.sg/yang/software/scassign/')  
# -----------------------------------------------------------------------------
#
def about_connjur(session):
  webbrowser.open('http://connjur.uchc.edu')    
# -----------------------------------------------------------------------------
#
def about_ncidpassign(session):
  webbrowser.open('http://nmr.chem.rug.nl/press/?page_id=39')    
# -----------------------------------------------------------------------------
#
def about_S3EPY(session):
  webbrowser.open('http://www.ncbr.muni.cz/s3epy/')    
# -----------------------------------------------------------------------------
#
def about_pacsy(session):
  webbrowser.open('http://pacsy.nmrfam.wisc.edu')      
 
# -----------------------------------------------------------------------------
#
def about_nef(session):
  webbrowser.open('http://www.nature.com/nsmb/journal/v22/n6/full/nsmb.3041.html')        
# -----------------------------------------------------------------------------
#
def about_rnapairs(session):
  webbrowser.open('http://pine.nmrfam.wisc.edu/RNA/')    
# -----------------------------------------------------------------------------
#
def about_rnaellipse(session):
  webbrowser.open('http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3794610/')
# -----------------------------------------------------------------------------
#
def openURL(url):
  webbrowser.open(url)
# -----------------------------------------------------------------------------
#
citation_dict = {
      'APES': """
Expert Rev Proteomics. 2008 Aug;5(4):589-601.
Structural proteomics by NMR spectroscopy.
Shin J, Lee W, Lee W.      
        """,
      'ARECA': """
J Biomol NMR, 2016 Jan;64(1):17-25
Probabilistic validation of protein NMR chemical shift assignments.
Dashti H et al.
        """,
      'CS-ROSETTA': """
Proc Natl Acad Sci U S A. 2008 Mar 25;105(12):4685-90.
Consistent blind protein structure generation from NMR chemical shift data.
Shen Y, Lange O, Delaglio F, Rossi P, Aramini JM, Liu G, Eletsky A, Wu Y, 
Singarapu KK, Lemak A, Ignatchenko A, Arrowsmith CH, Szyperski T, 
Montelione GT, Baker D, Bax A.    
        """,
      'GETSBY': """
Expert Rev Proteomics. 2008 Aug;5(4):589-601.
Structural proteomics by NMR spectroscopy.
Shin J, Lee W, Lee W.       
      
Lee W, Lee W. 
Method to predict protein secondary structure using NMR spectroscopy. 
The Korean Intellectual Property Office. 2009 Mar 16. Reg. No.: 1008899400000
        """,
        'I-PINE web server': """
Journal of Biomolecular NMR. 2019 June; 73(5): 213-222
I-PINE web server: an integrative probabilistic NMR assignment system for proteins
Lee W, Bahrami A, Dashti H, Eghbalnia HR, Tonelli M, Westler WM, Markley JL. 
        """,
      'LACS': """
J Biomol NMR, 2005 May;32(1):13-22.
Linear analysis of carbon-13 chemical shift differences and its application 
to the detection and correction of errors in referencing and 
spin system identifications.
Wang L, Eghbalnia HR, Bahrami A, Markley JL    
        """,
      'ncIDP-ASSIGN': """
Bioinformatics. 2011 Apr 1;27(7):1039-40.
ncIDP-assign: a SPARKY extension for the effective NMR assignment of 
intrinsically disordered proteins.
Tamiola K, Mulder FA.       
        """,
      'ncSPC': """
Biochem Soc Trans. 2012 Oct;40(5):1014-20
Using NMR chemical shifts to calculate the propensity for structural order 
and disorder in proteins. 
Tamiola K, Mulder FAA. 
        """,
      'NDPPLOT': """
J Biomol NMR. 2016 Apr; 64(4); 307-332
Integrative NMR for biomolecular research
Lee W et al.
        """,        
      'PACSY': """
J Biomol NMR. 2012 Oct;54(2):169-79
PACSY, a relational database management system for protein structure 
and chemical shift analysis.
Lee W, Yu W, Kim S, Chang I, Lee W, Markley JL.
        """,
      'PINE': """
PLoS Comput Biol. 2009 Mar;5(3):e1000307.
Probabilistic interaction network of evidence algorithm and its application 
to complete labeling of peak lists from protein NMR spectroscopy.
Bahrami A, Assadi AH, Markley JL, Eghbalnia HR.

Journal of Biomolecular NMR. 2019 June; 73(5): 213-222
I-PINE web server: an integrative probabilistic NMR assignment system for proteins
Lee W, Bahrami A, Dashti H, Eghbalnia HR, Tonelli M, Westler WM, Markley JL. 
        """,
      'PINE-SPARKY': """
Bioinformatics. 2009 Aug 15;25(16):2085-7. Epub 2009 Jun 3.
PINE-SPARKY: graphical interface for evaluating automated probabilistic 
peak assignments in protein NMR spectroscopy.
Lee W, Westler WM, Bahrami A, Eghbalnia HR, Markley JL.
        """,
      'PINE-SPARKY.2': """
Bioinformatics.2018 May 1;34(9):1586-8
PINE-SPARKY.2 for automated protein structure research.
Lee W, Markley JL.
        """,
      'PISA-SPARKY':"""
Bioinformatics. 2020 epub
PISA-SPARKY: an interactive SPARKY plugin to analyze oriented solid-state
NMR spectra of helical membrane proteins.
Weber DK, Wang S, Markley JL, Veglia G, Lee W.
        """,  
      'PONDEROSA': """
J Biomol NMR. 2016 Jun;65(2):51-7. Epub 2016 May 12.
The AUDANA algorithm for automated protein 3D structure determination from NMR NOE data.
Lee W, Petit CM, Cornilescu G, Stark JL, Markley JL.
      
J Biomol NMR. 2014 Sep 5.
PONDEROSA-C/S: client-server based software package for automated protein 
3D structure determination.
Lee W, Stark JL, Markley JL.

Bioinformatics. 2011 Jun 15;27(12):1727-8.
PONDEROSA, an automated 3D-NOESY peak picking program, enables automated 
protein structure determination.
Lee W, Kim JH, Westler WM, Markley JL.      
        """,
      'INTEGRATIVE NMR': """
J Biomol NMR. 2016 Apr; 64(4):307-332
Integrative NMR for biomolecular research.
Lee W et al.
      """,
      'PSIPRED': """
J Mol Biol. 1999 Sep 17;292(2):195-202.
Protein secondary structure prediction based on position-specific scoring matrices.
Jones DT.      
        """,
      'Reproducibility': """
Fenwick et al. in preparation      
        """,
      'RNA Ellipses': """
Nucleic Acids Res. 2013 Oct;41(18):e172.
Automated and assisted RNA resonance assignment using NMR chemical shift statistics.
Aeschbacher T, Schmidt E, Blatter M, Maris C, Duss O, Allain FH, Guentert P, Schubert M.
        """,
      'SCASSIGN': """
Bioinformatics. 2006 Nov 15;22(22):2833-4.
SCAssign: a sparky extension for the NMR resonance assignment of aliphatic side-chains 
of uniformly 13C,15N-labeled large proteins.
Zhang L, Yang D.
        """,
      'SHIFTX2': """
J Biomol NMR. 2011 May;50(1):43-57
SHIFTX2: significantly improved protein chemical shift prediction.
Han B, Liu Y, Ginzinger SW, Wishart DS.      
        """,
      'SPARKY 3': """
Goddard TD & Kneller DG (2008) SPARKY 3. University of California, San Francisco.      
        """,
      'STRIDE': """
Nucleic Acids Res. 2004 Jul 1;32(Web Server issue):W500-2.
STRIDE: a web server for secondary structure assignment from known atomic 
coordinates of proteins.
Heinig M, Frishman D.      
        """,
      'TALOS-N': """
J Biomol NMR. 2013 Jul;56(3):227-41.
Protein backbone and sidechain torsion angles predicted from NMR chemical shifts 
using artificial neural networks.
Shen Y, Bax A.      
        """,
      'THIS PROGRAM': """
Bioinformatics. 2015 Apr 15; 31(8):1325-7. Epub 2014 Dec 12
NMRFAM-SPARKY: enhanced software for biomolecular NMR spectroscopy
Lee W, Tonelli M, Markley JL.

J Biomol NMR. 2016 Apr; 64(4); 307-332
Integrative NMR for biomolecular research
Lee W et al.
        """
}
class credit_nmrfamdialog(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
    tkutil.Dialog.__init__(self, session.tk, 'Credits...')
    
    # Create label object
    t1 = tkutil.entry_row(self.top, 'NMRFAM-SPARKY citation: ')
    t1.frame.pack(side = 'top', anchor = 'w')
    t2 = tkutil.entry_row(self.top, 
                '  Bioinformatics. 2015 Apr 15; 31(8):1325-7. Epub 2014 Dec 12')
    t2.frame.pack(side = 'top', anchor = 'w')
    t3 = tkutil.entry_row(self.top, 
                '  NMRFAM-SPARKY: enhanced software for biomolecular NMR spectroscopy.')
    t3.frame.pack(side = 'top', anchor = 'w')    
    t4 = tkutil.entry_row(self.top, '  Lee W, Tonelli M, Markley JL ')
    t4.frame.pack(side = 'top', anchor = 'w')    
        
    # separator 
    import Tkinter
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')    
    
    self.func = sorted(citation_dict.keys())
    
    t5 = tkutil.entry_row(self.top, 'Features used: ')    
    t5.frame.pack(side = 'top', anchor = 'w')    
    
    type_om = tkutil.option_menu(self.top, "type: ", self.func, 'APES')
    type_om.frame.pack(side = 'top', fill="both")
    type_om.add_callback(self.chose_func_cb)
    self.type_om = type_om
    
    # scrolling_list
    self.listbox = tkutil.scrolling_list(self.top, 'Citations for features in NMRFAM-SPARKY: ', 9)    
    self.listbox.frame.pack(side = 'top', fill = 'both', expand = 1)
    
    # separator    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')    
        
    # button    
    self.br = tkutil.button_row(self.top,
			   ('Close', self.close_cb),
			   )
    self.br.frame.pack(side = 'top', anchor = 'w')			       
    
    self.chose_func_cb('APES')
  
  def chose_func_cb(self, name):
    self.listbox.clear()
    lines = citation_dict[name]
    lines_to_add = lines.split('\n')
    for line in lines_to_add[1:]:
      self.listbox.append(line)

 
# -----------------------------------------------------------------------------
#      
def credit_nmrfam_dialog(session):
  sputil.the_dialog(credit_nmrfamdialog,session).show_window(1)
