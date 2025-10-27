import os
import time
from typing import Dict, List

import llm_adapter
from intent_classifier import classify_intent

# A list of prompts to test the AI systems with
BENCHMARK_PROMPTS = {
    "coding": [
        "How do I write a function in Python to reverse a string?",
        "What is the difference between a list and a tuple in Python?",
        "How do I handle exceptions in Java?",
    ],
    "writing": [
        "Summarize the following text: [insert text here]",
        "Rewrite the following sentence to be more concise: [insert sentence here]",
        "What are some synonyms for the word 'important'?",
    ],
    "design": [
        "What are some best practices for designing a mobile app?",
        "What are some popular color palettes for web design?",
        "How can I create a user-friendly navigation menu?",
    ],
}

def run_benchmark(provider: str, api_key: str) -> Dict:
    """
    Runs a benchmark test for the specified AI provider.

    Args:
        provider (str): The AI provider to test (e.g., 'openai', 'gemini').
        api_key (str): The API key for the AI provider.

    Returns:
        Dict: A dictionary containing the benchmark results.
    """
    results = {
        "provider": provider,
        "total_time": 0,
        "total_prompts": 0,
        "responses": [],
    }

    for intent, prompts in BENCHMARK_PROMPTS.items():
        for prompt in prompts:
            start_time = time.time()
            conversation = [
                {"role": "system", "content": f"You are a helpful AI assistant specializing in {intent}."},
                {"role": "user", "content": prompt},
            ]
            response = "".join(llm_adapter.analyze_code(conversation, provider=provider, api_key=api_key))
            end_time = time.time()

            results["total_time"] += end_time - start_time
            results["total_prompts"] += 1
            results["responses"].append(
                {
                    "intent": intent,
                    "prompt": prompt,
                    "response": response,
                    "time": end_time - start_time,
                }
            )

    return results

if __name__ == "__main__":
    # NOTE: This is a placeholder for a more sophisticated implementation.
    # You will need to replace 'YOUR_API_KEY' with your actual API key if not set as an environment variable.
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("GEMINI_API_KEY environment variable not set. Please set it to run the benchmark.")
    else:
        gemini_results = run_benchmark("gemini", gemini_api_key)
        print("\nGemini Benchmark Results:")
        print(gemini_results)
