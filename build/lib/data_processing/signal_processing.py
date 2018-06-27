
# This file is part of pylabcontrol, software for laboratory equipment control for scientific experiments.
# Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell
#
#
# pylabcontrol is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pylabcontrol is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pylabcontrol.  If not, see <http://www.gnu.org/licenses/>.


import numpy as np


def power_spectral_density(x, time_step, freq_range = None):
    """
    returns the power spectral density of the time trace x which is sampled at intervals time_step
    Args:
        x (array):  timetrace
        time_step (float): sampling interval of x
        freq_range (array or tuple): frequency range in the form [f_min, f_max] to return only the spectrum within this range

    Returns:

    """
    P = np.abs(np.fft.rfft(x))**2 * time_step**2 /len(x)
    F = np.fft.rfftfreq(len(x), time_step)

    if freq_range is not None:
        brange = np.all([F>=freq_range[0], F<=freq_range[1]], axis = 0)
        P = P[brange]
        F = F[brange]

    return F, P

if __name__ == '__main__':
    l = 100

    tmax = 10
    t = np.linspace(0, tmax,l)

    dt = tmax / l
    signal = 2.* np.sin(2*np.pi *t) + np.random.randn(l)
    print(signal)

    plt.plot()