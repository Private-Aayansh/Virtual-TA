# TDS Virtual Teaching Assistant

A Retrieval Augmented Generation (RAG) system that serves as a Virtual Teaching Assistant for the "Tools in Data Science" course. The system scrapes course content and forum discussions, creates vector embeddings, and provides intelligent responses to student questions using OpenAI's GPT-4o-mini.

## Features

- **Multi-source Knowledge Base**: Combines course materials and forum discussions
- **Vector Search**: Uses FAISS for efficient similarity search
- **Image Support**: OCR text extraction from student-submitted images
- **RESTful API**: FastAPI-based endpoint for question answering
- **Intelligent Responses**: Context-aware answers with source citations

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Processing     │    │   API Service   │
│                 │    │                  │    │                 │
│ • Course Repo   │───▶│ • Text Chunking  │───▶│ • FastAPI App   │
│ • Discourse     │    │ • Embeddings     │    │ • Vector Search │
│   Forum         │    │ • FAISS Index    │    │ • LLM Response  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Setup & Local Development

### Option 1: Complete Setup from Scratch

This option walks you through the entire data collection and processing pipeline.

#### Prerequisites

- Python 3.8+
- Git
- Access to the course repository
- Valid authentication cookies for Discourse forum
- API keys for OpenAI and Together AI

#### Step 1: Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd tds-virtual-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR for image processing
# On Ubuntu/Debian:
sudo apt-get update
sudo apt-get install tesseract-ocr

# On macOS:
brew install tesseract

# On Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
```

#### Step 2: Environment Variables

Create a `.env` file in the root directory:

```env
AIPROXY_API_KEY=your_openai_api_key_here
TOGETHER_AI_API_KEY=your_together_ai_api_key_here
```

#### Step 3: Data Collection & Processing

```bash
# Create necessary directories
mkdir -p raw-data/fetched raw-data/cleaned raw-data/cloned data extra

# Step 1: Clone the course repository
git clone <course-repo-url> raw-data/cloned

# Step 2: Update authentication cookies in scraping files
# Edit the COOKIE variable in 1_topics_fetcher.py and 4_topics_answer.py
# with valid Discourse forum authentication cookies

# Step 3: Run the data processing pipeline
python 1_topics_fetcher.py      # Fetch forum topics
python 2_topics_cleaner.py      # Clean and filter topics
python 3_topics_merger.py       # Merge topic files
python 4_topics_answer.py       # Fetch detailed discussions
python 5_content_merger.py      # Process course content
python 6_topics_embedding.py    # Create discourse embeddings
python 7_content_embedding.py   # Create course embeddings
```

#### Step 4: Run the Application

```bash
# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# The API will be available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### Option 2: Quick Start (Assuming Data Available)

If you already have the processed data files, follow these steps:

#### Prerequisites

- Python 3.8+
- Processed data files in the `data/` directory:
  - `discourse_index.faiss`
  - `discourse_metadata.json`
  - `course_index.faiss`
  - `course_metadata.json`

#### Setup

```bash
# Clone and setup environment
git clone <your-repo-url>
cd tds-virtual-assistant
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR
# (See installation instructions in Option 1)

# Create .env file with API keys
echo "AIPROXY_API_KEY=your_openai_api_key" >> .env
echo "TOGETHER_AI_API_KEY=your_together_ai_key" >> .env

# Ensure data files are in place
ls data/
# Should show: course_index.faiss, course_metadata.json, discourse_index.faiss, discourse_metadata.json

# Start the application
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Usage

### Endpoint: POST /generate-answer

Send questions to the virtual teaching assistant.

**Request Body:**
```json
{
  "question": "How do I deploy a FastAPI application?",
  "image": "optional_base64_encoded_image"
}
```

**Response:**
```json
{
  "answer": "To deploy a FastAPI application, you have several options...",
  "links": [
    {
      "url": "https://discourse.example.com/topic/123",
      "text": "FastAPI Deployment Discussion"
    }
  ]
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/generate-answer" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "What is the difference between supervised and unsupervised learning?"
     }'
```

## Deployment

### Vercel Deployment

Vercel provides free serverless hosting for FastAPI applications.

#### Prerequisites
- GitHub account
- Vercel account
- API keys set as environment variables

#### Step 1: Prepare for Vercel

Create `vercel.json` in the root directory:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ],
  "env": {
    "AIPROXY_API_KEY": "@aiproxy_api_key",
    "TOGETHER_AI_API_KEY": "@together_ai_api_key"
  }
}
```

#### Step 2: Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod

# Set environment variables
vercel env add AIPROXY_API_KEY
vercel env add TOGETHER_AI_API_KEY

# Redeploy with environment variables
vercel --prod
```

**Alternative: GitHub Integration**

1. Push your code to GitHub
2. Connect your GitHub repository to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy automatically on every push

#### Vercel Limitations & Considerations

- **File Size**: Vector database files (FAISS indices) must be <50MB
- **Memory**: Limited to 1024MB RAM in free tier
- **Execution Time**: 10-second timeout for serverless functions
- **Storage**: No persistent file storage

### AWS Deployment

For production workloads with larger datasets and more control.

#### Option A: AWS EC2 Deployment

**Step 1: Launch EC2 Instance**

```bash
# Launch Ubuntu 20.04 LTS instance
# Minimum recommended: t3.medium (2 vCPU, 4GB RAM)

