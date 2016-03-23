import numpy as np

from src.scripts_old import ESR

if __name__ == '__main__':
    RF_Power = -12
    avg = 200
    test_freqs = np.linspace(2820000000, 2920000000, 200)
    esr_data, fit_params, fig = ESR.run_esr(RF_Power, test_freqs, num_avg=avg, int_time=.002)
    dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150714_Diamond_Ramp_Over_Mags_ESR'
    tag = 'NV1_RFPower_{:03d}mdB_NumAvrg_{:03d}'.format(RF_Power, avg)
    print('saving ESR spectrum {:s} '.format(tag))
    # ESR.save_esr(esr_data, fig, dirpath, tag)