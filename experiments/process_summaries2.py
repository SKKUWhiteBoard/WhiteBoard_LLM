import os

def split_summaries_into_files(folder_path):
	summaries_path = os.path.join(folder_path, "_summaries.txt")
	summaries_folder = os.path.join(folder_path, "summaries")

	# Summaries 폴더 생성
	if not os.path.exists(summaries_folder):
		os.makedirs(summaries_folder)

	with open(summaries_path, "r") as f:
		lines = f.read().strip().split("\n")

	# 첫 두 줄 (source와 index) 처리
	source = lines[0]
	index = lines[1]
	summaries = lines[2:]  # Summary만 분리

	if len(summaries) != 100:
		raise ValueError(f"Error in folder '{folder_path}': Found {len(summaries)} summaries, expected 100.")

	# Summary를 각각의 파일로 저장
	for i, summary in enumerate(summaries, start=1):
		summary_file_path = os.path.join(summaries_folder, f"summary_{i}.txt")
		with open(summary_file_path, "w") as f:
			f.write(summary.strip())

	print(f"Summaries saved to '{summaries_folder}' folder.")

def main():
    base_directory = "."  # 현재 디렉토리 기준
    for folder_name in os.listdir(base_directory):
        folder_path = os.path.join(base_directory, folder_name)
        if os.path.isdir(folder_path):
            split_summaries_into_files(folder_path)

if __name__ == "__main__":
    main()
