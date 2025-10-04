# EdFitter


## Description


EdFitter is a Gradio-based application that guides learners and academic staff in matching educational courses with labour-market expectations. The interface allows users to compare course offerings and job vacancies, collect feedback, and explore recommendation settings within a unified dashboard backed by configurable data and embeddings.




## Dataset Information


The datasets required by EdFitter combine HeadHunter (HH) job descriptions with internal course information from National Research University Higher School of Economics (HSE). HH vacancy data can be found here: https://disk.yandex.ru/d/9_dinpnWHeUP-w. HSE internal data about all University courses is private and one needs to adapt the interface to their specific data and calculate similarity scores. During preparation, HTML artefacts and duplicate records are removed, text is normalised, and TF-IDF plus Sentence-BERT similarity scores are computed to link jobs with relevant courses. These derived links power the recommendation interface.





Before running the application, provision the data under `app/data`.


Update `config.toml` if your data lives in a different location or if you need to rename any of these assets.





## Code Information


- `app.py` instantiates the Gradio Blocks UI, registers tabs, and launches the application server with optional background services for quality monitoring.


- `app/config.py` and `config.toml` define runtime settings (tab selection, paths to datasets, labels, and UI strings) that are loaded into a shared namespace at startup.


- `app/data_init.py` handles eager loading of skills, grade data, and initial SBERT embeddings.


- `app/load_models.py` manages SentenceTransformer models and updates embeddings for course or vacancy recommendations.


- `app/tabs.py` builds the interactive interface components (user profile form, recommendation controls, and auxiliary informational sections).





## Usage Instructions


1. Create and activate a Python 3.12 environment.


2. Install the dependencies: `pip install -r requirements.txt`.


3. Place the data in `app/data`


4. Launch the Gradio app with `python app.py`. The interface will be available at `http://localhost:7860` by default.







## Requirements


- Python 3.12


- Core libraries: Gradio 5.7, Polars, PyArrow or FastParquet for Parquet IO, SentenceTransformers (and Safetensors/Einops for model support), FastAPI, DuckDB, and psutil (see `requirements.txt` for pinned versions).


- Optional GPU acceleration via PyTorch if available.





---
title: EdFitter
emoji: 🔝
colorFrom: gray
colorTo: red
sdk: gradio
python_version: 3.12
sdk_version: 5.7.0
app_file: app.py
app_port: 7860
header: default
pinned: true
license: mit
short_description: 
---

Check out the configuration reference here <https://huggingface.co/docs/hub/spaces-config-reference>
