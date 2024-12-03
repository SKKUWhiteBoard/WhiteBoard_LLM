#!/bin/bash

# 실험 폴더 경로
EXPERIMENTS_DIR="experiments"

# 결과 저장 파일
OUTPUT_FILE="top_5_experiments.txt"

# 중간 파일 초기화
TEMP_FILE=$(mktemp)

# 모든 experiments 폴더를 순회하며 results.txt 읽기
for dir in "$EXPERIMENTS_DIR"/*; do
    if [ -d "$dir" ] && [ -f "$dir/results.txt" ]; then
        # results.txt에서 점수 추출
        rouge1_mean=$(grep "rouge1: mean=" "$dir/results.txt" | awk -F'[=,]' '{print $2}')
        rouge2_mean=$(grep "rouge2: mean=" "$dir/results.txt" | awk -F'[=,]' '{print $2}')
        rougeL_mean=$(grep "rougeL: mean=" "$dir/results.txt" | awk -F'[=,]' '{print $2}')
        bert_score_mean=$(grep "bert_score: mean=" "$dir/results.txt" | awk -F'[=,]' '{print $2}')

        # 모든 점수의 합 계산
        total_score=$(echo "$rouge1_mean + $rouge2_mean + $rougeL_mean + $bert_score_mean" | bc)

        # 디렉토리 이름과 합산 점수를 임시 파일에 저장
        echo "$total_score $dir" >> "$TEMP_FILE"
    fi
done

# 점수 기준으로 상위 5개 선택
echo "Top 5 experiments:" > "$OUTPUT_FILE"
sort -nr "$TEMP_FILE" | head -n 5 >> "$OUTPUT_FILE"

# 결과 출력
cat "$OUTPUT_FILE"

# 임시 파일 삭제
rm "$TEMP_FILE"
