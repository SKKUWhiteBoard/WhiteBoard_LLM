#!/bin/bash

# 실험 파라미터 설정
N_WORDS=(100 150 200 2000)
N_OVERLAPS=(0 10)
THRESHOLDS=(0.7 0.8 0.9)
METHODS=("ward" "single" "complete" "average")

# 12GB 기준 배치 크기 고정
BATCH_SIZE=12  # 추정치. 필요하면 조정 가능.

# 실험 번호
EXPERIMENT_ID=1

# 결과 저장 디렉토리 생성
RESULT_DIR="experiment_results"
mkdir -p $RESULT_DIR

# 루프를 돌며 config.yaml 파일 생성 및 실험 실행
for n_word in "${N_WORDS[@]}"; do
  for n_overlap in "${N_OVERLAPS[@]}"; do
    for threshold in "${THRESHOLDS[@]}"; do
      for method in "${METHODS[@]}"; do
        
        # 실험 이름 설정
        EXPERIMENT_NAME="hierarchical_nw${n_word}_no${n_overlap}_th${threshold}_${method}"

        # config.yaml 생성
        cat <<EOL > config.yaml
experiment_name: "$EXPERIMENT_NAME"

mini_batch:
  size: $BATCH_SIZE

data:
  source: "opensource"
  opensource: "ccdv/govreport-summarization"
  youtube: "WhiteboardLLM/Data"
  index_set: 1

segment:
  args:
    n_word: $n_word
    n_overlap: $n_overlap
    fix_size: False

concat:
  method: "concate_hierarchical_clustering"
  args:
    threshold: $threshold
    method: "$method"

summary:
  args:
    min_length: 100
    max_length: 1024

save_summaries: True
EOL

        # 실험 실행
        echo "Running Experiment $EXPERIMENT_ID: $EXPERIMENT_NAME"
        python3 experiment.py > $RESULT_DIR/${EXPERIMENT_NAME}.log

        # 실험 번호 증가
        EXPERIMENT_ID=$((EXPERIMENT_ID + 1))
      done
    done
  done
done

echo "All experiments completed!"
