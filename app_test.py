import unittest
from scrapper import Scrapper
from utils.logger import logger


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)  # add assertion here
        url = 'https://www.youtube.com/channel/UC4k_yOMhQtmy4pGPOkGVF-A/videos'
        url = url.encode()
        # logger.debug(f"Url is {url} of datatype {type(url)}")
        max_videos_to_fetch = 10  # request.form['Max_Video_Count']
        sc = Scrapper(url)
        sc.valid_url()
        sc.get_latest_channel_videos(max_videos_to_fetch)
        sc.get_likes_n_comments()

        return sc.video_urls


if __name__ == '__main__':
    unittest.main()
