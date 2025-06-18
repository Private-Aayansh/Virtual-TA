## ⚙️ Prerequisites

### 1. Clone the Repository
```bash
git clone https://github.com/Private-Aayansh/Virtual-TA.git
```

### 2. Change the working directory
```bash
cd Virtual-TA
```

### 3. Create & Activate Virtual Environment
- #### Create Virtual Environment
  
```bash
python -m venv venv
```

- #### Activate Virtual Environment
For Linux/macOS:
```
source venv/bin/activate
```
For Windows:
```
venv\\Scripts\\activate
```

### 4. Install Required Package Dependencies
```bash
pip install -r requirements.txt
```

---

## **🚀 Setup & Local Development**

## Option 1: Quick Start with Pre-processed Data

This option will let you use pre-processed data and embeddings created by me!

### 1. Change the directory
```bash
cd api
```

### 2. Start the server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 6969
```

## Option 2: Complete Setup from Scratch

This option walks you through the entire data collection and processing pipeline.

### 1. Data Fetching and Embedding

- Fetch the topics first
```bash
python 1_topics_fetcher.py
```

- Clean the topics
```bash
python 2_topics_cleaner.py
```

- Merge the topics
```bash
python 3_topics_merger.py
```

- Fetch the question and replies of the topics
```bash
python 4_topics_anser.py
```

- Clone the course content
```bash
git clone https://github.com/sanand0/tools-in-data-science-public raw-data/cloned
```

- Merge the course content
```bash
python 5_content_merger.py
```

- Create embeddings of Topics Using intfloat-large-instruct
```bash
python 6_topics_embedding.py
```

- Create embeddings of Course content Using intfloat-large-instruct
```bash
python 7_content_embedding.py
```

### 2. Change the directory
```bash
cd api
```

### 3. Start the server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 6969
```
