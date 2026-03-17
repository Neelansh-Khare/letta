import os
import argparse
import json
from tqdm import tqdm
from letta_client import Letta
from letta_client.types import MessageCreateParam
from tests.benchmarks.common.runner import BenchmarkRunner
from tests.benchmarks.common.utils import load_json, save_json, calculate_f1

def run_longmemeval(args):
    client = Letta(base_url=args.base_url)
    
    if not os.path.exists(args.data_path):
        print(f"Data not found at {args.data_path}. Please download it first.")
        return

    # Note: LongMemEval data can be very large, we may need to stream it or limit it
    # For now, we'll try to load it into memory if it's not too huge, but args.limit is recommended
    data = load_json(args.data_path)
    
    if args.limit:
        data = data[:args.limit]
    
    results = []
    
    for item_idx, item in enumerate(tqdm(data, desc="Processing LongMemEval items")):
        # Create a new agent for each long-term memory scenario
        agent = client.agents.create(
            name=f"longmem_agent_{item_idx}",
            model=args.model,
            memory_blocks=[
                {"label": "persona", "value": "I am a helpful assistant with a perfect memory and long-term context recall."},
                {"label": "human", "value": "I am a user engaged in a long-term conversation with you."}
            ]
        )
        
        runner = BenchmarkRunner(client, agent.id)
        
        # Feed the haystack_sessions
        # LongMemEval has multiple sessions which can be quite long.
        for session in item['haystack_sessions']:
            # Preload the entire session's messages efficiently
            runner.bulk_add_messages(session, args.model)
        
        # Evaluate the question
        question = item['question']
        ground_truth = item['answer']
        
        # Ask the final question
        response_messages = runner.run_interaction(f"Final Question based on our entire history: {question}\nAnswer briefly.")
        
        # Extract prediction
        prediction = ""
        for m in reversed(response_messages):
            if hasattr(m, 'content') and m.content:
                if isinstance(m.content, str):
                    prediction = m.content
                    break
                elif isinstance(m.content, list):
                    prediction = " ".join([c.text for c in m.content if hasattr(c, 'text')])
                    break
        
        f1 = calculate_f1(prediction, str(ground_truth))
        
        results.append({
            "item_idx": item_idx,
            "question": question,
            "ground_truth": ground_truth,
            "prediction": prediction,
            "f1": f1
        })
        
        # Cleanup
        client.agents.delete(agent.id)

    # Aggregate
    overall_f1 = sum(r['f1'] for r in results) / len(results) if results else 0
    
    summary = {
        "model": args.model,
        "overall_f1": overall_f1,
        "items_processed": len(results)
    }
    
    print(f"\nLongMemEval Benchmark Summary:")
    print(f"Model: {args.model}")
    print(f"Overall F1 Score: {overall_f1:.4f}")
    
    if args.output_path:
        save_json({"summary": summary, "details": results}, args.output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LongMemEval benchmark on Letta.")
    parser.add_argument("--base_url", type=str, default="http://localhost:8283", help="Letta server base URL")
    parser.add_argument("--data_path", type=str, default="tests/benchmarks/longmemeval/data/longmemeval_s_cleaned.json", help="Path to LongMemEval JSON")
    parser.add_argument("--model", type=str, default="openai/gpt-4o-mini", help="Model to use for the agent")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of items to process")
    parser.add_argument("--output_path", type=str, default="tests/benchmarks/longmemeval/results.json", help="Path to save results")
    
    args = parser.parse_args()
    run_longmemeval(args)
