import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
import numpy as np
import torch

from datasets import load_dataset
import matplotlib.pyplot as plt
import seaborn as sns
from rouge_score import rouge_scorer
from bert_score import score as bert_score
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

import yaml
from box import Box
import os
import time

from utils.eval_similarity import *
from utils.utils import *
from utils.segment_embedding import *
from utils.concat_functions import *
from utils.summarizer import *

# load config ----------------------
with open("config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    config = Box(config)

print(config.experiment_name)

# load data ----------------------
open_source_datasets = load_dataset(config.data.open_source)
youtube_datasets = load_dataset(config.data.youtube)

print(open_source_datasets, youtube_datasets)

# based on the dataset, change the key to access the data
open_source_datasets = open_source_datasets["train"]["report"]
youtube_datasets  = youtube_datasets["train"]["content"]

# *** DO NOT PRINT THE WHOLE DATASET ipynb will die ***
print(len(open_source_datasets), len(youtube_datasets))

# select data for experiment ----------------------
experiment_texts = open_source_datasets[:1]
# experiment_texts = youtube_datasets[:100]

print(len(experiment_texts))

# run experiment ----------------------
summaries = []
results = []

for i in range(len(experiment_texts)):
    print(f"==== Processing {i+1}/{len(experiment_texts)} ====")
    
    start_time = time.time()
    texts = experiment_texts[i]
    # print(texts)

    # texts to segments
    print("Segmentating...")
    segments = segmentate_sentence(texts, config.segment.n_word, config.segment.n_overlap, True)
    embeddings = encode_segments(segments)

    # concatenate segements
    print("Concatenating...")
    # concatenated_indexes = concate_time_based(embeddings,threshold=0.6 )
    # concatenated_indexes = concate_knn(embeddings)
    concatenated_indexes = concate_clustering(embeddings)
    max_length = max([len(group) for group in concatenated_indexes])
    print(f"theme_num: {len(concatenated_indexes)}, max_size: {max_length}")

    # based on concatenated indexes make theme segements
    theme_segments = [
        " ".join(segments[j] for j in group) for group in concatenated_indexes
    ]

    # make summary
    print("Summarizing...")
    summary = summarizer(
        theme_segments, 
        model=config.summary.model, 
        max_length=config.summary.max_length,
        min_length=config.summary.min_length
    )
    summaries.append(summary)
    # print(summary)

    # evaluation ----------------------
    # TODO: evaluation code here
    # results.append(evaluation(summary, texts))

    end_time = time.time()
    print(f"Time taken: {end_time - start_time}")

# save config & results ----------------------
exp_dir = os.path.join(config.experiment_dir, config.experiment_name)
os.makedirs(exp_dir, exist_ok=True)
os.system(f"cp config.yaml {exp_dir}")

# TODO: save experiment results
# *** important : please save the number of data you used ***
# num_data = len(experiment_texts)