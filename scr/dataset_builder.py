import pandas as pd
import numpy as np

class PPGDatasetBulder:
    def __init__(self, ppg_fr=256):
        self.ppg_fr = ppg_fr
        self.dataset = []


    def add_segment(self, signal, start_sec, end_sec, label):
        # start_idx = int(start_sec * self.ppg_fr)
        # end_idx = int(end_sec * self.ppg_fr)

        start_idx = int(start_sec * len(signal))
        end_idx = int(end_sec * len(signal))

        # if start_idx >= len(signal) or end_idx > len(signal):
        #     raise ValueError("Incorrect time points!")
        
        segment = signal[start_idx:end_idx]

        self.dataset.append((segment, label))


    def process_file(self, file_path, annotations):
        data = pd.read_csv(file_path)
        signal = data['afe_LED1ABSVAL'].values

        for ann in annotations:
            self.add_segment(signal, ann['start'], ann['end'], ann['label'])


    def save(self, output_path):
        np.save(output_path, np.array(self.dataset, dtype=object))

    def get_dataset(self):
        return np.array(self.dataset, dtype=object)
    