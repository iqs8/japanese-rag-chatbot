# 🤖 Japanese Learning RAG Chatbot

A **local Retrieval-Augmented Generation (RAG)** chatbot for Japanese language learning, built with **Streamlit** and powered by **Qwen3:1.7b** via **Ollama**.

## 🧠 Context

**RAG (Retrieval-Augmented Generation)** enhances language models by providing relevant context from a knowledge base before generating responses. This approach is particularly valuable for domain-specific knowledge, privacy, consistency, and source verification.

I created this project while learning Japanese to test how a smaller model (Qwen3:1.7b - chosen for its strong Japanese language performance) would work with the exact textbook content I was studying. The concept can be applied to any language or topic by uploading relevant data to the system.

## 🔧 How It Works

### RAG Pipeline Overview
1. **Question Input**: User asks a question about Japanese grammar or vocabulary
2. **Vector Search**: ChromaDB performs similarity search on stored Genki textbook chunks
3. **Context Retrieval**: Most relevant content is retrieved (with lesson/sublesson filtering)
4. **Enhanced Query**: Retrieved context is added to the user's question
5. **Local Generation**: Qwen model generates response using both question and context
6. **Source Verification**: App displays retrieved chunks so you can verify the information



### Smart Filtering
**Textbook content presents unique challenges for semantic matching** - the same basic grammar points appear across multiple lessons with similar vocabulary and explanations, making it difficult for vector similarity to distinguish between them. This is unlike querying a story where events have distinct contexts and locations.

To address this, the system includes **intelligent filtering**:

- **Specify lessons in your question**: `"lesson 3 sublesson 2 te-form"`
- **Use sidebar filters** to override and focus on specific content  
- **Structured metadata filtering** ensures you get content from the right lesson/sublesson
- **Hybrid approach**: Combines semantic search with precise content filtering for better results

## 🚀 Prerequisites

1. **Ollama Installation**: Install [Ollama](https://ollama.ai/) for running local models
2. **Model Setup**: Pull the required model:
   ```bash
   ollama pull qwen3:1.7b
   ```
3. **Start Ollama Service**:
   ```bash
   ollama serve
   ```

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/iqs8/lang-rag-chatbot.git
   cd lang-rag-chatbot
   ```

2. **Install Python dependencies**:
   ```bash
   pip install streamlit langchain-chroma langchain-huggingface chromadb ollama pathlib
   ```

3. **Run the application**:
   ```bash
   streamlit run main.py
   ```

4. **Open your browser** to `http://localhost:8501`

## 🔧 Important Setup Notes

- **No database included**: The `chroma_db/` folder is not in the repository and will be created automatically
- **Auto-population**: On first run, the app checks if the "genki" collection exists and is populated
- **Smart initialization**: If the collection is empty, it automatically ingests data from `Data/Genki1.json`
- **Force reset**: The reset button wipes the database and clears the cache, triggering re-population on next query *(see Features section for more details)*

## 📚 Data & Content

### Current Data
The app pulls from **Genki 1 textbook content** (`Data/Genki1.json`) structured with metadata:
- ✅ **Chunked educational content** from the Genki Japanese textbook series
- ✅ **Enhanced with metadata** (lesson, sublesson, topic, chunk_id)
- ✅ **Ready for semantic search and filtering**

### Adding Your Own Data
1. **Prepare your content**: Chunk your data and create embeddings using an embedding model
2. **Follow the JSON structure**:
   ```json
   [
     {
       "text": "Content text here",
       "lesson": 1,
       "sublesson": 1,
       "topic": "Topic name",
       "chunk_id": "unique_id"
     }
   ]
   ```
3. **Update paths and names**: Modify `GENKI_PATH` and `COLLECTION_NAME` in `main.py` for your data
4. **Multiple data sources**: Consider modifying the force reset check to handle multiple collections
5. **Use the reset function** to ingest new data

## ⚙️ Features

### 🔍 Smart Context Retrieval
- **Semantic search** through educational content
- **Sidebar filters** for lesson/sublesson targeting
- **Source material verification** - see exactly what content was used
- **Hybrid filtering** to overcome limitations of pure vector similarity

### 🔄 Force Reset Functionality
- **UI Reset**: Use the "🧹 Wipe & Rebuild Chroma Collection" button in the sidebar
- **Code Reset**: Set `FORCE_RESET = True` in `main.py`  
- **Environment Reset**: `FORCE_RESET=1 streamlit run main.py`

**What it does**: 
- **Clears Streamlit cache** for all cached functions (Streamlit's resource management system)
- **Wipes the vector database** completely
- **Re-initializes everything** on the next query or app restart
- **Useful for**: Adding new data chunks to your JSON files while the app is running

## 🗂️ Project Structure

```
lang-rag-chatbot/
├── chroma_db/          # Vector database storage
├── Data/               # Source data files
│   └── Genki1.json    # Genki 1 textbook content
├── main.py            # Main application logic
├── .gitignore         # Git ignore rules
└── README.md          # This file
```


---


