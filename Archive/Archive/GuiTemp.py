import matplotlib
matplotlib.interactive( True )
matplotlib.use( 'WXAgg' )
import matplotlib.pyplot as plt

import numpy as num
import numpy.random
import wx

class PlotPanel (wx.Panel):
    """The PlotPanel has a Figure and a Canvas. OnSize events simply set a
flag, and the actual resizing of the figure is triggered by an Idle event."""
    def __init__( self, parent, fignum, **kwargs ):
        from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
        from matplotlib.figure import Figure

        # initialize Panel
        if 'id' not in kwargs.keys():
            kwargs['id'] = wx.ID_ANY
        if 'style' not in kwargs.keys():
            kwargs['style'] = wx.NO_FULL_REPAINT_ON_RESIZE
        #wx.Panel.__init__( self, parent, pos=pos, size=size, **kwargs )
        wx.Panel.__init__( self, parent, **kwargs )

        # initialize matplotlib stuff
        self.figure = plt.figure(fignum)
        self.canvas = FigureCanvasWxAgg( self, -1, self.figure )
        self.SetColor( None )

        #self._SetSize()
        self.draw()

        self._resizeflag = False

        #self.Bind(wx.EVT_IDLE, self._onIdle)
        #self.Bind(wx.EVT_SIZE, self._onSize)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.canvas, .5, wx.EXPAND | wx.ALL)

        self.SetSizerAndFit(sizer)

    def SetColor( self, rgbtuple=None ):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ).Get()
        clr = [c/255. for c in rgbtuple]
        self.figure.set_facecolor( clr )
        self.figure.set_edgecolor( clr )
        self.canvas.SetBackgroundColour( wx.Colour( *rgbtuple ) )

    #def _onSize( self, event ):
    #    self._resizeflag = True

    #def _onIdle( self, evt ):
       # if self._resizeflag:
        #    self._resizeflag = False
         #   self._SetSize()

    #def _SetSize( self ):
    #    pixels = tuple( self.parent.GetClientSize() )
     #   self.SetSize( pixels )
     #   self.canvas.SetSize( pixels )
      #  self.figure.set_size_inches( float( pixels[0] )/self.figure.get_dpi(),
      #                               float( pixels[1] )/self.figure.get_dpi() )

    def draw(self): pass # abstract, to be overridden by child classes


class TestFrame(wx.Frame):

    def __init__(self, parent):
        frame = wx.Frame.__init__( self, None, title = 'Experiment', size=(200,200), pos=(0,0) )
        self.CreateStatusBar()
        filemenu = wx.Menu()

        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", " Information about the Program")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit", " Terminate the Program")

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        self.Show(True)

    def OnAbout(self,e):
        dlg = wx.MessageDialog( self, "It Runs The Experiment", "About Our Experiment Runner", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self,e):
        self.Close(True)

class TextBoxPanel(wx.Panel):
    def __init__( self, parent, tbNum, **kwargs ):
        # initialize Panel
        if 'id' not in kwargs.keys():
            kwargs['id'] = wx.ID_ANY
        if 'style' not in kwargs.keys():
            kwargs['style'] = wx.NO_FULL_REPAINT_ON_RESIZE
        wx.Panel.__init__( self, parent, **kwargs )
        sizer = wx.GridSizer(tbNum/2,2)
        for i in range(tbNum):
            boxSizer = wx.BoxSizer(wx.VERTICAL)
            boxSizer.Add(wx.TextCtrl(self))
            boxSizer.Add(wx.StaticText(self,-1,'Test'))
            sizer.Add(boxSizer, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border = 5)
        self.SetSizerAndFit(sizer)


if __name__ == '__main__':
    class DemoPlotPanel1 (PlotPanel):
        """Plots several lines in distinct colors."""
        def __init__( self, parent, **kwargs ):
            self.parent = parent

            # initiate plotter
            PlotPanel.__init__( self, parent, 1, **kwargs )
            self.SetColor( (255,255,255) )

        def draw( self ):
            """Draw data."""
            mat = [[1,2,3],[3,4,5],[5,6,7]]
            ax = self.figure.add_axes([0.0,0.08,1.0,.9])
            im = ax.imshow(mat, cmap = 'summer',interpolation="nearest")
            self.figure.colorbar(im)
    class DemoPlotPanel2 (PlotPanel):
        """Plots several lines in distinct colors."""
        def __init__( self, parent, **kwargs ):
            self.parent = parent

            # initiate plotter
            PlotPanel.__init__( self, parent, 2, **kwargs )
            self.SetColor( (255,255,255) )

        def draw( self ):
            """Draw data."""
            mat = numpy.random.ranf((5,5))
            ax = self.figure.add_axes([0.0,0.08,1,.9])
            im = ax.imshow(mat, interpolation="nearest")
            self.figure.colorbar(im)

    app = wx.App( False )
    frame = TestFrame(None)
    panel1 = DemoPlotPanel1(frame)
    panel2 = DemoPlotPanel2(frame)
    panel3 = TextBoxPanel(frame,10)
    sizer = wx.GridSizer(2,2)
    sizer.Add(panel1, 0, wx.EXPAND | wx.ALL, border = 0)
    sizer.Add(panel2, 0, wx.EXPAND | wx.ALL, border = 0)
    sizer.Add(panel3)
    frame.SetSizerAndFit(sizer)
    frame.Show()
    app.MainLoop()