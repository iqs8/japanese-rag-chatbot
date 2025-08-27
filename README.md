# 📘 Language Learning Rag Chatbot

A **local Retrieval-Augmented Generation (RAG)** application for language learning, built with **Streamlit** and powered by local models via **Ollama**.

## 🎯 Purpose

This project was created to:
- Get hands-on experience with **running local language models**
- Explore whether **RAG could enhance Japanese language learning**
- Build a **privacy-focused alternative** to cloud-based language tutors
- Demonstrate a **proof-of-concept** for secure, offline language learning tools

> **Note**: While GPT and other cloud models are still superior for language learning, this approach offers better **privacy and security** when working with sensitive data.

## 🔧 How It Works

### RAG Pipeline Overview
1. **Question Input**: User asks a question about Japanese grammar or vocabulary
2. **Vector Search**: ChromaDB performs similarity search on stored Genki textbook chunks
3. **Context Retrieval**: Most relevant content is retrieved (with lesson/sublesson filtering)
4. **Enhanced Query**: Retrieved context is added to the user's question
5. **Local Generation**: Qwen model generates response using both question and context
6. **Source Verification**: App displays retrieved chunks so you can verify the information

### Why Vector Search?
The **local model alone struggles** with specific Japanese grammar questions. By storing textbook content as vectors and retrieving relevant context, we **dramatically improve response quality**. The vector database allows semantic similarity matching, so asking about "te-form" will find relevant content even if the exact term isn't in your question.

### Smart Filtering
While the app uses vector similarity search, it also includes **lesson/sublesson filtering** for more precise results. You can:
- **Specify lessons in your question**: `"lesson 3 sublesson 2 te-form"`
- **Use sidebar filters** to override and focus on specific content
- **Get the right content** almost every time due to structured metadata

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
   git clone <your-repo-url>
   cd japanese-rag-tutor
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

## 📚 Data & Content

### Current Data
The app comes with **Genki 1 textbook content** (`Data/Genki1.json`) that has been:
- ✅ **Extracted from textbook images** using Claude AI (OCR libraries didn't work well with the textbook format)
- ✅ **Chunked into manageable pieces**
- ✅ **Enhanced with metadata** (lesson, sublesson, topic, chunk_id)

### Adding Your Own Data
1. **Place your JSON files** in the `Data/` folder
2. **Ensure they follow this structure**:
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
3. **Update `GENKI_PATH`** in `main.py` to point to your file
4. **Use the "🧹 Wipe & Rebuild" button** to ingest new data

## ⚙️ Features

### 🔍 Smart Context Retrieval
- **Semantic search** through Japanese learning content
- **Lesson and sublesson filtering**
- **Source material verification** - see exactly what content was used

### 💬 Interactive Learning
- **Multi-turn conversations** with memory
- **Streaming responses** for better UX
- **Source citations** with expandable content

### 🎛️ Flexible Controls
- **Force reset functionality** for development
- **Sidebar filters** for precise content targeting
- **Model configuration** options

### ✅ Verification & Trust
- Shows **retrieved chunks and their metadata**
- Displays **number of sources used**
- **Expandable source content** for fact-checking

## 🔄 Force Reset Options

If you need to rebuild the database:

1. **UI Reset**: Use the "🧹 Wipe & Rebuild Chroma Collection" button in the sidebar
2. **Code Reset**: Set `FORCE_RESET = True` in `main.py`
3. **Environment Reset**: 
   ```bash
   FORCE_RESET=1 streamlit run main.py
   ```

## 🗂️ Project Structure

```
japanese-rag-tutor/
├── chroma_db/          # Vector database storage
├── Data/               # Source data files
│   └── Genki1.json    # Genki textbook content
├── main.py            # Main application logic
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## ⚠️ Limitations & Future Work

### Current Limitations
- 🔸 **Local models still lag behind GPT/Claude** for language learning
- 🔸 **OCR extraction method limits content quality**
- 🔸 **Only Genki 1 content** currently included
- 🔸 **Vector search accuracy varies** with Japanese content

### Future Improvements
- 🔧 Explore **better OCR methods** for textbook digitization
- 📚 Add support for **multiple textbooks** (Genki 2, Tobira)
- 🎛️ Implement **textbook filtering functionality**
- 🧪 Experiment with **different embedding models**
- 💾 Add **conversation export/import**

## 🎥 Demo

*YouTube demo video will be added here*

---

> **⚠️ Important Note**: This is a **proof-of-concept** for educational and portfolio purposes. For serious Japanese language learning, consider using it alongside more powerful cloud-based models while leveraging this tool's **privacy benefits**.

## 🤝 Contributing

Feel free to **fork this project** and submit pull requests! This is primarily a learning/portfolio project, but improvements are welcome.
