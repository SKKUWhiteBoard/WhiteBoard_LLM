import os
import numpy as np
import matplotlib.pyplot as plt
from utils.eval_similarity import calculate_sementic_similarity
from utils.segment_embedding import *
import time

from datasets import load_dataset

# Semantic similarity 계산 및 저장
def process_summaries(folder_path, original_texts):
    summaries_folder = os.path.join(folder_path, "summaries")
    similarity_scores_path = os.path.join(folder_path, "semantic_similarity.txt")
    similarity_graph_path = os.path.join(folder_path, "semantic_similarity_distribution.png")
    similarity_scores = []

    if not os.path.exists(summaries_folder):
        raise FileNotFoundError(f"Summaries folder not found in '{folder_path}'.")

    start_time = time.time()
    print(f"Processing summaries in '{folder_path}'... ")

    # Summary 파일 읽기
    summary_files = sorted(os.listdir(summaries_folder), key=lambda x: int(x.replace("summary_", "").replace(".txt", "")))

    with open(similarity_scores_path, "w") as f:
        for i, (summary_file, original_text) in enumerate(zip(summary_files, original_texts), start=1):
            print(f"Processing summary {i}/{len(summary_files)}... ", end="\r", flush=True)
            
            summary_path = os.path.join(summaries_folder, summary_file)
            with open(summary_path, "r") as sf:
                summary = sf.read().strip()
            
            # Calculate similarity
            similarity = calculate_sementic_similarity(original_text, summary)
            similarity_scaled = similarity * 100  # Scale to 0-100
            similarity_scores.append(similarity_scaled)
            f.write(f"[{i}] Semantic Similarity: {similarity_scaled:.2f}\n")
    
    # 그래프 생성
    plot_similarity_distribution(similarity_scores, similarity_graph_path)

    print(f"Done. Elapsed time: {time.time() - start_time:.2f} sec.")
    return similarity_scores

# 그래프 생성 함수
def plot_similarity_distribution(similarity_scores, save_path):
    plt.hist(similarity_scores, bins=20, range=(0, 100), alpha=0.7, edgecolor="black")
    plt.title("Semantic Similarity Distribution")
    plt.xlabel("Semantic Similarity (%)")
    plt.ylabel("Frequency")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.savefig(save_path)
    plt.close()

# 데이터 로드 함수
def load_original_text(config_path):
    import yaml  # Import yaml library for config parsing
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    print("Loading data... ", end="", flush=True)
    if config["data"]["source"] == "opensource":

        datasets = load_dataset(config["data"]["opensource"])
        indices = np.load(f"./data/gov_indices{config['data']['index_set']}.npy")
        original_texts = datasets["train"].select(indices)["report"]

    elif config["data"]["source"] == "youtube":

        datasets = load_dataset(config["data"]["youtube"])
        indices = np.load(f"./data/ytb_indices{config['data']['index_set']}.npy")
        original_texts = datasets["train"].select(indices)["content"]

    print("Done.")
    return original_texts

# 메인 함수
def main():
    base_directory = "./experiments"  # 현재 디렉토리 기준
    for folder_name in os.listdir(base_directory):
        folder_path = os.path.join(base_directory, folder_name)
        if os.path.isdir(folder_path):
            try:
                # Load config and original texts
                config_path = os.path.join(folder_path, "config.yaml")
                original_texts = load_original_text(config_path)

                # Process summaries and calculate semantic similarity
                process_summaries(folder_path, original_texts)

            except FileNotFoundError as e:
                print(e)
            except Exception as e:
                print(f"Error in folder '{folder_name}': {e}")

if __name__ == "__main__":
    main()
