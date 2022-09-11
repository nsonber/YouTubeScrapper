from flask import Flask, render_template, request, session, redirect
from flask_cors import cross_origin
from flask_session import Session

from scrapper import Scrapper
from utils.logger import logger
from utils.dwnldvideos import download_video
from utils.mongodbcm import SaveToMongo

app = Flask(__name__)
# Check Configuration section for more details
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)

app.config['dbconfig'] = {'host': 'localhost',
                          'user': 'root',
                          'password': "Mysql@Jul22",
                          'database': "YouTube", }

app.config['mongoconfig'] = {'host': 'cluster0.iertm.mongodb.net/?retryWrites=true&w=majority',
                             'user': 'ineuronmongo',
                             'password': 'ineuron1',
                             'database': 'YouTubeComments',
                             'collection': 'Comments'
                             }

Session(app)


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index2.html")


@app.route('/search', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def search():
    # print("Am i  here")
    if request.method == 'POST':
        # url = 'https://www.youtube.com/user/krishnaik06/videos'
        url = request.form['url'].encode()
        logger.debug(f"Url is {url} of datatype {type(url)}")
        max_videos_to_fetch = request.form['Max_Video_Count']
        sc = Scrapper(url)
        sc.valid_url()
        sc.get_latest_channel_videos(max_videos_to_fetch)
        sc.get_likes_n_comments()
        session['videos'] = sc.video_urls
        return render_template('results2.html', videos=sc.video_urls)
    else:
        print(f"here {request.method}")
        return render_template('index2.html')


@app.route('/save_data', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def save_to_db():
    videos = session.get('videos')
    if request.method == 'POST':
        logger.debug(f"Data type of videos {type(videos)}")
        logger.debug(f"Length of videos {len(videos)}")
        # for video in videos:
        #     download_video(video['link'], video['title'], '/downloads')
        #     with SaveToMongo(app.config['mongoconfig']) as coll:
        #         result = coll.insert_many(dict({'Video_url': video.get('link'), 'Comments': video.get('all_comments')}))
    return redirect(request.referrer)


if __name__ == "__main__":
    # app.run(host='127.0.0.1', port=8001, debug=True)
    app.run()
