# ======================= [built-in modules] =======================
import os
import time
# ====================== [third-party modules] =====================
import yaml
import numpy as np
import matplotlib.pyplot as plt
from datasets import load_dataset
# ======================= [custom modules] =========================
from utils.eval_similarity import calculate_semantic_similarity, calculate_bert_score
from utils.segment_embedding import *




def process_summaries(folder_path, original_texts, target_name):
    summaries_folder = os.path.join(folder_path, "summaries")
    similarity_scores_path = os.path.join(folder_path, f"{target_name}.txt")
    similarity_graph_path = os.path.join(folder_path, f"{target_name}_distribution.png")
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
            
            similarity = calculate_bert_score(original_text, summary, model="allenai/led-base-16384")
            
            similarity_scaled = similarity * 100  # Scale to 0-100
            similarity_scores.append(similarity_scaled)
            
            f.write(f"[{i}] Semantic Similarity: {similarity_scaled:.2f}\n")
    
    plot_similarity_distribution(similarity_scores, similarity_graph_path, target_name)

    print(f"Done. Elapsed time: {time.time() - start_time:.2f} sec.")
    return similarity_scores



def plot_similarity_distribution(similarity_scores, save_path, target_name):
    plt.hist(similarity_scores, bins=20, range=(0, 100), alpha=0.7, edgecolor="black")
    plt.title(f"{target_name} Distribution")
    plt.xlabel(f"{target_name}")
    plt.ylabel("Count")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.savefig(save_path)
    plt.close()




def load_original_text(config):
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




def main():
    base_directory = "./experiments"  # relative path
    
    experiments_dirs = os.listdir(base_directory)
    experiments_dirs.sort()

    for folder_name in experiments_dirs:
        folder_path = os.path.join(base_directory, folder_name)
        if os.path.isdir(folder_path):
            try:
                # Load config and original texts
                print(f"========== Evaluating {folder_path} ========== ", end="\n\n", flush=True)
                with open(os.path.join(folder_path, "config.yaml"), "r") as f:
                    config = yaml.safe_load(f)
                original_texts = load_original_text(config)

                # Process summaries and calculate semantic similarity
                process_summaries(folder_path, original_texts, target_name="BERTScore_v2")
            
            except FileNotFoundError as e:
                print(e)
            
            except Exception as e:
                print(f"Error in folder '{folder_name}': {e}")

if __name__ == "__main__":
    main()
