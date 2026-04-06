import argparse
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run_lab import cmd_dalat_compare
from tests.test_prompts import PROMPTS_LIST

def main():
    print(f"Loaded {len(PROMPTS_LIST)} test prompts.")
    
    for i, prompt in enumerate(PROMPTS_LIST):
        print("\n" + "="*50)
        print(f"RUNNING TEST {i+1} / {len(PROMPTS_LIST)}")
        print(f"PROMPT: {prompt}")
        print("="*50 + "\n")
        
        args = argparse.Namespace(
            question=prompt,
            provider=None, # Will default to DEFAULT_PROVIDER from .env (gemini-2.5-flash)
            model=None
        )
        
        try:
            cmd_dalat_compare(args)
        except Exception as e:
            print(f"\n[!] Error occurred during test: {e}")
            if "429" in str(e) or "Quota" in str(e):
                print(f"[!] Hit API rate limit on Test {i+1}!")
                
        # API quotas limit free tiers (like Gemini) to a few requests per minute.
        # So we add a delay between test cases to prevent instant crashing.
        if i < len(PROMPTS_LIST) - 1:
            print("\nSleeping for 60 seconds to avoid API Rate Limits...")
            time.sleep(60)

if __name__ == "__main__":
    main()
