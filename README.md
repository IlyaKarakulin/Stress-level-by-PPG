
# PPG Signal Processing Toolkit

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/IlyaKarakulin/stress-level-by-PPG?style=social)](https://github.com/IlyaKarakulin/stress-level-by-PPG/stargazers)

A Python package for robust Photoplethysmography (PPG) signal processing with motion artifact removal from wearable devices.

## In this README :point_down:

- [Features](#features)
- [Installation](#initial-setup)
- [Usage](#usage)
  - [Basic-processing](#basic-processing)
  - [Advanced Features](#advanced-features)
- [Visualisation](#demo-visualization-)
- [Processing Workflow](#processing-workflow-️)
- [API Reference 📚](#api-reference-)


## Features

⚡ **Automated Processing Pipeline**
- Spectral analysis and noise detection
- Adaptive filtering with cubic spline interpolation
- Variance-based normalization

📈 **Quality Control**
- Signal quality assessment metrics
- Interactive visualization tools
- Batch processing capabilities

🔧 **Developer Friendly**
- Type checking with mypy
- Linting with ruff
- Formatting with isort/black
- Comprehensive CI/CD pipeline

📚 **Documentation**
- API reference with examples
- Step-by-step processing guide
- Jupyter notebook tutorials

## Installation

### Initial Setup

1. Clone repository:
```bash
git clone https://github.com/IlyaKarakulin/stress-level-by-PPG.git
cd stress-level-by-PPG
```

2. Create conda environment:
```bash
conda create -n ppg-env python=3.9
conda activate ppg-env
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Processing
```python
from ppg_processing import Pipeline, visualize

processor = Pipeline(
    sample_rate=100,
    noise_threshold=0.6
)

raw_signal = processor.load_sample_data()
clean_signal = processor.process(raw_signal)
visualize(raw_signal, clean_signal)
```

### Advanced Features
```python
# Batch processing
from ppg_processing import BatchProcessor

BatchProcessor().run(
    input_dir="data/raw/",
    output_dir="data/processed/",
    config_file="config.yaml"
)

# Quality report generation
from ppg_processing import QualityAnalyzer

report = QualityAnalyzer().generate_full_report(clean_signal)
print(f"Signal Quality Index: {report['sqi']}")
```

## Demo Visualization 🎨

```python
from ppg_processing import load_sample, visualize

raw, clean = load_sample("demo_dataset")
visualize(
    raw_signal=raw,
    processed_signal=clean,
    title="Motion Artifact Removal Demo"
)
```

![Processing Demo](docs/demo_visualization.png)

## Processing Workflow ⚙️

### 1. Preprocessing
- 📉 Baseline correction using moving average
- 🔢 Signal normalization (z-score)
- 🎚️ Adaptive amplitude scaling

### 2. Spectral Analysis
- 🌌 STFT spectrogram calculation (window size=256)
- 🎯 Motion artifact detection in 0.5-5Hz band
- 📊 Noise power ratio estimation

### 3. Adaptive Filtering
- ✂️ Noise-dominant segment removal
- 🧩 Cubic spline interpolation for gaps
- 🌀 Edge smoothing with Tukey window

### 4. Postprocessing
- ✅ Output validation checks
- 📏 Final amplitude normalization
- 💾 Result serialization (CSV/PKL/HDF5)

## API Reference 📚

### Core Classes

| Class               | Methods                          | Description                          |
|---------------------|----------------------------------|--------------------------------------|
| `SpectralFilter`    | `.process()`, `.configure()`     | Main signal processing engine        |
| `QualityAnalyzer`   | `.calculate_snr()`, `.get_report()` | Signal quality assessment toolkit  |
| `BatchProcessor`    | `.run_job()`, `.monitor()`        | Bulk dataset processing              |
| `Visualizer`        | `.plot_raw()`, `.animate()`      | Interactive visualization tools      |

### Key Methods

```python
# Process single file
Pipeline.process_file(
    input_path: str,
    output_dir: str = "./processed",
    config: dict = None
)

# Calculate signal-to-noise ratio
QualityAnalyzer.calculate_snr(
    clean_signal: np.ndarray,
    noise_profile: np.ndarray
) -> float

# Run batch processing
BatchProcessor.run_job(
    config_file: str,
    parallel: bool = True,
    progress_bar: bool = True
)
```


## Contributing

We welcome contributions through:
- 🐛 [Bug Reports](https://github.com/IlyaKarakulin/stress-level-by-PPG/issues/new?template=bug_report.md)
- 🚀 [Feature Requests](https://github.com/IlyaKarakulin/stress-level-by-PPG/issues/new?template=feature_request.md)
- 📖 Documentation Improvements


## FAQ

**Q: Can I use this without wearable device data?**  
A: Yes! The package includes sample datasets for testing.

**Q: How to handle real-time processing?**  
A: Use the `RealtimeProcessor` class with 5-second windowing.

**Q: What input formats are supported?**  
A: CSV, EDF, and NumPy arrays. See `data_formats.md` for details.

## License

Distributed under MIT License. See [LICENSE](LICENSE) for details.

## Support

Found this useful? Give us a ⭐!  
Need help? Contact us:

- 📧 Email: [ppg.support@example.com](mailto:ppg.support@example.com)
- 💬 [Discussion Forum](https://github.com/IlyaKarakulin/stress-level-by-PPG/discussions)
- 🐦 Twitter: [@PPG_Experts](https://twitter.com/PPG_Experts)

---
