import asyncio
import json
import time
from typing import List, Dict
import os
from datetime import datetime
from openai import AsyncOpenAI

OPENAI_API = ""
client = AsyncOpenAI(api_key=OPENAI_API)

class ProgressTracker:
    """
    A class to track and persist progress of batch processing operations.
    
    This class maintains a record of processed items and their indices, allowing for
    resumption of batch processing operations in case of interruption.
    
    Attributes:
        tracker_file (str): Path to the JSON file used to store progress information
        processed_count (int): Number of items processed so far
        last_processed_index (int): Index of the last successfully processed item
    """
    
    def __init__(self, tracker_file: str = 'progress_tracker.json'):
        """
        Initialize the ProgressTracker.
        
        Args:
            tracker_file (str): Path to the JSON file used to store progress information.
                              Defaults to 'progress_tracker.json'
        """
        self.tracker_file = tracker_file
        self.processed_count = 0
        self.last_processed_index = -1
        self.load_progress()
    
    def load_progress(self) -> None:
        """
        Load previously saved progress from the tracker file.
        
        Reads the tracker file if it exists and updates the processed_count and
        last_processed_index attributes. If the file doesn't exist or there's an error,
        the default values are maintained.
        """
        if os.path.exists(self.tracker_file):
            try:
                with open(self.tracker_file, 'r') as f:
                    data = json.load(f)
                    self.processed_count = data.get('processed_count', 0)
                    self.last_processed_index = data.get('last_processed_index', -1)
                print(f"Loaded progress: processed {self.processed_count} items, last index: {self.last_processed_index}")
            except Exception as e:
                print(f"Error loading progress tracker: {e}")
    
    def save_progress(self) -> None:
        """
        Save current progress to the tracker file.
        
        Writes the current processed_count, last_processed_index, and timestamp
        to the tracker file in JSON format. Any errors during saving are logged
        but do not interrupt the program flow.
        """
        try:
            with open(self.tracker_file, 'w') as f:
                json.dump({
                    'processed_count': self.processed_count,
                    'last_processed_index': self.last_processed_index,
                    'last_update': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving progress tracker: {e}")

async def query_openai(model: str, system_prompt: str, user_prompt: str, max_tokens: int = 1000, temperature: float = 0.0) -> str:
    """
    Send a query to the OpenAI API and get the response.
    
    Args:
        model (str): The OpenAI model to use for the query
        system_prompt (str): The system message to set the context
        user_prompt (str): The user's input message
        max_tokens (int): Maximum number of tokens in the response. Defaults to 1000
        temperature (float): Sampling temperature. Defaults to 0.0 for deterministic output
    
    Returns:
        str: The generated response from the OpenAI API
        
    Raises:
        Exception: If there's an error communicating with the OpenAI API
    """
    try:
        completion = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        raise

async def process_single_query(data: Dict, index: int, output_file: str, progress_tracker: ProgressTracker) -> None:
    """
    Process a single query and save its results.
    
    Args:
        data (Dict): The query data containing model information and messages
        index (int): The current processing index
        output_file (str): Path to the file where results will be saved
        progress_tracker (ProgressTracker): Instance of ProgressTracker to monitor progress
    
    The function handles the entire lifecycle of a single query:
    - Sending the query to OpenAI
    - Recording the response
    - Updating progress
    - Error handling and logging
    """
    try:
        custom_id = data['custom_id']
        start_time = datetime.now()
        
        print(f"Processing index {index} (ID: {custom_id})")
        
        response = await query_openai(
            data['body']['model'], 
            data['body']['messages'][0]['content'], 
            data['body']['messages'][1]['content']
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        async with asyncio.Lock():
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    "custom_id": custom_id, 
                    "response": response,
                    "index": index,
                    "processing_time": processing_time,
                    "processed_at": datetime.now().isoformat()
                }) + '\n')
            
            progress_tracker.processed_count += 1
            if index > progress_tracker.last_processed_index:
                progress_tracker.last_processed_index = index
            progress_tracker.save_progress()
        
        print(f"Completed index {index} (ID: {custom_id}). Processing time: {processing_time:.2f}s. Total processed: {progress_tracker.processed_count}")
    except Exception as e:
        print(f"Error processing index {index}, custom_id {data.get('custom_id', 'unknown')}: {str(e)}")
        with open('error_log.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "custom_id": data.get('custom_id', 'unknown'),
                "index": index,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }) + '\n')

