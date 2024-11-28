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
    
    # ========================== [Embedding] ===========================
    print("Embedding...    ", end="", flush=True)
    s = time.time()
    embeddings = encode_segments(segments) # model fixed
    e = time.time()
    print("Done", f"{e-s:.2f} sec")

    # ========================== [Clustering] ==========================
    print("Clustering...   ", end="", flush=True)
    s = time.time()
    concat_indices = globals()[config.concat.method](embeddings, **config.concat.args)
    e = time.time()
    print("Done", f"{e-s:.2f} sec")

    max_group_size = max([len(group) for group in concat_indices])
    print(f"Num. of Cluster: {len(concat_indices)}, Max group size: {max_group_size}")

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
                           len(batch_clusters) // config.mini_batch.size)

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
    score = 0
    e = time.time()
    print("Done", f"{e-s:.2f} sec")
    print(f"=> Score: {score:.4f}  ")

    # ========================== [Post-process] ========================
    if score > max_score: # score는 대소비교 가능한 1가지 방식을 이용
        max_score = score
        best_summary = batch_summaries
        # 원본 텍스트의 index는 indices[di]로 찾을 수 있음
    
    evaluation_results.append(score)
    print(f"Total: {time.time()-init_s:.2f} sec")

print("===============================================")

# ====================== [Save experiment result] ======================
print("Saving evaluation results... ", end="", flush=True)

save_dir_path = os.path.join('experiments', f'{config.experiment_name}')
if not os.path.exists(save_dir_path):
    os.makedirs(save_dir_path)

# Copy config file
os.system(f'cp config.yaml {save_dir_path}')

# Make README.md
with open(os.path.join(save_dir_path, 'README.md'), 'w') as f:
    f.write(f'# {config.experiment_name}\n')

# Save evaluation results
...
print("Done")