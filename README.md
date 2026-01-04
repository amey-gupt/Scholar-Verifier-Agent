# Scholar-Verifier-Agent

An agentic relevance filter for scientific literature search. Unlike standard search engines that rely on keyword matching, this agent uses an LLM to read abstracts in real-time and verify semantic intent.

## The Problem
Standard retrieval (e.g., Google Scholar) optimizes for **recall**, often returning irrelevant papers that share keywords with the query but differ in context.

## The Solution
This agent implements an **LLM-as-a-Judge** workflow:
1. **Broad Retrieval:** Fetches raw candidates via the Semantic Scholar API.
2. **Agentic Verification:** Uses **Google Gemini 2.5 Flash-Lite** to read every abstract.
3. **Reasoning Loop:**
   - Assigns a relevance score (0-10).
   - Extracts specific **evidence sentences** supporting the match.
   - Rejects "lexical decoys" (papers with right words, wrong meaning).
4. **Visual Output:** Displays a "Green/Red" acceptance panel for transparent decision-making.

## Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Set API Key: `export GEMINI_API_KEY='...'`
3. To run the agent with the live "thinking" visualization, ensure the main block in verifier.py calls run_workflow_verbose
4. Run the agent: `python verifier.py`

## Project Report
For a detailed architectural analysis and comparison with Google Scholar, see the full report: