import os
import argparse
import json
from tqdm import tqdm
from letta_client import Letta
from letta_client.types import MessageCreateParam
from tests.benchmarks.common.runner import BenchmarkRunner
from tests.benchmarks.common.utils import load_json, save_json, calculate_f1

def run_membench_real(args):
    client = Letta(base_url=args.base_url)
    
    if not os.path.exists(args.data_path):
        print(f"Data not found at {args.data_path}. Please download it first.")
        return

    data = load_json(args.data_path)
    # The real MemBench format (FirstAgent/simple.json) is:
    # { "roles": [ { "tid": 0, "message_list": [[...]], "QA": {...} }, ... ] }
    items = data.get("roles", [])
    
    if args.limit:
        items = items[:args.limit]
    
    results = []
    
    for item in tqdm(items, desc="Running MemBench Real"):
        tid = item.get("tid")
        message_list = item.get("message_list", [])
        qa = item.get("QA", {})
        
        agent = client.agents.create(
            name=f"membench_real_agent_{tid}",
            model=args.model,
            memory_blocks=[
                {"label": "persona", "value": "I am a helpful assistant with a perfect memory."},
                {"label": "human", "value": "I am a user sharing information with you."}
            ]
        )
        
        runner = BenchmarkRunner(client, agent.id)
        
        # Feed all messages in message_list
        # message_list is a list of lists of message objects
        for sub_list in message_list:
            for msg_obj in sub_list:
                user_msg = msg_obj.get("user_message")
                if user_msg:
                    runner.run_interaction(user_msg)
        
        # Now ask the question
        question = qa.get("question")
        ground_truth = qa.get("answer")
        
        if not question or not ground_truth:
            client.agents.delete(agent.id)
            continue
            
        response_messages = runner.run_interaction(f"Question: {question}\nAnswer briefly.")
        
        # Find prediction
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
            "tid": tid,
            "question": question,
            "ground_truth": ground_truth,
            "prediction": prediction,
            "f1": f1
        })
        
        client.agents.delete(agent.id)

    # Calculate aggregate metrics
    overall_f1 = sum(r['f1'] for r in results) / len(results) if results else 0
    
    print(f"\nMemBench Real Benchmark Summary:")
    print(f"Model: {args.model}")
    print(f"Overall F1 Score: {overall_f1:.4f}")
    
    if args.output_path:
        save_json({"summary": {"model": args.model, "overall_f1": overall_f1}, "details": results}, args.output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MemBench Real benchmark on Letta.")
    parser.add_argument("--base_url", type=str, default="http://localhost:8283", help="Letta server base URL")
    parser.add_argument("--data_path", type=str, default="tests/benchmarks/membench/data/MemData/FirstAgent/simple.json", help="Path to MemBench real dataset")
    parser.add_argument("--model", type=str, default="openai/gpt-4o-mini", help="Model to use for the agent")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of items to process")
    parser.add_argument("--output_path", type=str, default="tests/benchmarks/membench/results_real.json", help="Path to save results")
    
    args = parser.parse_args()
    run_membench_real(args)
