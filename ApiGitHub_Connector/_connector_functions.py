import requests
import pandas as pd
from pandas.io.json import json_normalize
import time

def create_session(user, pwd):

    try:
        session = requests.Session()
        session.auth = (user, pwd)
        r = session.get("https://api.github.com/user")
        assert r.ok
    except ValueError:
        print("Can't connect to the API, please make sure that you use the rigth credentials")

    return session


def url_builder(action_type, user_name, **kwargs):

    url = "https://api.github.com/{}/".format(action_type)

    _repo = kwargs.get('repo_name', None)
    _search_path = kwargs.get('search_path', None)
    _set_per_page_limit = kwargs.get('set_per_page_limit', False)
    _is_iterator_per_page = kwargs.get('iterate_per_page', False)
    _other_option = kwargs.get('other_option', False)

    if _repo is None:
        url = url + str(user_name) + "/{}".format(_search_path) + "?"
    else:
        url = url + str(user_name) + "/{}".format(_repo) + "/{}".format(_search_path) + "?"

    if _set_per_page_limit:
        url = url + "per_page=100"

    if _is_iterator_per_page:
        url = url + "&page={}"

    if _other_option:
        if _set_per_page_limit:
            url = url + "&{}".format(_other_option)
        else:
            url = url + str(_other_option)

    return url


def compile_by_page(session, url, **kwargs):
    _func = kwargs.get('_transform_function', None)

    i = 1
    _stop = False
    _output_set = None

    tic = time.time()
    while _stop == False:

        r = session.get(url.format(i))

        if (not r.json()) or (r.ok == False):
            _stop = True
        else:
            if _func is None:
                _output_set = pd.concat([_output_set, pd.DataFrame(r.json())], axis=0)
            else:
                _output_set = pd.concat([_output_set, _func(pd.DataFrame(r.json()))], axis=0)
            i += 1

    print("the api scrapper did his job in {} seconds".format(time.time() - tic))

    return _output_set


def pull_request_transformer(data):

    _works_data = json_normalize(data=data["user"])
    _works_data[["login", "node_id"]]
    final_pull_request = pd.concat([data[["closed_at", "state", "updated_at", "created_at", "merged_at"]],
                                _works_data[["login", "node_id"]]], axis=1)

    return final_pull_request



def compute_files(session, user, repo, dir_path, num_files):
    if dir_path is not None:
        url = "https://api.github.com/repos/{}/{}/contents".format(user, repo) + "/" + str(dir_path)
    else:
        url = "https://api.github.com/repos/{}/{}/contents".format(user, repo)
    r = session.get(url)
    data = pd.DataFrame(r.json())
    if data.loc[data.type == "dir","path"].shape[0] > 0:
        num_files = num_files + data.loc[data.type != "dir", "path"].shape[0]
        for dir_path in list(data.loc[data.type == "dir", "path"]):
            num_files = compute_files(session, user, repo, dir_path, num_files)
    else:
        num_files = num_files + data.loc[data.type != "dir", "path"].shape[0]
    return num_files


def compile_repos_stats(session, user_name):
    url = url_builder(action_type="users",
                      user_name=user_name,
                      search_path="repos",
                      set_per_page_limit=True,
                      iterate_per_page=True)

    _output_stats = compile_by_page(session, url, _transform_function=repos_stats_transformer)

    return _output_stats


def repos_stats_transformer(data):
    data = data[["created_at","default_branch","description","forks_count","language","license","name","open_issues_count","owner",
          "permissions","private","pushed_at","stargazers_count","updated_at","watchers_count"]]
    return data


def contributors_commits_transformer(data):

    if "login" not in data.columns:
        data["login"] = ""
    if "email" not in data.columns:
        data["email"] = ""
    if "contributions" not in data.columns:
        data["contributions"] = ""
    if "type" not in data.columns:
        data["type"] = ""

    data = data[["email", "contributions", "login", "type"]]

    return data

def release_transformer(data):
    _works_data = json_normalize(data=data["author"])
    _output = pd.concat([data[["name", "published_at", "created_at", "tag_name"]],
                                _works_data[["login"]]], axis=1)
    return _output


def update_stats(session, user_stats, list_names, user_name):
    repos_stats_issues = dict()
    repos_stats_pull_requests = dict()

    for repo in list_names:
        repos_stats_issues[repo] = session.get(
            "https://api.github.com/search/issues?q=repo:{}/{}+type:issue".format(user_name, repo)).json()[
            'total_count']
        repos_stats_pull_requests[repo] = session.get(
            "https://api.github.com/search/issues?q=repo:{}/{}+type:pr".format(user_name, repo)).json()['total_count']

    df1 = pd.DataFrame.from_dict(repos_stats_issues, orient='index')
    df2 = pd.DataFrame.from_dict(repos_stats_pull_requests, orient='index')
    df1.columns = ["total_issues"]
    df2.columns = ["total_pull_requests"]
    df_end = pd.merge(df1, df2, left_index=True, right_index=True, how="inner"). \
        reset_index(drop=False).rename(columns={"index": "name"})

    user_stats = pd.merge(user_stats, df_end, how='inner', on="name")

    return user_stats