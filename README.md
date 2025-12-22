# Scholar-Evidence-Ranker

An agentic relevance filter for scientific literature search. It doesn't just check for keywords, but uses an LLM to extract specific sentences that support the query.

## 🚀 The Problem
Standard keyword search (e.g., Google Scholar) often returns papers that contain the right keywords but the wrong context (e.g., "cross-correlation" in *Dance* vs. *Robotics*).

## 🤖 The Solution
This agent acts as a **Relevance Verifier**. It:
1. Fetches raw abstracts via Semantic Scholar.
2. Uses an LLM to read each abstract.
3. Extracts specific **evidence sentences** that support the query.
4. Reranks papers based on evidence quality, filtering out hallucinations and noise.

## 🛠️ Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Set API Key: `export GEMINI_API_KEY='...'`
3. Run the agent: `python verifier.py`