import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
import neurokit2 as nk

class StressIndex:
    def __init__(self, path_to_model: str):
        self.model = CatBoostRegressor()
        self.model.load_model(path_to_model)
        self.feature = [
            'HRV_MeanNN', 'HRV_SDNN', 'HRV_RMSSD', 'HRV_SDSD',
            'HRV_CVNN', 'HRV_CVSD', 'HRV_MedianNN', 'HRV_MadNN',
            'HRV_pNN50', 'HRV_pNN20', 'HRV_MinNN', 'HRV_MaxNN',
            'HRV_HTI', 'HRV_TINN', 'HRV_HF', 'HRV_LF', 'HRV_LFn',
            'HRV_HFn', 'HRV_LFHF'
        ]

    def __get_feature_nk(self, ppg, fr_ppg):
        peaks, _ = nk.ppg_peaks(ppg, sampling_rate=fr_ppg, show=False, method="elgendi")

        time_features = nk.hrv_time(peaks, sampling_rate=fr_ppg)
        frequency_features = nk.hrv_frequency(peaks, sampling_rate=fr_ppg, show=False)

        time_features = time_features.iloc[0].to_dict()
        frequency_features = frequency_features.iloc[0].to_dict()

        hrv_indices = {**time_features, **frequency_features}

        feature_vector = [hrv_indices.get(f) for f in self.feature]

        return feature_vector

    def __calc_feature(self, ppg, fr_ppg, wind_size_in_sec=45, step_in_sec=5):
        feature_list = []
        window_size = int(wind_size_in_sec * fr_ppg)
        step = int(step_in_sec * fr_ppg)
        n_samples = len(ppg)

        for start in range(0, n_samples - window_size + 1, step):
            end = start + window_size
            window = ppg[start:end]
            if np.count_nonzero(window) >= 0.8 * window_size:
                feature_vector = self.__get_feature_nk(ppg=window, fr_ppg=fr_ppg)
                feature_list.append(feature_vector)

        return pd.DataFrame(feature_list, columns=self.feature)

    def predict(self, ppg, fr_ppg):
        data = self.__calc_feature(ppg, fr_ppg)
        return self.model.predict(data)
