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
python 4_topics_answer.py
```

- Clone the course content
```bash
git clone https://github.com/sanand0/tools-in-data-science-public.git raw-data/cloned
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


## **🚀 Cloud Deployment (AWS)**
Deploying your application on AWS EC2 provides full control over the server environment and is ideal for backend applications like your RAG App.

1. **Launch an EC2 Instance**:
    - Ubuntu 22.04 LTS, t3.micro (or bigger if you use larger embeddings)
    - Open ports 22 (SSH) and 6969 (your API)

2. **SSH into the Instance**:
   - Use your key pair to SSH into the instance:
     ```bash
     ssh -i /path/to/key.pem ubuntu@YOUR_EC2_PUBLIC_IP
     ```

3. **Install Dependencies**:
   - Update the package list:
     ```bash
     sudo apt update
     ```
   - Install Python, pip, Git, and other necessary packages:
     ```bash
     sudo apt install python3 python3-pip git
     ```

4. **Clone the Repository**:
   - Clone your GitHub repository:
     ```bash
     git clone https://github.com/Private-Aayansh/Virtual-TA.git
     ```
   - Change to the project directory:
     ```bash
     cd Virtual-TA
     ```

5. **Set Up Virtual Environment**:
   - Create a virtual environment:
     ```bash
     python3 -m venv venv
     ```
   - Activate the virtual environment:
     ```bash
     source venv/bin/activate
     ```

6. **Install Python Dependencies**:
   - Install the required packages:
     ```bash
     pip install -r requirements.txt
     ```

7. **Run the Application**:
     - Create a service file at `/etc/systemd/system/virtual-ta.service`:
   
       ```ini
        [Unit]
        Description=Gunicorn server for your FastAPI app
        After=network.target
        
        [Service]
        User=ubuntu
        Group=ubuntu
        WorkingDirectory=/home/ubuntu/Virtual-TA/api
        Environment="PATH=/home/ubuntu/Virtual-TA/venv/bin"
        Environment="PYTHONPATH=/home/ubuntu/Virtual-TA/api"
        # force uvloop + h11 via env vars for UvicornWorker
        Environment="UVICORN_LOOP=uvloop"
        Environment="UVICORN_HTTP=httph11"
        # 2 workers (one per vCPU), 16 threads each
        ExecStart=/home/ubuntu/Virtual-TA/venv/bin/gunicorn \
          main:app \
          -k uvicorn.workers.UvicornH11Worker \
          --workers 2 \
          --threads 16 \
          --bind 0.0.0.0:8000
        
        Restart=always
        RestartSec=3
        TimeoutStopSec=10
        
        [Install]
        WantedBy=multi-user.target
       ```
     - Reload systemd and start the service:
       ```bash
       sudo systemctl daemon-reload
       sudo systemctl start virtual-ta
       sudo systemctl enable virtual-ta
       ```

8. **Access the Application**:
   - The application will be accessible at `http://<ec2-public-ip>:8000`.

---

