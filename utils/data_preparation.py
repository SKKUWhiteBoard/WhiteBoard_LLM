import os
from multiprocessing import Pool
# Assume these are your custom functions for handling YouTube playlists
from transcript_extractor_autoTranscript import get_videos_from_playlist, get_video_id_from_url, get_playlist_transcript
from preprocess import preprocess_youtube_dataset

def process_single_playlist(filepath, raw_transcript_dir, processed_transcript_dir):
    """
    하나의 _playlist.txt 파일을 처리: transcript 추출 및 전처리.
    """
    try:
        # 파일 이름에서 플레이리스트 이름 추출
        playlist_name = os.path.splitext(os.path.basename(filepath))[0]
        print(f"Processing file: {filepath}")

        # 읽어들인 URL 리스트 처리
        with open(filepath, 'r') as file:
            playlist_urls = [line.strip() for line in file if line.strip()]

        for idx, playlist_url in enumerate(playlist_urls):
            print(f"[Extracting playlist {idx + 1}/{len(playlist_urls)}: {playlist_url}]")

            try:
                # Transcript 추출
                pl_name, video_names, video_urls = get_videos_from_playlist(playlist_url)
                video_ids = get_video_id_from_url(video_urls)
                get_playlist_transcript(pl_name, video_names, video_ids, raw_transcript_dir)
            except Exception as e:
                print(f"Error processing playlist {playlist_url}: {e}")

        # 전처리 수행
        preprocess_youtube_dataset(raw_transcript_dir, processed_transcript_dir)
        print(f"Preprocessing completed for: {playlist_name}")
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")

def process_all_playlists_in_parallel(input_dir, raw_transcript_dir, processed_transcript_dir, num_workers=4):
    """
    멀티 프로세스를 사용하여 모든 _playlist.txt 파일 처리.
    """
    # Ensure directories exist
    os.makedirs(raw_transcript_dir, exist_ok=True)
    os.makedirs(processed_transcript_dir, exist_ok=True)

    # _playlist.txt 파일 경로 리스트 생성
    playlist_files = [
        os.path.join(input_dir, filename)
        for filename in os.listdir(input_dir)
        if filename.endswith('_playlist.txt')
    ]

    # 멀티 프로세스 풀 생성
    with Pool(processes=num_workers) as pool:
        # 각 파일을 독립적으로 처리
        pool.starmap(
            process_single_playlist,
            [(filepath, raw_transcript_dir, processed_transcript_dir) for filepath in playlist_files]
        )

if __name__ == '__main__':
    # Directories
    url_dir = '../data/youtube_urls'
    raw_transcript_dir = '../data/raw_dataset/youtube_dataset'
    processed_transcript_dir = '../data/preprocessed_dataset/youtube_dataset'

    # Step: Process all playlists in parallel
    process_all_playlists_in_parallel(url_dir, raw_transcript_dir, processed_transcript_dir, num_workers=20)

    print("Transcripts extraction and preprocessing completed.")