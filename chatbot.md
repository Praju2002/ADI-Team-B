# Chatbot Mechanism Documentation

This document outlines the architecture, components, and data flow of the chatbot implemented in this project.

## Overview

The chatbot is designed to answer questions about the datasets loaded in the dashboard. It uses a **Retrieval-Augmented Generation (RAG)** approach, where relevant data rows are retrieved from the dataframes and passed to a Large Language Model (LLM) to generate a natural language answer. Additionally, it performs **automated data analysis** to provide deterministic insights and visualizations.

## Architecture

The system consists of three main layers:

1.  **Frontend (UI)**: Built with Streamlit, handling user input, displaying chat history, and rendering visualizations.
2.  **Middleware (Logic)**: Handles data indexing, retrieval, prompt construction, and statistical analysis.
3.  **Backend (LLM)**: Interfaces with external LLM APIs (primarily **Groq**, with fallback support for Google Generative AI and OpenAI) to generate responses.

## Components

### 1. User Interface (`pages/4_Chatbot.py`)
-   **Page Config**: Sets up the page layout and custom CSS for a modern, pastel design.
-   **Sidebar**: Hidden from the main navigation but accessible via the floating button. Contains settings for API keys, retriever `top_k`, and an option to rebuild the index.
-   **Chat History**: Maintains a session-state based history of questions, answers, insights, and sources.
-   **Input Handling**: Accepts user queries and suggested example questions.
-   **Graph Rendering**: Executes Python code returned by the LLM to render interactive Plotly charts.

### 2. Core Logic (`utils/chatbot.py`)
This module handles the heavy lifting:
-   **Indexing**:
    -   Converts dataframe rows into text strings (e.g., "col1: val1 | col2: val2").
    -   Uses `sklearn.feature_extraction.text.TfidfVectorizer` to create a TF-IDF index of these rows.
    -   Persists the index (vectorizer, documents, sparse matrix) to `Raw_Data/processed/chat_index/` to avoid rebuilding it on every reload.
-   **Retrieval (`get_top_docs`)**:
    -   Converts the user's query into a TF-IDF vector.
    -   Computes cosine similarity between the query vector and the document vectors.
    -   Returns the top `k` most similar rows (documents).
-   **Prompt Engineering (`_build_prompt`)**:
    -   Constructs a prompt containing system instructions, retrieved context, and the user query.
    -   Includes specific instructions and table schemas for generating Python/Plotly graph code if requested.

### 3. Navigation (`utils/floating_button.py`)
-   Injects a fixed floating button (💬) on the bottom-right of every page.
-   Uses CSS to style the button and hide the Chatbot page from the standard Streamlit sidebar navigation.
-   Clicking the button navigates the user to the Chatbot page.

## Data Analysis Mechanism

The chatbot implements a dual-layer analysis approach to ensure accuracy and utility:

### 1. Deterministic Statistical Analysis (`summarize_docs_insights`)
Independent of the LLM, the system performs direct analysis on the retrieved data rows to prevent "hallucinations" on numbers.
-   **Parsing**: Converts the text representation of retrieved rows back into structured dictionaries.
-   **Numeric Analysis**: Identifies numeric columns and calculates key statistics:
    -   **Average**
    -   **Sum**
    -   **Minimum**
    -   **Maximum**
-   **Categorical Analysis**: Identifies categorical columns and determines the **Top Value** (mode) and its frequency.
-   **Presentation**: These insights are displayed in a "Success" box in the UI, providing immediate, fact-based summaries (e.g., "avg_Revenue: 5000", "top_Country: Uganda").

### 2. LLM-based Visualization
The system instructs the LLM to generate Python code for visual analysis.
-   **Aggregation**: The prompt explicitly instructs the LLM to aggregate data (using `groupby`, `sum`, `mean`) before plotting, suitable for large datasets.
-   **Plotting**: The LLM generates `plotly.express` code.
-   **Execution**: The UI safely executes this code in a local scope to render interactive charts.

## LLM Integration

The system is designed to support multiple LLM providers, with a specific prioritization logic:

1.  **Groq (Llama 3)**: This is the **primary** backend. The system checks for a `GROQ_API_KEY` or a key starting with `gsk_`.
2.  **OpenAI (GPT-3.5-Turbo)**: Used if an OpenAI API key (starting with `sk-`) is provided.
3.  **Google Generative AI (Text-Bison)**: Used as a default fallback if other keys are not present.

## Data Flow

1.  **Initialization**: App loads data and checks/builds the TF-IDF index.
2.  **User Query**: User asks a question.
3.  **Retrieval**: System finds top `k` relevant rows.
4.  **Analysis**:
    -   System computes **Deterministic Insights** from rows.
    -   LLM generates **Answer** and optional **Graph Code**.
5.  **Display**: UI shows the Question, Insight Box, Answer, and Graph.

## Setup & Configuration

-   **Dependencies**: `scikit-learn`, `pandas`, `numpy`, `scipy`, `requests`, `plotly`, `streamlit`.
-   **Index Storage**: `Raw_Data/processed/chat_index/`.
