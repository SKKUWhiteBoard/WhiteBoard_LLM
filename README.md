# WhiteBoard SLLM (swe3032)

```
├── LICENSE
├── README.md
├── config.yaml
├── data
│   ├── collect_script
│   │   ├── combine_jsonl.py
│   │   ├── data_preparation.py
│   │   ├── preprocess.py
│   │   ├── setup.sh
│   │   └── transcript_extractor.py
│   ├── open_source
│   │   ├── huggingface_data_paths.txt
│   │   └── urls.txt
│   ├── youtube_urls
│   │   └── <category>_playlist.txt
│   ├── gov_indices<N>.npy
│   └── ytb_indices<N>.npy
├── experiment.ipynb
├── experiment.py
├── experiments
│   └── example
│       └── config.yaml
├── previous_project
│   ├── experiments
│   └── trainer_baseline.ipynb
└── utils
    ├── concat_functions.py
    ├── eval_similarity.py
    ├── segment_embedding.py
    ├── summarizer.py
    └── utils.py

```
> ## Huggingface Organization
* [Our team Organization Link](https://huggingface.co/WhiteboardLLM)
---
> ## Dataset

* `[./data]` 
    * `[./data/opensource, youtube]` : 오픈소스 (huggingface), 유튜브 meta data
    * `[./data/collect_script/*]` : 데이터 추출 및 전처리
    * `[./data/gov_indices<N>.npy]`: 오픈소스 데이터셋인 "ccdv/govreport-summarization" 중 샘플링하여 사용할 인덱스 세트
    * `[./data/ytb_indices<N>.npy]`: 직접 수집한 데이터셋인 "WhiteboardLLM/Data" 중 샘플링하여 사용할 인덱스 세트
----
* `actual dataset` : 실제 데이터는 `huggingface` 업로드 후 사용
    * [Youtube GPT Summary datasets](https://huggingface.co/datasets/ht324/WhiteBoard_LLM_Data_response)
    
    * [Youtube Raw contents](https://huggingface.co/datasets/WhiteboardLLM/Data)
    
    *  사용 예시 : ```dataset = load_dataset( data path )```

---

> ## Experiment
* `[./config.yaml]` : 실험에 사용하는 주 하이퍼파라미터
* `[./experiment.py]` : 실험 파이프라인 구현 ( py ver )
* `[./experiment.ipynb]` : 실험 파이프라인 구현 ( ipynb ver )
* `[./utils/*]` : 현재 사용하는 아키텍처의 함수 구현
* `[./experiments/*]` : 실험 기록

---

> ## Others (Previous Project)
* `[./previous_project/*]` : sLLM fine tuning 프로젝트
    
* `trainer.ipynb` : kaggle, colab에서 학습에 사용하는 코드

* `trained_models`: 학습된 모델은 `huggingface` 업로드 후 사용 (huggingface repo 참고)