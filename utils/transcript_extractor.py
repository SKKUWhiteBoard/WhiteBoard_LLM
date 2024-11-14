# built-in modules
import os
import time

# third-party modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from youtube_transcript_api import YouTubeTranscriptApi


# *********************** Get each video's url from the playlist ***********************
def init_selenium():
    """
    Selenium 드라이버 초기화

    Returns:
        driver (webdriver.Chrome): 초기화된 드라이버
    """
    chrome_path = '/usr/bin/google-chrome-stable'

    options = webdriver.ChromeOptions()
    options.binary_location = chrome_path
    options.add_argument("--headless")  # background without opening browser
    options.add_argument('--no-sandbox')  # Sandbox 옵션 비활성화
    options.add_argument('--disable-dev-shm-usage')  # 메모리 공유 비활성화

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def get_videos_from_playlist(playlist_url):
    """
    플레이리스트 url로부터 비디오 정보 추출

    Args:
        playlist_url (str): 플레이리스트 url

    Returns:
        playlist_name (str): 플레이리스트 이름
        video_names (list): 비디오 이름 리스트
        video_urls (list): 비디오 url 리스트
    """
    print("Extracting video urls from the playlist... ", end='', flush=True)

    driver = init_selenium()
    driver.get(playlist_url)
    time.sleep(1)  # wait for page to load

    try:
        video_elements = driver.find_elements(By.XPATH, '//a[@id="video-title"]')
        
        video_urls = [video.get_attribute('href') for video in video_elements]
        video_names = [video.get_attribute('title') for video in video_elements]

        playlist_name = driver.find_element(By.XPATH, '//span[@class="yt-core-attributed-string yt-core-attributed-string--white-space-pre-wrap"]').text
    except Exception as e:
        print(f"Error occurred: {e}")

    driver.quit()

    print("Done.")
    return playlist_name, video_names, video_urls

# ************************* parsing video id from url *************************
def get_video_id_from_url(video_urls):
    """
    비디오 url로부터 비디오 id 추출

    Args:
        video_urls (list[str]): 비디오 url 리스트

    Returns:
        video_ids (list[str]): 비디오 id 리스트
    """
    return [url.split('v=')[1].split('&')[0] for url in video_urls]


# ************************* Extracting subtitles *************************
def convert_transcript_format(transcript):
    """
    딕셔너리 형태의 객체를 텍스트로 변환
    [{'text': 'Hello world.', 'start': 1.0, 'duration': 2.0}, ...] -> "hh:mm:ss Hello world.\nhh:mm:ss Hello world. ..."

    Args:
        transcript (list[dict]): 비디오 자막 정보

    Returns:
        converted_transcript (list[str]): 변환된 텍스트 리스트
    """
    converted_transcript = []
    for line in transcript:
        start = int(line['start'])
        start = time.strftime('%H:%M:%S', time.gmtime(start))
        
        text = line['text'].replace('\n', ' ') # new line to space
        converted_transcript.append(f"{start} {text}")
    return converted_transcript

def get_playlist_transcript(playlist_name, video_names, video_ids):
    """
    플레이리스트의 각 비디오로부터 자막 추출
    플레이리스트 이름으로 폴더 생성 후 각 비디오의 자막을 텍스트 파일로 저장, 각 파일의 이름은 <비디오 이름>.txt

    Args:
        playlist_name (str): 플레이리스트 이름
        video_names (list[str]): 비디오 이름 리스트
        video_ids (list[str]): 비디오 id 리스트

    Returns:
        None
    """
    playlist_path = os.path.join(os.getcwd(), playlist_name)
    if not os.path.exists(playlist_path):
        os.makedirs(playlist_path)

    for video_name, video_id in zip(video_names, video_ids):
        print(f"Extracting subtitles from video: {video_name}... ", end='', flush=True)
        try:
            # 자동생성이 아닌 수동 입력된 자막을 추출
            # 오류 발생 시 아래 리스트에 수동 생성된 자막이 없다는 것이므로 오류의 (MANUALLY CREATED)에 있는 언어를 아래 리스트에 추가
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id).find_manually_created_transcript(['en', 'en-US'])
            transcript = transcript_list.fetch()
            converted_transcript = convert_transcript_format(transcript)
            
            with open(os.path.join(playlist_path, f"{video_name}.txt"), 'w') as f:
                f.write('\n'.join(converted_transcript))
        except Exception as e:
            print(f"Error occurred: {e}")
        print("Done.")
    
    return None

if __name__ == '__main__':
    playlist_urls = [
        'https://www.youtube.com/playlist?list=PL3FW7Lu3i5JvHM8ljYj-zLfQRF3EO8sYv',
        'https://www.youtube.com/playlist?list=PLoROMvodv4rPOWA-omMM6STXaWW4FvJT8',
        'https://www.youtube.com/playlist?list=PLoROMvodv4rMp7MTFr4hQsDEcX7Bx6Odp',

    ]

    for idx, playlist_url in enumerate(playlist_urls):
        print(f"[Extracting playlist {idx+1}/{len(playlist_urls)}: {playlist_url}]")
        playlist_name, video_names, video_urls = get_videos_from_playlist(playlist_url)
        video_ids = get_video_id_from_url(video_urls)
        get_playlist_transcript(playlist_name, video_names, video_ids)