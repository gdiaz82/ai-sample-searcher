#  AI Sample Searcher

**Find your samples by describing them, not by filename.**

![Demo](docs/demo.gif)

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

Prerequisite: Python 3.10 is required.

1. **Clone the respository**
```bash
   git clone https://github.com/gdiaz82/ai-sample-searcher
   cd ai-sample-searcher
```
2. **Create a virtual environment (Recommended)**
```bash
    conda create -n audio-search python=3.10
    conda activate audio-search
```
3. **Install dependencies**
```bash
    pip install -r requirements.txt
```
*Note: If you have an NVIDIA GPU, ensure you have the correct PyTorch version with CUDA support installed.*
*pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121*

## Usage

1. **Launch the Application**
```bash
python desktop_app/app.py
```
2. **Index your Library**
When you open the app for the first time, the database will be empty.

- Click the "📂 Add Samples Folder" button at the top.

- Select the root directory of your sample library via the file explorer window.

- The AI will scan and generate embeddings for your files. This is GPU-accelerated but may take a few minutes depending on your library size.

- A popup will confirm when indexing is finished.

3. **Search & Drag**

- Type a description in the search bar (e.g., "Crunchy hip hop snare" or "Atmospheric sci-fi texture").

- Press Enter.

- Click on a result to preview the sound.

- Drag and Drop the result directly from the list into your DAW (Ableton, FL Studio, etc.).


## Cloud Web Demo

I have deployed a lightweight version of the search engine to the cloud, with a small only snare database.

> **[🔴 Try the Live API Demo Here](https://sample-api-284683380712.us-central1.run.app/docs)**

### Cloud Architecture
Unlike the desktop app which indexes your local files, this microservice runs in a containerized environment with a pre-indexed database of 14 snare samples.

### How to test the API:
1. Click the link above.
2. Click on the **POST /search** endpoint.
3. Click **"Try it out"**.
4. Enter a query in the JSON body, e.g.: `{"query": "snare with light reverb"}`
5. Click **Execute** to see the AI results.

## License
This project uses the LAION-CLAP model. Please refer to their repository for model licensing details.