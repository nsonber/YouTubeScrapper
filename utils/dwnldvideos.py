from pytube import YouTube


def download_video(url, title, download_path):
    try:
        # object creation using YouTube
        # which was imported in the beginning
        yt = YouTube(url)
    except:
        print("Connection Error")  # to handle exception

    stream = yt.streams.filter(file_extension='mp4')
    stream.get_by_itag(22).download(output_path=download_path, filename=title[0:40], filename_prefix='mp4')

    return
