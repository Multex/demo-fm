# 📡 demo-fm

**Interactive FM modulation demo with Streamlit.** 

Visualize non-sinusoidal waveforms, analyze spectra, and compare FM vs AM noise robustness in real-time.

![main](./images/page.png)

---

## 🚀 Quick Start

### Option 1: Using virtual environment (Recommended)

```bash
./scripts/run_streamlit.sh
```

### Option 2: Auto-install and run

**Linux:**
```bash
./scripts/run_app.sh
```

**Windows:**
```bash
scripts\run_app.bat
```

### Option 3: Manual

```bash
pip install -r requirements.txt
streamlit run src/main.py
```

---

## 📁 Project Structure

```
demo-fm/
├── docs/                   # Documentation
│   ├── info.md             # Educational guide (Spanish)
│   └── INSTRUCCIONES.txt   # Setup instructions (Spanish)
├── images/                 # Images for documentation
│   └── page.png
├── scripts/                # Run scripts
│   ├── run_app.sh          # Linux/Mac auto-install script
│   ├── run_app.bat         # Windows auto-install script
│   └── run_streamlit.sh    # Linux/Mac with venv
├── src/                    # Source code
│   ├── main.py             # Main Streamlit app
│   ├── core/               # Core FM calculation modules
│   │   ├── __init__.py
│   │   ├── waveforms.py
│   │   ├── spectrum.py
│   │   ├── demodulation.py
│   │   ├── fm_calculator.py
│   │   └── validations.py
│   └── app/                # Streamlit UI components
│       ├── __init__.py
│       ├── sidebar.py
│       ├── components.py
│       └── tabs.py
├── requirements.txt
└── README.md
```

---

## 📚 Documentation

- **[docs/info.md](docs/info.md)** - Small guide on FM concepts (Spanish)
- **[docs/INSTRUCCIONES.txt](docs/INSTRUCCIONES.txt)** - Setup instructions (Spanish)

---

## 🛠️ Tech Stack

- Python 3.8+
- Streamlit
- NumPy
- Matplotlib
