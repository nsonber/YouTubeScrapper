import time

from selenium.common import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, urlunparse, urlencode, parse_qsl
# import logging
from utils.logger import logger



class CustomError(Exception):
    pass


def add_args_to_url(url, params: dict):
    if type(url) == str:
        url = url.encode('utf-8')
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query).encode('utf-8')
    logger.debug(f" various parts to join : {url_parts} datatype {type(url_parts)}")

    return urlunparse(url_parts).decode("utf-8")


class Scrapper:

    def __init__(self, in_url):
        self.url = in_url
        self.video_urls = []

    def valid_url(self):
        """

        :return:
        """
        if urlparse(self.url).netloc != b'www.youtube.com':
            logger.debug(urlparse(self.url).netloc)
            raise CustomError("This is not a youtube URL")
        else:
            urlpath = urlparse(str(self.url)).path.split('/')

            if urlpath[5].strip("'") == 'videos':
                args = dict({'view': '0', 'sort': 'dd', 'flow': 'grid'})
                self.url = add_args_to_url(self.url, args)
            else:
                logger.debug(f"{urlpath[5]} Datatype {type(urlpath[5])}")
                raise CustomError("This is an invalid youtube URL for channel")
        return True

    def get_latest_channel_videos(self, max_videos_to_fetch):
        """

        :param max_videos_to_fetch:
        :return:
        """
        logger.debug(f"Getting latest {max_videos_to_fetch} videos from {self.url}")

        chrome_options = Options()
        chrome_options.add_argument('--headless')

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

        logger.debug(f"url is {self.url} with type {type(self.url)}")

        driver.get(self.url)

        video_count = 0
        while video_count < int(max_videos_to_fetch):
            video_count += 1
            video_frame = driver.find_element(By.CSS_SELECTOR,
                                              f"#items > ytd-grid-video-renderer:nth-child({video_count})")
            driver.execute_script("arguments[0].scrollIntoView();", video_frame)
            # get all metadata of videos & thumbnail
            link = video_frame.find_element(By.CSS_SELECTOR, "#video-title").get_attribute("href")
            title = video_frame.find_element(By.CSS_SELECTOR, "#video-title").get_attribute("title")
            thumbnail_src = video_frame.find_element(By.CSS_SELECTOR, "#img").get_attribute("src")

            d_videos = dict({'link': link, 'title': title, 'thumbnail_src': thumbnail_src})

            self.video_urls.append(d_videos)

        driver.close()

        return

    def get_likes_n_comments(self):
        """

        :param self:
        :return:
        """

        def element_exists(frame, css_selector):
            """

            :param frame:
            :param css_selector:
            :return:
            """
            try:
                frame.find_element(By.CSS_SELECTOR, css_selector)
            except NoSuchElementException:
                return False
            return True

        def comments_exists(utube_driver):

            found_comments = False

            if element_exists(utube_driver, "#contents > ytd-message-renderer"):
                no_comments = utube_driver.find_element(By.CSS_SELECTOR,
                                                        "#contents > ytd-message-renderer").text
                logger.debug(no_comments)
                found_comments = not (no_comments.split('.')[0].__contains__("turned off"))
            elif element_exists(utube_driver, "#count > yt-formatted-string"):
                Total_Comments = driver.find_element(By.CSS_SELECTOR, "#count > yt-formatted-string").text.rsplit(' ')[
                    0]
                logger.debug(f"Total_Comments : {Total_Comments}")
                if Total_Comments.isdigit():
                    if int(Total_Comments) > 0:
                        found_comments = True

            return found_comments

        chrome_options = Options()
        # chrome_options.add_argument('--headless')

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

        updated_videos = []

        for elem in self.video_urls:
            url = elem.get("link")

            if url.__contains__("shorts"):
                elem.update({"like_count": like_count,
                             "comment_count": 0,
                             "all_comments": dict({})
                             })
                # if int(Total_Comments) == comment_count:
                #     moreCommentsExists = False
                updated_videos.append(elem)
            else:
                # Disable Autoplay of videos
                url1 = add_args_to_url(url, {'autoplay': 0})

                driver.get(url1)
                driver.maximize_window()
                time.sleep(2)
                # driver.find_element(By.CSS_SELECTOR, "#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > "
                #                                      "div.ytp-left-controls > button").click()
                driver.execute_script("window.scrollTo(0, 200);")
                time.sleep(1)

                like_count = driver.find_element(By.CSS_SELECTOR,
                                                 "#top-level-buttons-computed > ytd-toggle-button-renderer:nth-child(1)").text

                if comments_exists(driver):
                    comment_frame = driver.find_element(By.CSS_SELECTOR, "#sections")
                    comment_sect = comment_frame.find_element(By.CSS_SELECTOR, "#comment")
                    driver.execute_script("arguments[0].scrollIntoView();", comment_sect)

                    moreCommentsExists = True
                    comment_count = 0
                    # d_comments = {'comment#': '', "comment_author": '', "comment_text": ''}
                    all_comments = []
                    while moreCommentsExists:
                        comment_count += 1
                        # print(comment_count)
                        comment_section = comment_frame.find_element(By.CSS_SELECTOR,
                                                                     f"#contents > ytd-comment-thread-renderer:nth-child({comment_count})")
                        driver.execute_script("arguments[0].scrollIntoView();", comment_section)
                        comment_author = comment_section.find_element(By.CSS_SELECTOR, "#author-text").text
                        comment_text = comment_section.find_element(By.CSS_SELECTOR, "#content-text").text

                        # print(comment_author)
                        # print(comment_text)
                        d_comments = dict({'comment#': comment_count,
                                           "comment_author": comment_author,
                                           "comment_text": comment_text})

                        all_comments.append(d_comments)

                        moreCommentsExists = element_exists(comment_frame,
                                                            f"#contents > ytd-comment-thread-renderer:nth-child({comment_count + 1})")
                        # print(moreCommentsExists)

                    elem.update({"like_count": like_count,
                                 "comment_count": comment_count,
                                 "all_comments": all_comments
                                 })
                    # if int(Total_Comments) == comment_count:
                    #     moreCommentsExists = False
                    updated_videos.append(elem)
                else:
                    elem.update({"like_count": like_count,
                                 "comment_count": 0,
                                 "all_comments": dict({})
                                 })
                    # if int(Total_Comments) == comment_count:
                    #     moreCommentsExists = False
                    updated_videos.append(elem)

        driver.close()

        self.video_urls = updated_videos

        return
