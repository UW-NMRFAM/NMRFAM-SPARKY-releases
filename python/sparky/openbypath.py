import os
def show_open_by_path(session):
    content = os.popen('pbpaste','r').read()
    print content
    session.open_spectrum(content)
