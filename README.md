# 🚀 Hybrid RAG System - 3-Day Pipeline

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/Glanzs-tech/Rag-Assignment)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/chromadb-latest-orange.svg)](https://www.trychroma.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Glanzs-tech/Rag-Assignment/pulls)

> **⚡ 3-DAY DEADLINE - BUILD HYBRID RAG SYSTEM** ⚡

![Hybrid RAG Architecture](https://via.placeholder.com/800x400/1f1f1f/ffffff?text=Hybrid+RAG+System+Architecture)

## 🔄 Getting Started - Fork & Contribute

### Step 1: Fork the Repository
1. **Fork** this repository by clicking the "Fork" button at the top right
2. **Clone** your forked repository:
```bash
git clone https://github.com/YOUR_USERNAME/Rag-Assignment.git
cd Rag-Assignment
```

### Step 2: Set Up Development Environment
```bash
# Add upstream remote
git remote add upstream https://github.com/Glanzs-tech/Rag-Assignment.git

# Create your feature branch
git checkout -b feature/your-feature-name

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Make Changes & Submit PR
```bash
# Make your changes and commit
git add .
git commit -m "feat: add your feature description"

# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# Go to your fork and click "New Pull Request"
```

### 🎯 PR Guidelines
- **Branch naming**: `feature/description` or `fix/issue-name`
- **Commit messages**: Use conventional commits (feat:, fix:, docs:)
- **Testing**: Ensure all tests pass before submitting
- **Documentation**: Update README if adding new features

## 🎯 Project Overview

Build a **Hybrid Retrieval-Augmented Generation (RAG)** system combining:
- 🔍 **Automated Query System** (PostgreSQL + BigQuery)
- 📚 **Document-Based Retrieval** (ChromaDB Vector Database)
- 🖥️ **Simple Streamlit UI**

## 📅 3-DAY PIPELINE

### 🔥 DAY 1: Query System & Database Setup
**Focus: Get data infrastructure running**

**Deliverables:**
- [ ] PostgreSQL setup and schema design
- [ ] BigQuery integration for analytics
- [ ] Basic query processing pipeline
- [ ] Database connections tested and working

**Key Tasks:**
- Set up PostgreSQL database with proper schema
- Configure BigQuery service account and datasets
- Build query preprocessing and routing logic
- Test all database connections

### 🔥 DAY 2: Document Retrieval with ChromaDB
**Focus: Vector database and document processing**

**Deliverables:**
- [ ] ChromaDB setup and configuration
- [ ] Document processing pipeline (PDF, TXT, DOCX)
- [ ] Vector embeddings and similarity search
- [ ] Hybrid search combining SQL + vector results

**Key Tasks:**
- Install and configure ChromaDB
- Build document chunking and embedding pipeline
- Implement semantic search with ChromaDB
- Create hybrid retrieval combining structured + vector data

### 🔥 DAY 3: Streamlit UI & Integration
**Focus: User interface and final integration**

**Deliverables:**
- [ ] Clean Streamlit interface
- [ ] Real-time query processing
- [ ] Document upload functionality
- [ ] Complete end-to-end system working

**Key Tasks:**
- Build intuitive Streamlit UI
- Connect frontend to backend systems
- Add file upload and processing
- Final testing and deployment

## 🏗️ System Architecture

```
User Query → Streamlit UI → Query Router
                              ↓
                    ┌─────────────────────┐
                    │   Hybrid Processor   │
                    └─────────────────────┘
                              ↓
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
   PostgreSQL            BigQuery              ChromaDB
  (Structured)          (Analytics)           (Documents)
        ↓                     ↓                     ↓
        └─────────────────────┼─────────────────────┘
                              ↓
                        RAG Engine → Response
```

## 🛠️ Technology Stack

### **Query System**
- **PostgreSQL**: Structured data storage and queries
- **BigQuery**: Large-scale analytics and data warehousing
- **SQLAlchemy**: Database ORM and connection management

### **Document Retrieval**
- **ChromaDB**: Vector database for document embeddings
- **Sentence-Transformers**: Text embeddings (all-MiniLM-L6-v2)
- **LangChain**: Document processing and text splitting

### **UI & Integration**
- **Streamlit**: Web interface
- **Python**: Backend processing
- **Docker**: Containerization

## ⚡ Quick Setup

### 1. Clone Repository
```bash
git clone https://github.com/Glanzs-tech/Rag-Assignment.git
cd Rag-Assignment
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create `.env` file:
```env
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_system
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=your_password

# BigQuery
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
BIGQUERY_PROJECT_ID=your-project-id
BIGQUERY_DATASET=rag_analytics

# ChromaDB (local by default)
CHROMA_DB_PATH=./chroma_db
```

### 4. Database Setup
```bash
# Start PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_DB=rag_system \
  -e POSTGRES_USER=rag_user \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 postgres:15

# Initialize database
python scripts/init_database.py
```

### 5. Run Application
```bash
streamlit run app.py
```

## 📦 Required Dependencies

```txt
streamlit>=1.28.0
chromadb>=0.4.0
psycopg2-binary>=2.9.0
google-cloud-bigquery>=3.11.0
sqlalchemy>=2.0.0
langchain>=0.0.300
sentence-transformers>=2.2.0
pandas>=2.0.0
numpy>=1.24.0
python-dotenv>=1.0.0
```

## 🎮 Usage Examples

### Query Types

**1. Structured Data Query**
```
Input: "Show me all users registered last month"
→ Routes to PostgreSQL
→ Returns structured results
```

**2. Document Search**
```
Input: "Find documents about machine learning best practices"
→ Routes to ChromaDB
→ Returns relevant document chunks
```

**3. Analytics Query**
```
Input: "What are the trending topics this quarter?"
→ Routes to BigQuery
→ Returns analytical insights
```

**4. Hybrid Query**
```
Input: "Show user feedback about our ML models"
→ Combines PostgreSQL + ChromaDB
→ Returns structured data + relevant documents
```

## 📁 Project Structure

```
rag-assignment/
├── app.py                    # Main Streamlit app
├── src/
│   ├── database/
│   │   ├── postgres.py       # PostgreSQL operations
│   │   └── bigquery.py       # BigQuery operations
│   ├── retrieval/
│   │   ├── chromadb_client.py # ChromaDB operations
│   │   └── embeddings.py     # Text embedding utilities
│   ├── processing/
│   │   ├── query_router.py   # Query routing logic
│   │   └── document_processor.py # Document processing
│   └── ui/
│       └── streamlit_components.py # UI components
├── scripts/
│   ├── init_database.py      # Database initialization
│   └── load_documents.py     # Document loading utility
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
└── docker-compose.yml       # Docker setup
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Access application at http://localhost:8501
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export POSTGRES_HOST=your_host
export BIGQUERY_PROJECT_ID=your_project

# Run application
streamlit run app.py --server.port 8501
```

## 📊 Performance Targets

| Component | Target Performance |
|-----------|-------------------|
| PostgreSQL Queries | < 100ms |
| ChromaDB Search | < 500ms |
| BigQuery Analytics | < 2s |
| End-to-End Response | < 3s |
| Document Processing | 100 docs/min |

## 🔧 Development Tips

### ChromaDB Best Practices
- Use persistent storage for production
- Batch document insertions for better performance
- Choose appropriate embedding model for your domain
- Implement proper error handling for vector operations

### Query Optimization
- Index frequently queried PostgreSQL columns
- Use BigQuery partitioning for large datasets
- Cache common ChromaDB queries
- Implement connection pooling

## 🎯 Success Criteria

### Day 1 ✅
- [ ] PostgreSQL connected and queryable
- [ ] BigQuery integration working
- [ ] Basic query routing implemented

### Day 2 ✅
- [ ] ChromaDB storing and retrieving documents
- [ ] Document processing pipeline functional
- [ ] Hybrid search combining all data sources

### Day 3 ✅
- [ ] Streamlit UI fully functional
- [ ] File upload and processing working
- [ ] Complete system deployed and accessible

## 🆘 Troubleshooting

### Common Issues

**ChromaDB Connection Error**
```bash
# Reset ChromaDB
rm -rf ./chroma_db
python scripts/init_chromadb.py
```

**PostgreSQL Connection Failed**
```bash
# Check connection
psql -h localhost -U rag_user -d rag_system
```

**BigQuery Authentication Error**
```bash
# Verify service account
gcloud auth application-default login
```

## 📈 Future Enhancements

- [ ] Multi-language document support
- [ ] Advanced analytics dashboard
- [ ] User authentication and sessions
- [ ] API endpoints for external integration
- [ ] Automated document ingestion pipeline

---

## 🏁 DEADLINE REMINDER

```
🚨 3-DAY SPRINT TIMELINE 🚨

Day 1: Database & Query System
Day 2: ChromaDB & Document Retrieval  
Day 3: Streamlit UI & Deployment

KEEP IT SIMPLE. MAKE IT WORK. SHIP IT! 🚀
```

![Success](https://via.placeholder.com/600x200/00ff00/ffffff?text=RAG+SYSTEM+DEPLOYED+SUCCESSFULLY!)

---

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository to your GitHub account
2. **Clone** your fork locally and set up the development environment
3. **Create** a feature branch from `main` for your changes
4. **Implement** your changes following the 3-day pipeline structure
5. **Test** your implementation thoroughly
6. **Submit** a Pull Request with clear description and screenshots

### PR Requirements Checklist
- [ ] Code follows the established project structure
- [ ] All existing tests pass
- [ ] New features include appropriate tests
- [ ] Documentation updated (README, code comments)
- [ ] Feature works end-to-end in the Streamlit UI
- [ ] No breaking changes to existing functionality
- [ ] Follows conventional commit message format

### Code Standards
- **Python**: Follow PEP 8 style guidelines
- **Commits**: Use conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`)
- **Branches**: Use descriptive names (`feature/chromadb-optimization`, `fix/postgres-connection`)
- **Documentation**: Update relevant sections when adding features

### Testing Your Changes
```bash
# Run basic functionality tests
python -m pytest tests/

# Test Streamlit app locally
streamlit run app.py

# Verify database connections
python scripts/test_connections.py
```

### Review Process
- PRs will be reviewed within 24 hours
- Address feedback promptly and professionally
- Maintain clean commit history (squash if needed)
- Ensure CI/CD checks pass before requesting review

### Getting Help
- **Issues**: [Report bugs or request features](https://github.com/Glanzs-tech/Rag-Assignment/issues)
- **Discussions**: [Join community discussions](https://github.com/Glanzs-tech/Rag-Assignment/discussions)
- **Pull Requests**: [View open PRs](https://github.com/Glanzs-tech/Rag-Assignment/pulls)

---

**Built with ❤️ | [Glanzs-tech](https://github.com/Glanzs-tech)**