# Security Group Rules:
# - SSH (22) from your IP
# - HTTP (80) from anywhere (0.0.0.0/0)
# - HTTPS (443) from anywhere (0.0.0.0/0)
# - Custom TCP (8000) from anywhere (0.0.0.0/0)
```

**Step 2: Setup Server**

```bash
# Connect to instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv nginx tesseract-ocr -y

# Clone your repository
git clone <your-repo-url>
cd tds-virtual-assistant

# Setup application
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create environment file
echo "AIPROXY_API_KEY=your_key" > .env
echo "TOGETHER_AI_API_KEY=your_key" >> .env
```

**Step 3: Configure Nginx**

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/tds-assistant

# Add configuration:
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/tds-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Step 4: Setup Process Management**

```bash
# Install PM2 for process management
sudo npm install -g pm2

# Create PM2 ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'tds-assistant',
    script: 'venv/bin/uvicorn',
    args: 'main:app --host 0.0.0.0 --port 8000',
    cwd: '/home/ubuntu/tds-virtual-assistant',
    env: {
      NODE_ENV: 'production'
    }
  }]
}
EOF

# Start application
pm2 start ecosystem.config.js
pm2 startup
pm2 save
```

#### Option B: AWS Lambda + API Gateway

For serverless deployment with automatic scaling.

**Step 1: Prepare Lambda Package**

```bash
# Create deployment package
mkdir lambda-deployment
cp -r *.py data/ lambda-deployment/
cd lambda-deployment

# Install dependencies for Lambda
pip install -r requirements.txt -t .

# Create Lambda handler
cat > lambda_handler.py << EOF
from mangum import Mangum
from main import app

handler = Mangum(app)
EOF

# Add mangum to requirements
echo "mangum" >> requirements.txt

# Create deployment zip
zip -r ../deployment.zip .
```

**Step 2: Deploy with AWS CLI**

```bash
# Create Lambda function
aws lambda create-function \
  --function-name tds-assistant \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
  --handler lambda_handler.handler \
  --zip-file fileb://deployment.zip \
  --timeout 30 \
  --memory-size 1024

# Set environment variables
aws lambda update-function-configuration \
  --function-name tds-assistant \
  --environment Variables='{
    "AIPROXY_API_KEY":"your_key",
    "TOGETHER_AI_API_KEY":"your_key"
  }'
```

**Step 3: Setup API Gateway**

```bash
# Create API Gateway
aws apigatewayv2 create-api \
  --name tds-assistant-api \
  --protocol-type HTTP \
  --target arn:aws:lambda:REGION:ACCOUNT:function:tds-assistant
```

## Project Structure

```
tds-virtual-assistant/
│
├── main.py                    # FastAPI application entry point
├── core.py                    # Core logic for embeddings and LLM
├── course.py                  # Course content search
├── discourse.py               # Forum discussion search
├── utils.py                   # Utility functions
├── requirements.txt           # Python dependencies
├── vercel.json               # Vercel deployment config
├── .env                      # Environment variables (create this)
│
├── data/                     # Processed data files
│   ├── course_index.faiss
│   ├── course_metadata.json
│   ├── discourse_index.faiss
│   └── discourse_metadata.json
│
├── raw-data/                 # Raw data processing
│   ├── fetched/             # Scraped forum data
│   ├── cleaned/             # Processed forum data
│   ├── cloned/              # Course repository clone
│   ├── topics.json          # Merged topics
│   ├── discussion.json      # Full discussions
│   └── course.json          # Structured course content
│
├── extra/                   # Additional processed files
│   ├── processed_course.json
│   └── processed_discussion.json
│
└── processing_scripts/      # Data processing pipeline
    ├── 1_topics_fetcher.py
    ├── 2_topics_cleaner.py
    ├── 3_topics_merger.py
    ├── 4_topics_answer.py
    ├── 5_content_merger.py
    ├── 6_topics_embedding.py
    └── 7_content_embedding.py
```

## Troubleshooting

### Common Issues

**1. Tesseract OCR not found**
```bash
# Install Tesseract and verify installation
tesseract --version

# If still failing, set path explicitly in code:
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
```

**2. FAISS index files not found**
```bash
# Ensure data files exist
ls -la data/
# Run embedding scripts if files are missing
python 6_topics_embedding.py
python 7_content_embedding.py
```

**3. API key errors**
```bash
# Verify environment variables
echo $AIPROXY_API_KEY
echo $TOGETHER_AI_API_KEY

# Or check .env file
cat .env
```

**4. Memory issues during embedding**
```bash
# Reduce batch size in embedding scripts
# Or use a machine with more RAM
```

### Performance Optimization

- **Vector Search**: Adjust FAISS index parameters for speed vs accuracy
- **Chunking**: Optimize chunk size and overlap for better context
- **Caching**: Implement response caching for repeated queries
- **Load Balancing**: Use multiple API keys for rate limit management

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions or issues:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review the API documentation at `/docs` endpoint

---

**Note**: Remember to keep your API keys secure and never commit them to version control. Use environment variables or secure secret management services in production.