import os

def preprocess_youtube_dataset(unprocessed_path, processed_path):
    if not os.path.exists(processed_path):
        os.makedirs(processed_path)

    for playlist_name in os.listdir(unprocessed_path):
        print(f"Processing {playlist_name}... ", end='', flush=True)
        
        playlist_path = os.path.join(unprocessed_path, playlist_name)
        
        if not os.path.exists(os.path.join(processed_path, playlist_name)):
            os.makedirs(os.path.join(processed_path, playlist_name))

        transcript_file_names = os.listdir(playlist_path)

        for file_name in transcript_file_names:
            with open(os.path.join(playlist_path, file_name), 'r') as f:
                transcript = f.readlines()

            converted_transcript = []
            for line in transcript:
                _, text = line.split(' ', 1) # do not use start time
                
                # remove speaker tags
                if '[' in line or ']' in line:
                    splitted = text.split(' ')
                    for word in splitted:
                        if word.startswith('[') and word.endswith(']'):
                            text = text.replace(word, '')
                # remove multiple spaces
                while '  ' in text:
                    text = text.replace('  ', ' ')
                
                converted_transcript.append(text.strip())

            with open(os.path.join(processed_path, playlist_name, file_name), 'w') as f:
                f.write(' '.join(converted_transcript))
        
        print("Done.")

def preprocess_youtube_dataset_light(unprocessed_path, processed_path):
    if not os.path.exists(processed_path):
        os.makedirs(processed_path)

    for playlist_name in os.listdir(unprocessed_path):
        print(f"Processing {playlist_name}... ", end='', flush=True)
        
        playlist_path = os.path.join(unprocessed_path, playlist_name)
        
        if not os.path.exists(os.path.join(processed_path, playlist_name)):
            os.makedirs(os.path.join(processed_path, playlist_name))

        transcript_file_names = os.listdir(playlist_path)

        for file_name in transcript_file_names:
            with open(os.path.join(playlist_path, file_name), 'r') as f:
                transcript = f.readlines()

            processed_transcript = []
            for line in transcript:
                # Remove timeline by splitting at the first space
                _, text = line.split(' ', 1)
                processed_transcript.append(text.strip())

            # Combine all lines into a single line (removing newlines)
            combined_transcript = ' '.join(processed_transcript)

            with open(os.path.join(processed_path, playlist_name, file_name), 'w') as f:
                f.write(combined_transcript)
        
        print("Done.")

if __name__ == '__main__':
    unprocessed_path = '../data/raw_dataset/youtube_dataset'
    processed_path = '../data/preprocessed_dataset/youtube_dataset'

    #preprocess_youtube_dataset(unprocessed_path, processed_path)
    preprocess_youtube_dataset_light(unprocessed_path, processed_path)