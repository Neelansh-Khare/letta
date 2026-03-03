import os
import argparse
import json
from tqdm import tqdm
from letta_client import Letta
from tests.benchmarks.common.runner import BenchmarkRunner
from tests.benchmarks.common.utils import load_json, save_json, calculate_f1

def create_synthetic_membench():
    """Creates a synthetic MemBench dataset for testing store, retrieve, update, delete."""
    data = [
        {
            "id": "task_1",
            "name": "Basic Memory Operations",
            "steps": [
                {
                    "operation": "store",
                    "input": "My favorite color is blue.",
                    "thought": "Storing favorite color."
                },
                {
                    "operation": "retrieve",
                    "input": "What is my favorite color?",
                    "expected": "blue"
                },
                {
                    "operation": "update",
                    "input": "Actually, I changed my mind. My favorite color is now green.",
                    "thought": "Updating favorite color."
                },
                {
                    "operation": "retrieve_updated",
                    "input": "What is my favorite color now?",
                    "expected": "green"
                },
                {
                    "operation": "delete",
                    "input": "Please forget what my favorite color is.",
                    "thought": "Deleting favorite color from memory."
                },
                {
                    "operation": "retrieve_deleted",
                    "input": "What is my favorite color?",
                    "expected_not": "green"
                }
            ]
        },
        {
            "id": "task_2",
            "name": "Factual Memory - Person Info",
            "steps": [
                {
                    "operation": "store",
                    "input": "My friend Alice works at Google as a Software Engineer.",
                    "thought": "Storing info about Alice."
                },
                {
                    "operation": "retrieve",
                    "input": "Where does Alice work?",
                    "expected": "Google"
                },
                {
                    "operation": "retrieve",
                    "input": "What is Alice's job title?",
                    "expected": "Software Engineer"
                },
                {
                    "operation": "update",
                    "input": "Alice recently got a new job at Meta as a Product Manager.",
                    "thought": "Updating Alice's job info."
                },
                {
                    "operation": "retrieve_updated",
                    "input": "Where does Alice work now?",
                    "expected": "Meta"
                },
                {
                    "operation": "retrieve_updated",
                    "input": "What is Alice's new job title?",
                    "expected": "Product Manager"
                }
            ]
        }
    ]
    return data

def run_membench(args):
    client = Letta(base_url=args.base_url)
    
    if os.path.exists(args.data_path):
        data = load_json(args.data_path)
    else:
        print(f"Data not found at {args.data_path}. Using synthetic data.")
        data = create_synthetic_membench()
        save_json(data, args.data_path)
    
    if args.limit:
        data = data[:args.limit]
    
    overall_results = []
    
    for task in tqdm(data, desc="Running MemBench tasks"):
        agent = client.agents.create(
            name=f"membench_agent_{task['id']}",
            model=args.model,
            memory_blocks=[
                {"label": "persona", "value": "I am a helpful assistant with a perfect memory."},
                {"label": "human", "value": "I am a user testing your memory."}
            ]
        )
        
        runner = BenchmarkRunner(client, agent.id)
        task_results = []
        
        for step in task['steps']:
            op = step['operation']
            input_text = step['input']
            
            response_messages = runner.run_interaction(input_text)
            
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
            
            result = {
                "operation": op,
                "input": input_text,
                "prediction": prediction,
                "success": False
            }
            
            if op.startswith("retrieve"):
                expected = step.get("expected")
                expected_not = step.get("expected_not")
                
                if expected:
                    f1 = calculate_f1(prediction, expected)
                    result["f1"] = f1
                    result["success"] = f1 > 0.5 # Threshold for success
                elif expected_not:
                    # For delete, we want to make sure the old info is NOT there
                    if expected_not.lower() not in prediction.lower():
                        result["success"] = True
            else:
                # For store/update/delete commands, we just assume success if the agent responded
                result["success"] = True
                
            task_results.append(result)
            
        overall_results.append({
            "task_id": task['id'],
            "task_name": task['name'],
            "steps": task_results
        })
        
        client.agents.delete(agent.id)

    # Calculate aggregate metrics
    total_steps = sum(len(r['steps']) for r in overall_results)
    successful_steps = sum(sum(1 for s in r['steps'] if s['success']) for r in overall_results)
    accuracy = successful_steps / total_steps if total_steps > 0 else 0
    
    print(f"
MemBench Benchmark Summary:")
    print(f"Model: {args.model}")
    print(f"Accuracy: {accuracy:.4f} ({successful_steps}/{total_steps})")
    
    if args.output_path:
        save_json({"summary": {"model": args.model, "accuracy": accuracy}, "details": overall_results}, args.output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MemBench benchmark on Letta.")
    parser.add_argument("--base_url", type=str, default="http://localhost:8283", help="Letta server base URL")
    parser.add_argument("--data_path", type=str, default="tests/benchmarks/membench/data/membench_synthetic.json", help="Path to MemBench dataset")
    parser.add_argument("--model", type=str, default="openai/gpt-4o-mini", help="Model to use for the agent")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of tasks to process")
    parser.add_argument("--output_path", type=str, default="tests/benchmarks/membench/results.json", help="Path to save results")
    
    args = parser.parse_args()
    run_membench(args)
