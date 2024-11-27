import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
import numpy as np
import torch

from datasets import load_dataset
import matplotlib.pyplot as plt
import seaborn as sns
from rouge_score import rouge_scorer
from bert_score import score as bert_score

import yaml
from box import Box
import os

from utils.eval_similarity import *
from utils.utils import *
from utils.segment_embedding import *
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from utils.concat_functions import *
from utils.summarizer import *


# load config ----------------------
with open("config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    config = Box(config)

print(config.open_source_datasets)

# load data ----------------------
open_source_datasets = load_dataset(config.open_source_datasets)["train"]["report"] # gov-report data, if other datasets check the key name
youtube_datasets = load_dataset(config.youtube_datasets)["train"]
print(open_source_datasets, youtube_datasets)


# select data for experiment ----------------------
experiment_texts = open_source_datasets.select(range(100))
# experiment_texts = youtube_datasets.select(range(100))


# run experiment ----------------------
summaries = []
results = []

for i in range(len(experiment_texts)):
    texts = experiment_texts[i]
    print(texts)

    # texts to segments ----------------------
    segments = segmentate_sentence(full_text, n_word, n_overlap, False)
    embeddings = encode_segments(segments)

    # get concatenate indexes based on similarity ----------------------
    concatenated_indexes = concate_time_based(embeddings)
    # concatenated_indexes = concate_clustering(embeddings)

    # make theme segements ----------------------
    theme_segments = [segments[i] for i in concatenated_indexes]

    # make summary ----------------------
    summary = summarizer(
        theme_segments, 
        model=config.summary.model, 
        max_length=config.summary.max_length,
        min_length=config.summary.min_length
    )
    summaries.append(summary)

    # evaluation ----------------------
    # TODO: evaluation code here
    # results.append(evaluation(summary, texts))

# save config & results ----------------------
exp_dir = os.path.join(config.experiment_name, config.exp_name)
os.makedirs(exp_dir, exist_ok=True)
os.system(f"cp config.yaml {exp_dir}")

# TODO: save experiment results
# *** important : please save the number of data you used ***
# num_data = len(experiment_texts)