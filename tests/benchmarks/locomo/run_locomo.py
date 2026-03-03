import os
import argparse
import json
from tqdm import tqdm
from letta_client import Letta
from tests.benchmarks.common.runner import BenchmarkRunner
from tests.benchmarks.common.utils import load_json, save_json, calculate_f1

def run_locomo(args):
    client = Letta(base_url=args.base_url)
    data = load_json(args.data_path)
    
    # Limit data for testing if requested
    if args.limit:
        data = data[:args.limit]
    
    results = []
    
    for item_idx, item in enumerate(tqdm(data, desc="Processing LOCOMO items")):
        # Create a new agent for each conversation item to ensure clean memory
        agent = client.agents.create(
            name=f"locomo_agent_{item_idx}",
            model=args.model,
            memory_blocks=[
                {"label": "persona", "value": "I am a helpful assistant with a perfect memory."},
                {"label": "human", "value": f"I am talking to {item['conversation']['speaker_a']} and {item['conversation']['speaker_b']}."}
            ]
        )
        
        runner = BenchmarkRunner(client, agent.id)
        
        # Feed the conversation sessions
        conversation = item['conversation']
        sessions = [k for k in conversation.keys() if k.startswith('session_') and not k.endswith('_date_time')]
        # Sort sessions numerically
        sessions.sort(key=lambda x: int(x.split('_')[1]))
        
        for session_key in sessions:
            session_messages = conversation[session_key]
            for msg in session_messages:
                # Format: "Speaker: Text"
                formatted_msg = f"{msg['speaker']}: {msg['text']}"
                # We send the message and ignore the immediate response for now, 
                # as we are building up the agent's memory.
                runner.run_interaction(formatted_msg)
        
        # Evaluate QA
        qa_results = []
        for qa in item['qa']:
            question = qa['question']
            ground_truth = qa['answer']
            
            # Ask the question
            response_messages = runner.run_interaction(f"Question: {question}\nAnswer briefly based on our conversation history.")
            
            # Find the assistant's answer (last message usually)
            prediction = ""
            for m in reversed(response_messages):
                if hasattr(m, 'content') and m.content:
                    if isinstance(m.content, str):
                        prediction = m.content
                        break
                    elif isinstance(m.content, list):
                        # Handle list of content items if necessary
                        prediction = " ".join([c.text for c in m.content if hasattr(c, 'text')])
                        break
            
            f1 = calculate_f1(prediction, str(ground_truth))
            
            qa_results.append({
                "question": question,
                "ground_truth": ground_truth,
                "prediction": prediction,
                "f1": f1
            })
            
        avg_f1 = sum(r['f1'] for r in qa_results) / len(qa_results) if qa_results else 0
        
        results.append({
            "item_idx": item_idx,
            "avg_f1": avg_f1,
            "qa_details": qa_results
        })
        
        # Clean up agent
        client.agents.delete(agent.id)

    # Aggregate results
    overall_f1 = sum(r['avg_f1'] for r in results) / len(results) if results else 0
    
    summary = {
        "model": args.model,
        "overall_f1": overall_f1,
        "items_processed": len(results)
    }
    
    print(f"\nLOCOMO Benchmark Summary:")
    print(f"Model: {args.model}")
    print(f"Overall F1 Score: {overall_f1:.4f}")
    
    if args.output_path:
        save_json({"summary": summary, "details": results}, args.output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LOCOMO benchmark on Letta.")
    parser.add_argument("--base_url", type=str, default="http://localhost:8283", help="Letta server base URL")
    parser.add_argument("--data_path", type=str, default="tests/benchmarks/locomo/data/locomo10.json", help="Path to LOCOMO dataset")
    parser.add_argument("--model", type=str, default="openai/gpt-4o-mini", help="Model to use for the agent")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of items to process")
    parser.add_argument("--output_path", type=str, default="tests/benchmarks/locomo/results.json", help="Path to save results")
    
    args = parser.parse_args()
    run_locomo(args)
