# Prototype: Hybrid Query Processing with Structured & Unstructured Data

## Overview
This project is an **early prototype** for building a system that can process both **structured** and **unstructured** data.  
The goal is to enable hybrid search and retrieval by combining vector embeddings with traditional databases.  

⚠️ **Note:** This is an incomplete prototype and does not yet achieve the full requirements.  

---

## Current Implementation

### 🔹 Unstructured Data
- Used **Sentence Transformers** for generating embeddings.
- Stored embeddings in **ChromaDB** for vector similarity search.
- Queries are checked against ChromaDB to retrieve relevant unstructured information.

### 🔹 Structured Data
- **PostgreSQL** (PSQL) used for relational structured data.
- **Google BigQuery** used for large-scale structured data queries.
- Query routing logic decides whether to use **PSQL** or **BigQuery** based on:
  - **Keyword-based rules**
  - **Complexity calculation**

### 🔹 Query Processing
- Simple **keyword matching** for handling general semantic queries (e.g., greetings like `"hello"`).
- **LLM-based query generation** to form SQL/BigQuery queries for structured data retrieval.
- Hybrid flow:
  1. Check unstructured DB (ChromaDB) for relevant information.
  2. If structured data is needed, route query to PSQL or BigQuery.
  3. Combine results into a single response.

### 🔹 Response
- The final response is an **object** containing:
  - Retrieved **structured data**
  - Retrieved **unstructured data**

---

## Limitations
- This is a **prototype** and not efficient.
- Routing logic and query generation need improvement.
- Retrieval accuracy is limited.