async def rate_limited_queries(
    data_batch: List[Dict], 
    output_file: str, 
    progress_tracker: ProgressTracker,
    requests_per_minute: int = 14
) -> None:
    """
    Process multiple queries with rate limiting.
    
    Args:
        data_batch (List[Dict]): List of query data to process
        output_file (str): Path to the file where results will be saved
        progress_tracker (ProgressTracker): Instance of ProgressTracker to monitor progress
        requests_per_minute (int): Maximum number of requests allowed per minute. Defaults to 14
    
    The function implements rate limiting using semaphores and ensures that the
    specified rate limit is not exceeded. It processes queries concurrently while
    maintaining the rate limit and handles any errors that occur during processing.
    """
    total_items = len(data_batch)
    initial_index = progress_tracker.last_processed_index
    semaphore = asyncio.Semaphore(requests_per_minute)
    
    async def process_with_semaphore(data: Dict, base_index: int):
        async with semaphore:
            start_time = datetime.now()
            await process_single_query(data, base_index, output_file, progress_tracker)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            wait_time = max(0, 60 - processing_time)
            if wait_time > 0:
                print(f"\nWaiting {wait_time:.2f}s to maintain rate limit (7 requests/minute)")
                await asyncio.sleep(wait_time)
    
    tasks = []
    for i, data in enumerate(data_batch):
        base_index = initial_index + i + 1
        task = asyncio.create_task(process_with_semaphore(data, base_index))
        tasks.append(task)
    
    try:
        await asyncio.gather(*tasks)
        print(f"\nAll tasks completed. Total processed: {progress_tracker.processed_count}")
    except Exception as e:
        print(f"\nError during batch processing: {e}")
        for task in tasks:
            if not task.done():
                task.cancel()

async def main():
    """
    Main entry point for the batch processing script.
    
    This function:
    1. Initializes the progress tracker
    2. Reads the input file
    3. Processes remaining items from the last checkpoint
    4. Handles interruptions and errors gracefully
    
    The process can be interrupted with Ctrl+C, and progress will be saved
    automatically. The script can be restarted and will continue from the
    last successful processing point.
    """
    input_file = 'batch_input.jsonl'
    output_file = 'batch_output.jsonl'
    progress_tracker = ProgressTracker()
    
    print("Reading input file...")
    with open(input_file, 'r', encoding='utf-8') as f:
        batch_input = [json.loads(line) for line in f.readlines()]
    
    start_index = progress_tracker.last_processed_index + 1
    remaining_batch = batch_input[start_index:]
    
    if not remaining_batch:
        print("All items have been processed!")
        return
    
    print(f"\nResuming from index {start_index}")
    print(f"Starting to process {len(remaining_batch)} remaining items...")
    print(f"Rate limit: 8 requests per minute (one request every 7.5 seconds)")
    print("Press Ctrl+C to interrupt processing (progress will be saved)\n")
    
    try:
        await rate_limited_queries(
            remaining_batch, 
            output_file, 
            progress_tracker,
            requests_per_minute=14
        )
        print("\nProcessing completed successfully!")
    except KeyboardInterrupt:
        print("\nProcessing interrupted. Progress has been saved.")
        print(f"Processed {progress_tracker.processed_count} items total.")
        print(f"Last processed index: {progress_tracker.last_processed_index}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print(f"Progress has been saved. Last processed index: {progress_tracker.last_processed_index}")

if __name__ == "__main__":
    asyncio.run(main())