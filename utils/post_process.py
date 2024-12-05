import os
import yaml

def process_experiment_folder(folder_path):
    # 1. config.yaml 파일 읽기
    config_path = os.path.join(folder_path, "config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    source = config["data"]["source"]
    index_set = config["data"]["index_set"]
    
    # 2. summaries.txt 처리
    summaries_path = os.path.join(folder_path, "summaries.txt")
    rouge_scores_path = os.path.join(folder_path, "ROUGE_scores.txt")
    bert_scores_path = os.path.join(folder_path, "bert_score.txt")
    new_summaries_path = os.path.join(folder_path, "_summaries.txt")
    
    with open(summaries_path, "r") as f:
        lines = f.readlines()
    
    rouge_scores = []
    bert_scores = []
    summaries = []
    current_summary = []
    is_summary_section = False  # Summary 섹션을 확인하는 플래그

    for line in lines:
        if line.startswith("===================="):
            if current_summary:  # 이전 블록 저장
                summaries.append("".join(current_summary))
                current_summary = []
                is_summary_section = False  # Summary 블록 종료
        elif line.startswith("ROUGE-"):
            # ROUGE 점수 파싱
            scores = line.strip().split(", ")
            rouge_scores.append(scores)
        elif line.startswith("BERTScore:"):
            # BERTScore 점수 파싱
            bert_scores.append(float(line.split(":")[1].strip()))
        elif "Summary:" in line:  # Summary: 키워드 제거
            is_summary_section = True
            current_summary.append(line.replace("Summary:", "").strip())
        elif is_summary_section:
            # Summary 블록 내용 추가
            current_summary.append(line.strip())
    
    if current_summary:  # 마지막 블록 저장
        summaries.append("".join(current_summary))
    
    # 3. ROUGE 점수 파일 저장
    with open(rouge_scores_path, "w") as f:
        for i, scores in enumerate(rouge_scores, start=1):
            formatted_scores = [f"{score.split(':')[0]}: {float(score.split(':')[1]):.2f}" for score in scores]
            f.write(f"[{i}] " + "\t".join(formatted_scores) + "\n")
    
    # 4. BERT 점수 파일 저장
    with open(bert_scores_path, "w") as f:
        for i, score in enumerate(bert_scores, start=1):
            f.write(f"[{i}] BERTScore: {score:.2f}\n")
    
    # 5. 새로운 summaries 파일 생성
    with open(new_summaries_path, "w") as f:
        f.write(f"{source}\n{index_set}\n")  # Source와 Index 사이 줄 바꿈 추가
        f.write("\n".join(summaries))  # Summary 사이 줄 바꿈 추가

def main():
    base_directory = "."  # 현재 디렉토리 기준
    for folder_name in os.listdir(base_directory):
        folder_path = os.path.join(base_directory, folder_name)
        if os.path.isdir(folder_path):  # 폴더만 처리
            process_experiment_folder(folder_path)

if __name__ == "__main__":
    main()