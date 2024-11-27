from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

"""
This file is for summarizer functions
Based on the model it could be different pipeline

*** parallel processing is recommended for summarization *** 

function signature:
    args: texts (list), any other arguments if needed
    returns: summary (str)

"""


def summarizer(texts: list, model="facebook/bart-large-cnn", max_length=1024, min_length=0)->str:
    """
    summarizer based on language model

    Args:
    - texts: list of texts
    - model: model name
    - max_length: maximum length of the summary
    - min_length: minimum length of the summary

    Returns:
    - str: summary
    """
    tokenizer = AutoTokenizer.from_pretrained(model)
    model = AutoModelForSeq2SeqLM.from_pretrained(model)

    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        summary_ids = model.generate(inputs['input_ids'], num_beams=4, max_length=100, early_stopping=True)

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    return summary