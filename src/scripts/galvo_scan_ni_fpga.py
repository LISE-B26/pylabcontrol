from src.core import Script, Parameter
import numpy as np
from src.instruments.labview_fpga import NI7845RGalvoScan
from src.plotting.plots_2d import plot_fluorescence_new, update_fluorescence
from copy import deepcopy
import datetime



class GalvoScanNIFpga(Script):
    """
GalvoScan uses the apd, daq, and galvo to sweep across voltages while counting photons at each voltage,
resulting in an image in the current field of view of the objective.
    """

    _DEFAULT_SETTINGS = [
        Parameter('max_counts_plot', -1, int, 'Rescales colorbar with this as the maximum counts on replotting')
    ]

    _INSTRUMENTS = {'NI7845RGalvoScan':  NI7845RGalvoScan}

    _SCRIPTS = {}

    def __init__(self, instruments, name = None, settings = None, log_function = None, timeout = 1000000000, data_path = None):

        Script.__init__(self, name, settings=settings, instruments=instruments, log_function=log_function, data_path = data_path)


    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        instr = self.instruments['NI7845RGalvoScan']['instance']
        instr_settings = deepcopy(self.instruments['NI7845RGalvoScan']['settings'])
        del instr_settings['piezo'] # don't update piezo to avoid spikes (assume this value is 0 but the scan starts at 50V, then this would give a huge step which is not necessary)

        def init_scan():
            # self._recording = False
            instr.update(instr_settings)

            Nx = instr_settings['num_points']['x']
            Ny = instr_settings['num_points']['y']
            time_per_pt = instr_settings['time_per_pt']
            extent = instr.pts_to_extent(instr_settings['point_a'], instr_settings['point_b'], instr_settings['RoI_mode'])

            self.data = {'image_data': np.zeros((Nx, Ny)), 'extent': extent}

            return Nx, Ny

        def print_diagnostics():
            print(unicode(datetime.datetime.now()))
            # diagnostics = {
            #     'acquire': instr.acquire,
            #     'elements_written_to_dma': instr.elements_written_to_dma,
            #     'DMATimeOut': instr.acquire,
            #     'ix': instr.ix,
            #     'iy': instr.iy,
            #     'detector_signal': instr.detector_signal,
            #     'Nx': instr.Nx,
            #     'Ny': instr.Ny,
            #     'running': instr.running,
            #     'DMA_elem_to_write': instr.DMA_elem_to_write,
            #     'loop_time': instr.loop_time,
            #     'meas_per_pt': instr.meas_per_pt,
            #     'settle_time': instr.settle_time,
            #     'failed': instr.failed
            # }

            # diagnostics = instr.read_probes()
            #
            # print(diagnostics)

        def calc_progress(i, Ny):
            return int(float(i + 1) / Ny * 100)

        Nx, Ny = init_scan()

        instr.start_acquire()

        i = 0

        while i < Ny:
            if self._abort:
                instr.abort_acquire()
                break

            elem_written = instr.elements_written_to_dma

            if elem_written >= Nx:
                line_data = instr.read_fifo(Nx)
                self.data['image_data'][:,i] = deepcopy(line_data['signal'])/1e3

                # set the remaining values to the mean so that we get a good contrast while plotting
                mean_value = np.mean(self.data['image_data'][0:i+1])
                self.data['image_data'][:,i+1:] = mean_value*np.ones((Nx, Ny-(i+1)))

                i +=1
                progress  = calc_progress(i, Ny)
                self.updateProgress.emit(progress)


        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()
            self.save_image_to_disk()

    @staticmethod
    def pts_to_extent(pta, ptb, roi_mode):
        """

        Args:
            pta: point a
            ptb: point b
            roi_mode:   mode how to calculate region of interest
                        corner: pta and ptb are diagonal corners of rectangle.
                        center: pta is center and ptb is extend or rectangle

        Returns: extend of region of interest [xVmin, xVmax, yVmax, yVmin]

        """
        if roi_mode == 'corner':
            xVmin = min(pta['x'], ptb['x'])
            xVmax = max(pta['x'], ptb['x'])
            yVmin = min(pta['y'], ptb['y'])
            yVmax = max(pta['y'], ptb['y'])
        elif roi_mode == 'center':
            xVmin = pta['x'] - float(ptb['x']) / 2.
            xVmax = pta['x'] + float(ptb['x']) / 2.
            yVmin = pta['y'] - float(ptb['y']) / 2.
            yVmax = pta['y'] + float(ptb['y']) / 2.
        return [xVmin, xVmax, yVmax, yVmin]


    def _plot(self, axes_list):
        '''
        Plots the galvo scan image to the input figure, clearing the figure and creating new axes if necessary
        Args:
            image_figure: figure to plot onto
            axes_colorbar: axes with a colorbar to overwrite with the new colorbar

        '''
        plot_fluorescence_new(self.data['image_data'].transpose(), self.data['extent'], axes_list[0],max_counts=self.settings['max_counts_plot'])

    def _update_plot(self, axes_list):
        """
        updates the image data. This is more efficient than replotting from scratch
        Args:
            axes_list:
        Returns:

        """
        axes_image = axes_list[0]
        update_fluorescence(self.data['image_data'].transpose(), axes_image, self.settings['max_counts_plot'])

    def get_axes_layout(self, figure_list):
        """
        returns the axes objects the script needs to plot its data
        the default creates a single axes object on each figure
        This can/should be overwritten in a child script if more axes objects are needed
        Args:
            figure_list: a list of figure objects
        Returns:
            axes_list: a list of axes objects

        """

        # only pick the first figure from the figure list, this avoids that get_axes_layout clears all the figures
        return Script.get_axes_layout(self, [figure_list[0]])

if __name__ == '__main__':
    script, failed, instruments = Script.load_and_append(script_dict={'GalvoScanNIFpga': 'GalvoScanNIFpga'})

    print('script',script)
    print('failed', failed)
    gs = script['GalvoScanNIFpga']
    print(gs)

    print(gs.instruments['NI7845RGalvoScan']['instance'].settings)

    gs.run()
    print(gs.data)

