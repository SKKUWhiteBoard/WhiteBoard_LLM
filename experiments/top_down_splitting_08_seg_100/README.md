# top_down_splitting_08_seg_100

1. top_down_splitting: 큰 덩어리부터 encoding 후 비교하여 일정 threshold 이하인 경우 재귀적으로 split하는 방식
    - threshold 값에 따라 재귀적으로 분할하므로 시간 오래 걸림
2. 점수 분포가 다양함
3. threshold가 낮으면 각 클러스터 크기가 커지지만 score는 좋지 않음, 0.8 이상에서 좋은 score가 발생하는 경우가 많음