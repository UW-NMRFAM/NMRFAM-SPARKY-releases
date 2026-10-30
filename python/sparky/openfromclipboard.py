import os, platform
def show_open_from_clipboard(session):
  import tkMessageBox
  if platform.system() == 'Linux':
    files = session.tk.selection_get(selection='CLIPBOARD').split()
    if len(files) == 1:
      filename = files[0].strip('\r\n')
      session.open_file(filename)
    else:
      for filename2 in files:
        filename = filename2.strip('\r\n')
        session.open_spectrum(filename)
      #session.open_file(filename2)
  elif os.name == 'posix': # mac
    content = os.popen('pbpaste','r').read()
    if content.find('/') == -1:
      tkMessageBox.showinfo('Not full path..', "To use feature, drag'n drop a file from finder to the terminal and copy a full path from there.")      
    try:
      session.open_file(content)
    except:
      session.open_spectrum(content)          
  else: # windows
    try:  
      content = os.popen('pbpaste','r').read()
    except:
      tkMessageBox.showinfo('Unsupported platform..', 'Unfortunately, your system does not support this feature.')
    try:    
      session.open_file(content)    
    except:
      session.open_spectrum(content)                
    
