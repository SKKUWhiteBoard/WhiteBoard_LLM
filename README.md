# WhiteBoard SLLM (swe3032)

```
├── LICENSE
├── README.md
├── data
│   ├── open_source
│   │   ├── huggingface_data_paths.txt
│   │   └── urls.txt
│   └── youtube_urls
│       ├── ai_playlist.txt
│       ├── ...
│       └── vision_playlist.txt
├── models
│   └── trainer_baseline.ipynb
└── utils
    ├── data_preparation.py
    ├── preprocess.py
    ├── setup.sh
    └── transcript_extractor.py

```
---
> ## Dataset

* `open_source`, `youtube_urls` : Opensource, youtube's meta data 

* `utils` : youtube 영상으로부터 transcript 추출 및 전처리

* `actual dataset` : 실제 데이터는 `huggingface` 업로드 후 사용
    * [Our team Dataset Huggingface Link](https://huggingface.co/datasets/ht324/WhiteBoard_LLM_Data)
    *  사용 예시 : ```dataset = load_dataset(data_path)```


> ## Models
* `trainer.ipynb` : kaggle, colab에서 학습에 사용하는 코드

* `trained_models`: 학습된 모델은 `huggingface` 업로드 후 사용
    * [Our team Model Huggingface Link](https://huggingface.co/ht324/WhiteBoard_LLM_Models)