import os
import json
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.progress import track
from semanticscholar import SemanticScholar
from dotenv import load_dotenv
import requests
import time
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

console = Console()

class RelevanceVerifier:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.sch = SemanticScholar()

    def search_papers(self, query: str, limit: int = 10) -> List[Dict]:
        """Fetches raw papers from Semantic Scholar."""
        console.print(f"[bold blue]🔍 Searching Semantic Scholar for: '{query}'...[/bold blue]")

        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,abstract,year,url"
        }

        for attempt in range(5):
            r = requests.get(url, params=params, timeout=20)

            if r.status_code == 429:
                wait = 2 ** attempt
                console.print(f"[yellow]⚠ Rate limited. Retrying in {wait}s...[/yellow]")
                time.sleep(wait)
                continue

            r.raise_for_status()
            payload = r.json()
            data = payload.get("data", [])

            console.print(f"[yellow]Debug: API returned {len(data)} raw results.[/yellow]")
            
            papers = [
                {
                    "title": p.get("title"),
                    "abstract": p.get("abstract"),
                    "year": p.get("year"),
                    "url": p.get("url")
                }
                for p in data
                if p.get("abstract")
            ]

            console.print(f"[green]✔ Found {len(papers)} papers with abstracts.[/green]\n")
            return papers

        raise RuntimeError("Semantic Scholar rate limit exceeded after retries")

    def evaluate_relevance(self, query: str, paper: Dict) -> Dict:
        """
        Uses Gemini Native API to score relevance.
        """
        prompt = f"""
        You are a strict scientific reviewer. Analyze the abstract below for the query: "{query}".
        
        Return a valid JSON object with these exact keys:
        - "score": A specific integer from 0-10 (10 = perfect match).
        - "is_relevant": Boolean (True if score > 5).
        - "evidence": The EXACT sentence from the abstract that justifies the score. If none, return null.
        - "reasoning": A 10-word explanation.

        Abstract: {paper['abstract']}
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return {"score": 0, "is_relevant": False, "evidence": None, "reasoning": "Error"}

    def run_workflow(self, query: str):
        # Step 1: Get Raw Data
        raw_papers = self.search_papers(query)
        
        # Step 2: Agentic Verification Loop
        verified_papers = []
        
        for paper in track(raw_papers, description="[yellow]🤖 Verifying papers...[/yellow]"):
            analysis = self.evaluate_relevance(query, paper)
            
            if analysis['is_relevant']:
                paper['score'] = analysis['score']
                paper['evidence'] = analysis['evidence']
                paper['reasoning'] = analysis['reasoning']
                verified_papers.append(paper)

        # Step 3: Display Results
        self.display_results(query, verified_papers)

    def display_results(self, query: str, papers: List[Dict]):
        table = Table(title=f"🎓 Verified Evidence for: {query}")

        table.add_column("Score", style="magenta", justify="center")
        table.add_column("Title", style="cyan", no_wrap=True)
        table.add_column("Extracted Evidence", style="green")

        papers.sort(key=lambda x: x['score'], reverse=True)

        for p in papers:
            table.add_row(
                str(p['score']),
                p['title'][:50] + "...",
                f"\"{p['evidence']}\"" if p['evidence'] else "[dim]No direct quote[/dim]"
            )

        console.print("\n")
        console.print(table)
        console.print(f"\n[bold]Summary:[/bold] Filtered {len(papers)} relevant papers from raw search.")


if __name__ == "__main__": 
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        console.print("[red]Error: Please set GEMINI_API_KEY environment variable.[/red]")
    else:
        agent = RelevanceVerifier(api_key)
        agent.run_workflow("IMU camera synchronization cross-correlation")