import json
import requests

from flask import Flask
from flask import render_template
from flask import request as flask_request


app = Flask(__name__)

# change to your own id/secret.
CLIENT_ID = 'MY_CLINET_ID'
CLIENT_SECRET = 'MY_CLIENT_SECRET'


def _read_data_file():
    with open('user_info.json', 'r') as load_file:
        try:
            load_data = json.load(load_file)
        except Exception:
            load_data = {}
    return load_data


def _write_data_file(data):
    old_data = _read_data_file()
    new_data = None
    if not old_data:
        new_data = {data['login']: data}
    else:
        if not old_data.get(data['login']):
            old_data.update({data['login']: data})
            new_data = old_data
    if new_data:
        with open('user_info.json', 'w') as load_file:
            try:
                json.dump(new_data, load_file)
            except Exception:
                pass


@app.route('/')
def index():
    data = _read_data_file()
    oauth_url = ("https://github.com/login/oauth/authorize?scope="
                 "user:email&amp;client_id=%s" % CLIENT_ID)
    return render_template("index.html", data=data, oauth_url=oauth_url)


@app.route('/callback')
def github_oauth_callback():

    query_dict = flask_request.args.to_dict()
    oauth_code = query_dict['code']
    result = requests.post(
        url='https://github.com/login/oauth/access_token',
        json={'client_id': CLIENT_ID,
              'client_secret': CLIENT_SECRET,
              'code': oauth_code,
              'accept': 'json'})
    access_token = None
    for text in result.text.split('&'):
        if 'access_token' in text:
            access_token = text.split('=')[1]
            break
    if access_token:
        result = requests.get(
            url='https://api.github.com/user?access_token=%s' % access_token)
        user_info = json.loads(result.text)
        login_name = user_info['login']
        user_name = user_info['name']
        user_email = user_info['email']
        user_company = user_info['company']
        created_at = user_info['created_at']
        public_repos = user_info['public_repos']
        followers = user_info['followers']
        following = user_info['following']
        _write_data_file(user_info)
        return render_template(
            "user_info.html", login_name=login_name,
            name=user_name, email=user_email,
            company=user_company, created_at=created_at,
            public_repos=public_repos, followers=followers,
            following=following)
    return ("Internal Error. Please connect to wxy(wangxiyuan1007@gmail.com) "
            "for help.")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
