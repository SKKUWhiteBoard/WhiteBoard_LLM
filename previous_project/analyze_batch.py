#!/usr/bin/env python3

import os
import re
import json
import collections
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Set

def get_all_txt_files(base_path: str = 'preprocessed_dataset/youtube_dataset') -> List[str]:
    """
    Recursively get all txt files from the specified directory.
    
    Args:
        base_path (str): Base directory path to search for txt files
        
    Returns:
        List[str]: List of paths to txt files
    """
    txt_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if re.search(r'\.txt$', file):
                txt_files.append(os.path.join(root, file))
    return txt_files

def load_transcripts(file_paths: List[str]) -> Tuple[List[str], List[str]]:
    """
    Load transcripts from txt files.
    
    Args:
        file_paths (List[str]): List of file paths to read
        
    Returns:
        Tuple[List[str], List[str]]: Tuple containing lists of transcripts and their names
    """
    transcripts = []
    transcript_names = []
    
    for file in file_paths:
        with open(file, 'r') as f:
            transcripts.append(f.read())
            transcript_names.append(file.split('/')[-1].split('.')[0])
            
    return transcripts, transcript_names

def analyze_word_counts(transcripts: List[str]) -> Dict:
    """
    Analyze word counts of transcripts.
    
    Args:
        transcripts (List[str]): List of transcript texts
        
    Returns:
        Dict: Dictionary containing word count statistics
    """
    word_counts = [len(transcript.split()) for transcript in transcripts]
    
    stats = {
        'mean': np.mean(word_counts),
        'max': np.max(word_counts),
        'min': np.min(word_counts),
        'word_counts': word_counts
    }
    
    return stats

def plot_word_count_distribution(word_counts: List[int], title: str = 'Word Count Distribution of Transcripts'):
    """
    Plot histogram of word count distribution.
    
    Args:
        word_counts (List[int]): List of word counts
        title (str): Title for the plot
    """
    plt.figure(figsize=(10, 6))
    plt.hist(word_counts, bins=50)
    plt.xlabel('Word Count')
    plt.ylabel('Frequency')
    plt.title(title)
    plt.show()

def filter_transcripts(transcripts: List[str], word_counts: List[int], 
                      min_percentile: float = 0.5, max_percentile: float = 99.5) -> Tuple[List[str], List[int]]:
    """
    Filter transcripts by removing top and bottom percentiles.
    
    Args:
        transcripts (List[str]): List of transcripts
        word_counts (List[int]): List of word counts
        min_percentile (float): Bottom percentile to remove
        max_percentile (float): Top percentile to remove
        
    Returns:
        Tuple[List[str], List[int]]: Filtered transcripts and their word counts
    """
    top_threshold = np.percentile(word_counts, max_percentile)
    bottom_threshold = np.percentile(word_counts, min_percentile)
    
    filtered_data = [(t, c) for t, c in zip(transcripts, word_counts) 
                    if bottom_threshold <= c <= top_threshold]
    
    return list(zip(*filtered_data)) if filtered_data else ([], [])

def create_batch_file(transcripts: List[str], transcript_names: List[str], 
                     system_prompt: str, output_file: str = 'batch_input.jsonl'):
    """
    Create a JSONL batch file for API requests.
    
    Args:
        transcripts (List[str]): List of transcripts
        transcript_names (List[str]): List of transcript names
        system_prompt (str): System prompt for the API
        output_file (str): Output file path
    """
    seen_custom_ids: Set[str] = set()
    batch_data = []
    
    for transcript, name in zip(transcripts, transcript_names):
        if name not in seen_custom_ids:
            seen_custom_ids.add(name)
            batch_data.append({
                "custom_id": name,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": transcript + "\n" + system_prompt}
                    ],
                    "max_tokens": 1000
                }
            })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in batch_data:
            f.write(json.dumps(item) + "\n")

def validate_jsonl(file_path: str) -> bool:
    """
    Validate JSONL file format.
    
    Args:
        file_path (str): Path to JSONL file
        
    Returns:
        bool: True if file is valid JSONL
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, start=1):
                json.loads(line)
        return True
    except Exception as e:
        print(f"Validation failed at line {line_number}: {e}")
        return False

def process_api_responses(input_file: str, output_file: str, response_file: str):
    """
    Process API responses and create paired data file.
    
    Args:
        input_file (str): Path to input JSONL file
        output_file (str): Path to output JSONL file
        response_file (str): Path to response JSONL file
    """
    # Create input lookup dictionary
    input_lookup = {}
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            input_data = json.loads(line)
            custom_id = input_data['custom_id']
            user_content = input_data['body']['messages'][1]['content']
            input_lookup[custom_id] = user_content

    # Process output and create response file
    with open(output_file, 'r', encoding='utf-8') as f, \
         open(response_file, 'w', encoding='utf-8') as out_file:
        for line in f:
            output_data = json.loads(line)
            custom_id = output_data['custom_id']
            response = output_data['response']
            
            user_content = input_lookup.get(custom_id)
            if user_content:
                json.dump({
                    'custom_id': custom_id,
                    'role': 'user',
                    'content': user_content,
                    'response': response
                }, out_file)
                out_file.write('\n')

def main():
    # Load system prompt
    system_prompt_default = "Generate an outline for the provided lecture transcript that identifies and summarizes the key topics in a sequential manner."
    
    # Get transcript files
    txt_files = get_all_txt_files()
    transcripts, transcript_names = load_transcripts(txt_files)
    
    # Analyze word counts
    stats = analyze_word_counts(transcripts)
    plot_word_count_distribution(stats['word_counts'])
    
    # Filter transcripts
    filtered_transcripts, filtered_word_counts = filter_transcripts(
        transcripts, stats['word_counts']
    )
    
    # Create batch file
    create_batch_file(filtered_transcripts, transcript_names, system_prompt_default)
    
    # Validate batch file
    if validate_jsonl('batch_input.jsonl'):
        print("Batch file created and validated successfully!")
        
    # Process API responses if output file exists
    if os.path.exists('batch_output.jsonl'):
        process_api_responses(
            'batch_input.jsonl',
            'batch_output.jsonl',
            'responses.jsonl'
        )

if __name__ == "__main__":
    main()