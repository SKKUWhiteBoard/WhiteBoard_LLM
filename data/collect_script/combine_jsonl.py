import os
import json

def convert_preprocessed_to_jsonl(preprocessed_path, output_jsonl_path):
    # JSONL 파일 생성
    with open(output_jsonl_path, 'w') as jsonl_file:
        for playlist_name in os.listdir(preprocessed_path):
            playlist_path = os.path.join(preprocessed_path, playlist_name)
            
            if not os.path.isdir(playlist_path):
                continue  # 디렉토리가 아닌 경우 건너뜀
            
            for file_name in os.listdir(playlist_path):
                file_path = os.path.join(playlist_path, file_name)
                
                with open(file_path, 'r') as f:
                    content = f.read().strip()  # 텍스트 파일 내용 읽기

                # JSON 객체 작성
                json_object = {
                    "playlist": playlist_name,
                    "file_name": file_name,
                    "content": content
                }

                # JSON 객체를 JSONL 형식으로 파일에 저장
                jsonl_file.write(json.dumps(json_object) + '\n')

if __name__ == '__main__':
    preprocessed_path = '../preprocessed_dataset/youtube_dataset'
    output_jsonl_path = '../preprocessed_dataset/youtube_dataset.jsonl'

    convert_preprocessed_to_jsonl(preprocessed_path, output_jsonl_path)
