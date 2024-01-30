import wx
import os
import ctypes


APP_EXIT = 1
NEW_NETLIST = 2
NEW_LIB = 3
IMPORT_LIB = 4
IMPORT_NETLIST = 5

current_dir = os.path.dirname(os.path.abspath(__file__))
# build the path to dir_assets
dir_assets = os.path.join(current_dir, '..', 'assets')

wildcard = "Python source (*.py)|*.py|" \
            "All files (*.*)|*.*"

def path_to_assets(file):
    return os.path.join(dir_assets, file)

class Interface(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(Interface, self).__init__(*args, **kwargs)
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "File and Folder Dialogs Tutorial")
        self.currentDirectory = os.getcwd()
        self.SetIcon(wx.Icon(path_to_assets("cusco_icon.png"), wx.BITMAP_TYPE_PNG))  # Configures the window icon
        
        # Configure the toolbar icon 
        my_app_id = r'cusco.v1.0'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
        
        self.InitUI()

    def PNGtoBMPresizer(self, png_path, width, height):
        bitmap = wx.Bitmap(png_path)
        bitmap.Rescale(bitmap, wx.Size(width,height))
        return bitmap

    def InitUI(self):

        menubar = wx.MenuBar()
        fileMenu = wx.Menu()

        new_netlist_item = wx.MenuItem(fileMenu, NEW_NETLIST, '&Create New Netlist\tCtrl+N')
        new_netlist_item.SetBitmap(self.PNGtoBMPresizer(path_to_assets('new_netlist_icon.png'), 20, 20)) 
        fileMenu.Append(new_netlist_item)

        new_lib_item = wx.MenuItem(fileMenu, NEW_LIB, '&Create New Library\tCtrl+L')
        new_lib_item.SetBitmap(self.PNGtoBMPresizer(path_to_assets('new_lib_icon.png'), 20, 20)) 
        fileMenu.Append(new_lib_item)

        imp = wx.Menu()
        imp.Append(IMPORT_LIB, 'Import Library')
        imp.Append(IMPORT_NETLIST, 'Import Netlist')

        fileMenu.AppendSubMenu(imp, 'I&mport' )

        quit_item = wx.MenuItem(fileMenu, APP_EXIT, '&Quit\tCtrl+Q')
        quit_item.SetBitmap(self.PNGtoBMPresizer(path_to_assets('quit_icon.png'), 20, 20)) 
        fileMenu.Append(quit_item)

        self.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
        self.Bind(wx.EVT_MENU, lambda event, file_type='LIB': self.onOpenFile(event, file_type), id=IMPORT_LIB)
        self.Bind(wx.EVT_MENU, lambda event, file_type='NETLIST': self.onOpenFile(event, file_type), id=IMPORT_NETLIST)
      
        self.Bind(wx.EVT_CLOSE, self.OnQuit)

        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)


        self.SetSize((350, 250))
        self.SetTitle('Cusco Cell Generator')
        self.Centre()
    
    def OnQuit(self, e):
        self.Close()
        wx.Exit()

    def onOpenFile(self, event, file_type):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=self.currentDirectory, 
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            print("You chose the following file(s):")
            for path in paths:
                print(path)
            if file_type == 'LIB':
                print('LIB')
            if file_type == 'NETLIST':
                print('UEEEEPAAA')

        dlg.Destroy()

def main():

    app = wx.App()
    ex = Interface(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()