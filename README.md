# PPG Signal Processing Toolkit

The SLBPPG framework provides tools for processing the PPG signal.

# Installation

```bash
pip install SLBPPG==0.1
```

# Methods

- **SLBPPG.filter(ppg, ppg_fr)** \
**Input**: \
&nbsp;&nbsp;&nbsp;&nbsp;PPG signal and sampling rate \
**Returns**:
    - PPG signal to which the frequency filter is applied, followed by floating window normalization. The filter also recognizes noise and replaces it with zeros.
    - Frequency filter and normalization only, no noise reduction
- **StressIndex.predict(ppg)** \
**Input**: \
&nbsp;&nbsp;&nbsp;&nbsp;PPG signal and sampling rate \
**Returns**: \
&nbsp;&nbsp;&nbsp;&nbsp;Itress index (on a five-point scale) for each window, duration 1 minute, by default

>You can view the usage example and learn more about the methods in the [file](.demo/example.ipynb)

