import numpy as np
# import hrvanalysis

def SI(rr_int_ms, window=300, si_percent=0.1):
    """
    Интервалы в MS.
    """
    rr_int_s = rr_int_ms / 1000
    ret = []

    for i in range(len(rr_int_ms)-window):
        sample = rr_int_s[i:i+window]
        MO = np.median(sample)
        AMO = (np.abs(sample - MO)<si_percent).mean()*100
        MxDMn = sample.max() - sample.min()
        
        si = AMO/(2*MO*MxDMn)
        if si > 1000:
            sample = sample + np.random.randint(-100, 110, len(sample))/1000
            MO = np.median(sample)
            AMO = (np.abs(sample - MO)<si_percent).mean()*100
            MxDMn = sample.max() - sample.min()
            if (MO*MxDMn) == 0:
                si = 0
                print("Aaaaaaaaaaaa")
            si = AMO/(2*MO*MxDMn)
        
        ret.append(si)
    return np.array(ret)

def HR(rr_int_ms, window=300):
    """
    Интервалы в MS.
    """
    ret = []
    for i in range(len(rr_int_ms)-window):
        slice_ = rr_int_ms[i:i+window]
        n_intervals_duration_in_sec = slice_.sum()/64
        hr = window/n_intervals_duration_in_sec*60
        ret.append(hr)
    return ret

def SDRR(rr_int_ms, window=300):
    ret = []
    for i in range(len(rr_int_ms)-window):
        slice_ = rr_int_ms[i:i+window]
        ret.append(np.std(slice_)*np.sqrt(window)/np.sqrt(window-1))
    return ret

def RMSSD(rr_int_ms, window=300):
    ret = []
    for i in range(len(rr_int_ms)-window):
        slice_ = rr_int_ms[i:i+window]
        rmssd = 0
        for j in range(len(slice_)-1):
            rmssd += (slice_[j+1] - slice_[j])**2
        
        rmssd = np.sqrt(rmssd/(window-1))
        ret.append(rmssd)
    return ret

def SD1(rr_int_ms, window=300):
    ret = []
    k = window - 1
    for i in range(len(rr_int_ms)-window):
        slice_1 = rr_int_ms[i:i+k]
        slice_2 = rr_int_ms[i+1:i+k+1]
        slice_1 = slice_1[:len(slice_2)]
        
        sd1 = np.std((slice_1 - slice_2)/np.sqrt(2))
        
        ret.append(sd1*np.sqrt(k)/np.sqrt(k-1))
    return np.array(ret)

def SD2(rr_int_ms, window=300):
    ret = []
    k = window
    for i in range(len(rr_int_ms)-window):
        slice_1 = rr_int_ms[i:i+k]
        slice_2 = rr_int_ms[i+1:i+k+1]
        slice_1 = slice_1[:len(slice_2)]
        
        sd2 = np.std((slice_1 + slice_2)/np.sqrt(2))
        
        ret.append(sd2*np.sqrt(k)/np.sqrt(k-1))
    return np.array(ret)

def SD1_SD2_RATIO(rr_int_ms, window=300):
    sd1 = SD1(rr_int_ms, window)
    sd2 = SD2(rr_int_ms, window)
    sd2 = np.where(sd2 == 0, np.ones(len(sd2))*0.0001, sd2)
    sd1_sd2_ratio = sd1 / sd2
    return sd1_sd2_ratio

def LF_HR_RATIO(rr_int_ms, window=300):
    # ret = []
    # for i in range(0, len(rr_int_ms)-window):
    #     fd = hrvanalysis.extract_features.get_frequency_domain_features(rr_int_ms[i:i+window], sampling_frequency = 4)
    #     lf_hf_ratio = fd['lf_hf_ratio']
    #     if np.isnan(lf_hf_ratio):
    #         lf_hf_ratio = 10
    #     ret.append(lf_hf_ratio)
    # return ret
    sd1 = SD1(rr_int_ms, window)
    sd2 = SD2(rr_int_ms, window)
    sd2 = np.where(sd2 == 0, np.ones(len(sd2))*0.0001, sd2)
    sd1_sd2_ratio = sd1 / sd2
    return sd1_sd2_ratio