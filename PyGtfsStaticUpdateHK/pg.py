from pytube import YouTube

def download_youtube_video(video_url, download_path='.'):
    try:
        yt = YouTube(video_url)
        stream = yt.streams.get_highest_resolution()
        stream.download(download_path)
        print(f"Downloaded: {yt.title}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    video_url = input("https://www.youtube.com/watch?v=m7i2xSxYS3o ")
    download_path = input("./") or '.'
    download_youtube_video(video_url, download_path)
