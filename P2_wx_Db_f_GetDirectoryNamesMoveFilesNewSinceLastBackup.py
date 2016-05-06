#
# DRILL:
# get user input for source directory
# get user input for destination directory
# user initiates the script
# identify files created or edited since last backup
# copy them to a transfer folder
# do it in a wxPython UI
# use Python2 and IDLE
#
import time
import os
import os.path
import shutil
import wx
import sqlite3


class GUI(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        #CREATE FRAME
        self.SetSize((700,400))
        self.Centre()
        self.CreateStatusBar()
        self.Show()
        self.sourceDir = ""
        self.destDir = ""
        
        #DEFINE MENUBAR ACTIONS
        def sourceChoose(event):
            srcPicker = wx.DirDialog(self, "Choose Source Directory")
            if srcPicker.ShowModal() == wx.ID_OK:
                self.sourceDir = srcPicker.GetPath()
                srcDisplay.SetValue(self.sourceDir)
            srcPicker.Destroy()

        def destChoose(event):
            destPicker = wx.DirDialog(self, "Choose Destination Directory")
            if destPicker.ShowModal() == wx.ID_OK:
                self.destDir = destPicker.GetPath()
                destDisplay.SetValue(self.destDir)
            destPicker.Destroy()

        def OnQuit(event):
            conn.close()
            self.Close()

        #CREATE MENUBAR
        fileMenu = wx.Menu()
        src = wx.MenuItem(fileMenu,wx.ID_ANY, "Choose Source directory")
        dest = wx.MenuItem(fileMenu,wx.ID_ANY, "Choose Destination directory")
        self.Bind(wx.EVT_MENU, sourceChoose, src)
        self.Bind(wx.EVT_MENU, destChoose, dest)
        fileMenu.AppendItem(src)
        fileMenu.AppendItem(dest)

        exitMenu = wx.Menu()
        exitItem = wx.MenuItem(exitMenu,wx.ID_EXIT, "Quit")
        self.Bind(wx.EVT_MENU, OnQuit, exitItem)
        exitMenu.AppendItem(exitItem)

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu,"FilePaths") 
        menuBar.Append(exitMenu,"Exit") 
        self.SetMenuBar(menuBar)

        #DEFINE PANEL ACTION
        def backup(event):
            if self.sourceDir == "" or self.destDir == "":
                warn = wx.MessageDialog(self, "Source and Destination Directories must be set before backup can be performed", "Paths not set", wx.OK)
                warn.ShowModal()
                warn.Destroy()
            else:
                #---->SET TIME VARIABLES
                now = time.time()
                nowAsc = time.asctime(time.localtime(now))

                #---->DECLARE INTENTION TO USER
                print "-------------------------------------------------------------------"
                print "Archiving all files created between \t",self.then,"(",self.thenAsc,")"
                print "\t\t\t\tand \t",now,"(",nowAsc,")"
                print "-------------------------------------------------------------------\n"
                print "NAME\t\t\tSIZE\tCREATED\t\tEDITED"

                #---->ANALYZE AND COPY FILES
                moveFiles = []
                counter = 0
                files = os.listdir(self.sourceDir)

                for f in files:
                    sourceFile = self.sourceDir + "\\" + f
                    fsize = os.path.getsize(sourceFile)
                    created = os.path.getctime(sourceFile)
                    modified = os.path.getmtime(sourceFile)
                    if created >= self.then or modified >= self.then:
                        counter += 1
                        destFile = self.destDir+ "\\"  + f
                        shutil.copy(sourceFile, destFile)
                        if len(f)<=14:
                            print f,"\t\t",fsize,"\t",created,"\t",modified
                        else:
                            print f,"\t",fsize,"\t",created,"\t",modified

                #---->REPORT RESULT TO USER
                print "\n--------------------------------------------------------------------"
                print "moved ",counter," files."
                #---->REPORT RESULT TO DATABASE
                print type(now), type(counter)
                c.execute("INSERT INTO events (backupTime, numberOfFiles) VALUES (?,?)", (now, counter))
                conn.commit()
                print "After backup, the current contents of the event database are:"
                c.execute("SELECT * FROM events")
                for row in c:
                    print row
                


        #CREATE PANEL
        panel=wx.Panel(self, size=(700,400))
        srcLabel = wx.StaticText(panel, pos=(10,15), size=(150,30), label="Source Directory ")
        destLabel = wx.StaticText(panel, pos=(10,45), size=(150,30), label="Destination Directory ")
        srcDisplay = wx.TextCtrl(panel, pos=(180,10), size=(400,30), style=wx.TE_READONLY | wx.TE_CENTER)
        destDisplay = wx.TextCtrl(panel, pos=(180,40), size=(400,30), style=wx.TE_READONLY | wx.TE_CENTER)

        lastLabel = wx.StaticText(panel, pos=(100,150), size=(500,30), style=wx.TE_READONLY | wx.TE_CENTER)
        
        go = wx.Button(panel, pos=(300,250), size=(100,60), label="Backup Files")
        self.Bind(wx.EVT_BUTTON, backup, go)

        # CREATE/OPEN DATABASE AND TABLE
        conn = sqlite3.connect("backups.db")
        c=conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, backupTime FLOAT, numberOfFiles INT)")
        allBackup = c.execute("SELECT * FROM events ORDER BY id DESC")
        print "Prior to backup, all backups: "
        for row in allBackup:
            print row
        
        # GET LAST BACKUP INFORMATION
        c.execute("SELECT * FROM events ORDER BY id DESC LIMIT 1")
        lastBackup = c.fetchone()
        print "Last Backup: "
        print lastBackup
        print "--------------------------"
        self.then = lastBackup[1]
        self.thenAsc = time.asctime(time.localtime(self.then))
        nf = lastBackup[2]
        lastLabel.SetLabel("Last backup ("+str(nf)+" files) was performed on "+str(self.thenAsc))



def main():
    
    # LAUNCH THE GUI
    app = wx.App()
    MainFrame = GUI(None, "Daily File Backup")
    app.MainLoop()

if __name__ == "__main__" : main()
