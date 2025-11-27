#  AI Sample Searcher

**Find your samples by describing them, not by filename.**

A local desktop application for music producers that allows you to search through your sample library using natural language (e.g., *"Heavy distorted industrial kick"* or *"Atmospheric sci-fi texture"*).

Powered by **LAION-CLAP**, **ChromaDB**, and **PyQt6**.

---

## Features

- **Semantic Search:** Uses Multimodal Embeddings to understand the "vibe" and texture of audio, bridging the gap between text and sound.
- **100% Local Privacy:** No cloud uploads. Your sample library is indexed and stored locally on your machine using ChromaDB.
- **DAW Integration:** Drag & Drop results directly from the app into **Ableton Live**, **FL Studio**, or **Bitwig**.
- **GPU Accelerated:** Optimized for CUDA to index thousands of samples in minutes.
- **Format Support:** Supports `.wav` and `.mp3` files.

## Tech Stack

- **Model:** [LAION-CLAP](https://huggingface.co/laion/clap-htsat-unfused) (Contrastive Language-Audio Pretraining).
- **Database:** [ChromaDB](https://www.trychroma.com/) (Local Vector Database with HNSW indexing).
- **GUI:** PyQt6 (Native desktop interface with Drag & Drop support).
- **Backend:** PyTorch & Transformers.

## Prerequisites

- **OS:** Windows 10/11 (Recommended for Drag & Drop compatibility), Linux, or macOS.
- **Python:** 3.10 or higher.
- **Hardware:** NVIDIA GPU recommended for faster indexing (CPU works but is slower).

## Instalation

1. **Clone the respository**
```bash
   git clone [https://github.com/gdiaz82/ai-sample-searcher](https://github.com/gdiaz82/ai-sample-searcher)
   cd ai-sample-searcher
```
2. **Create a virtual environment (Recommended)**
```bash
    conda create -n audio-search python=3.10
    conda activate audio-search
```
3. **Install depndencies**
```bash
    pip install -r requirements.txt
```
*Note: If you have an NVIDIA GPU, ensure you have the correct PyTorch version with CUDA support installed.*

## Usage

1. **Indexing your Library**
Before searching, the AI needs to "listen" to your samples.
- Open src/indexer.py and set your sample folder path:
```bash
    SAMPLE_FOLDER = "C:/Users/You/Music/Samples"
```
- Run the indexer:
```bash
    python src/indexer.py
```
2. **Launching the App**
Once indexed, launch the GUI:
```bash
    python src/app.py
```
- Type a description (e.g. "Crunchy hip hop snare").
- Press Enter.

## Roadmap
- [x] Core Semantic Search Engine

- [x] Local Vector DB Persistence

- [ ] PyQt6 GUI with Drag & Drop

- [ ] Built-in Audio Player (Preview before drag)

- [ ] File Watcher (Auto-index new files)

- [ ] Metadata Filtering (Filter by BPM or Key)

## License
This project uses the LAION-CLAP model. Please refer to their repository for model licensing details.