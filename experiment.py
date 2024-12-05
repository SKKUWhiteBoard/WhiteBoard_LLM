# ======================= [built-in modules] =======================
import os
import time

# ====================== [third-party modules] =====================
import yaml
from box import Box
import numpy as np
from datasets import load_dataset
from bert_score import score as bert_score
from rouge_score import rouge_scorer
import matplotlib.pyplot as plt

# ======================= [custom modules] =========================
from utils.eval_similarity import *
from utils.utils import *
from utils.segment_embedding import *
from utils.concat_functions import *
from utils.summarizer import *


# ========================= [Load config] ===========================
with open("config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    config = Box(config)

print('Experiment name:', config.experiment_name)
print('===============================================')

# ========================== [Load data] ============================
print("Loading data... ", end="", flush=True)
if config.data.source == 'opensource':
    datasets = load_dataset(config.data.opensource)
    indices = np.load(f'data/gov_indices{config.data.index_set}.npy')
    datasets = datasets['train'].select(indices)['report']

elif config.data.source == 'youtube':
    datasets = load_dataset(config.data.youtube)
    indices = np.load(f'data/ytb_indices{config.data.index_set}.npy')
    datasets = datasets['train'].select(indices)['content']
print("Done")
print('===============================================')

save_dir_path = os.path.join('experiments', f'{config.experiment_name}')
if not os.path.exists(save_dir_path):
    os.makedirs(save_dir_path)

# ========================== [Run experiments] ==========================
max_score = 0
best_summary = ""

evaluation_results = []
for di, text in enumerate(datasets):
    print(f" ----------------- [{di+1}/{len(datasets)}] ----------------- ")
    init_s = time.time()

    # ========================== [Segmentation] ========================
    print("Segmentating... ", end="", flush=True)
    s = time.time()
    segments = segmentate_sentence(text, **config.segment.args)
    e = time.time()
    print("Done", f"{e-s:.2f} sec")

    # ========================== [Clustering] ==========================
    print("Clustering...   ", end="", flush=True)
    s = time.time()
    concat_indices = globals()[config.concat.method](segments, **config.concat.args)
    e = time.time()
    print("Done", f"{e-s:.2f} sec")

    max_group_size = max([len(group) for group in concat_indices])
    avg_group_size = np.mean([len(group) for group in concat_indices])
    print(f"Num. of Cluster: {len(concat_indices)}, Max group size: {max_group_size}, Avg. group size: {avg_group_size:.2f}")

    # ========================== [Ready to summarize] ==================
    batch_clusters = [
        " ".join([segments[gi] for gi in group]) for group in concat_indices
    ]

    # ========================== [Summarize] ===========================
    print("Summarizing...  ", end="", flush=True)
    s = time.time()
    if config.mini_batch.size > 0:
        mini_batch_size = (len(batch_clusters)
                           if len(batch_clusters) < config.mini_batch.size else
                           config.mini_batch.size)

        batch_summaries = []
        for i in range(0, len(batch_clusters), mini_batch_size):
            mini_batch_summaries = summarizer(batch_clusters[i:i+mini_batch_size], **config.summary.args)
            batch_summaries.append(mini_batch_summaries)
        batch_summaries = " ".join(batch_summaries)
    else:
        batch_summaries = summarizer(batch_clusters, **config.summary.args)
    e = time.time()
    print("Done", f"{e-s:.2f} sec")

    # ========================== [Evaluate] ============================
    print("Evaluating...   ", end="", flush=True)
    s = time.time()
    
    rouge1, rouge2, rougeL = calculate_rouge_scores(text, batch_summaries)
    s_score = calculate_sementic_similarity(text, batch_summaries)

    # scale score * 100
    rouge1, rouge2, rougeL = rouge1*100, rouge2*100, rougeL*100
    s_score = s_score * 100

    e = time.time()
    print("Done", f"{e-s:.2f} sec")
    
    print(f"=> ROUGE-1: {rouge1:.2f}, ROUGE-2: {rouge2:.2f}, ROUGE-L: {rougeL:.2f}")
    print(f"=> BERTScore: {s_score:.2f}")

    # ========================== [Post-process] ========================
    if s_score > max_score: # score는 대소비교 가능한 1가지 방식을 이용
        max_score = s_score
        best_summary = batch_summaries
        best_index = di
        # 원본 텍스트의 index는 indices[di]로 찾을 수 있음
    
    evaluation_results.append({
        'rouge1': rouge1,
        'rouge2': rouge2,
        'rougeL': rougeL,
        'bert_score': s_score
    })
    print(f"Total: {time.time()-init_s:.2f} sec")

    # append summary and scores to text file (cummulative)
    # Ensure directories exist
    base_path = f'experiments/{config.experiment_name}'
    summaries_dir = os.path.join(base_path, 'summaries')
    os.makedirs(summaries_dir, exist_ok=True)

    # Save the summary in a separate file
    summary_path = f'experiments/{config.experiment_name}/summaries/summary_{di+1}.txt'
    with open(summary_path, 'w') as f:
        f.write(f"Summary:\n{batch_summaries}\n\n")

    # Append ROUGE scores to ROUGE_scores.txt
    rouge_path = f'experiments/{config.experiment_name}/ROUGE_scores.txt'
    with open(rouge_path, 'a') as f:
        f.write(f"[{di+1}] ROUGE-1: {rouge1:.2f}\tROUGE-2: {rouge2:.2f}\tROUGE-L: {rougeL:.2f}\n")

    # Append semantic scores to Semantic_scores.txt
    semantic_path = f'experiments/{config.experiment_name}/Semantic_scores.txt'
    with open(semantic_path, 'a') as f:
        f.write(f"[{di+1}] Semantic Score: {s_score:.2f}\n")

print("===============================================")

# ====================== [Save experiment result] ======================
print("Saving evaluation results... ")


# Copy config file
os.system(f'cp config.yaml {save_dir_path}')

# Make README.md
with open(os.path.join(save_dir_path, 'README.md'), 'w') as f:
    f.write(f'# {config.experiment_name}\n')

# Save best summary & index
with open(os.path.join(save_dir_path, 'best_summary.txt'), 'w') as f:
    f.write(f"Best index: {best_index}\n\n")
    f.write(best_summary)

# plot evaluation results
metrics = list(evaluation_results[0].keys())
data_by_metric = {metric: [sample[metric] for sample in evaluation_results] for metric in metrics}

statistics = {}
for metric, values in data_by_metric.items():
    statistics[metric] = {
        'mean': np.mean(values),
        'var': np.var(values),
        'min': np.min(values),
        'max': np.max(values)
    }

# print and save statistics in results.txt
for metric, stats in statistics.items():
    print(f"{metric}: mean={stats['mean']:.3f}, var={stats['var']:.3f}, min={stats['min']:.3f}, max={stats['max']:.3f}")
    with open(os.path.join(save_dir_path, 'results.txt'), 'a') as f:
        f.write(f"{metric}: mean={stats['mean']:.3f}, var={stats['var']:.3f}, min={stats['min']:.3f}, max={stats['max']:.3f}\n")

for metric, values in data_by_metric.items():
    plt.figure(figsize=(8, 5))
    plt.hist(values, bins=10, edgecolor='black', alpha=0.7)
    plt.title(f'Distribution of {metric}')
    plt.xlabel(metric)
    plt.ylabel('count')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(save_dir_path, f'{metric}_histogram.png'))
    plt.close()


print("Done")