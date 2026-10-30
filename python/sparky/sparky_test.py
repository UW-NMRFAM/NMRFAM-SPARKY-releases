import sparky
import tkutil
import sputil
import Tkinter
class Test_dialog(tkutil.Dialog):
    def __init__(self, session):
        self.session = session
        self.ui_test()
        self.auto_test()

    def ui_test(self):
        tkutil.Dialog.__init__(self, self.session.tk, 'Test')
        guess_button = Tkinter.Button(self.top, text = "Test", command = self.test_cb)
        guess_button.pack(side = 'left', anchor = 'w')

    def test_cb(self):
        pass

    def auto_test(self):
        v = self.session.selected_view()
        print v.pointer_position


def show_dialog(session):
    d = sputil.the_dialog(Test_dialog, session)
    d.show_window(1)
