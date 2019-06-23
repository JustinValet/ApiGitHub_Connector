from ApiGitHub_Connector._connector_functions import *
import time
import pandas as pd

class connect_to_GitHub_API:

    def __init__(self, user, pwd):
        self.user = user
        self.pwd = pwd
        self._api_session = create_session(self.user, self.pwd)

class GitHub_API_Connector(connect_to_GitHub_API):

    def __init__(self, user, pwd, user_name):
        self._user_name = user_name
        connect_to_GitHub_API.__init__(self, user, pwd)
        self._user_stats = compile_repos_stats(self._api_session, self._user_name)
        self._repos_names = list(self._user_stats["name"])
        self._user_stats = update_stats(self._api_session, self._user_stats, self._repos_names, self._user_name)

    def extract_contributors_stats(self, repo, **kwargs):

        add_other_option = kwargs.get('add_other_option', None)

        if add_other_option is None:
            other_option = "anon=1"
        else:
            other_option = "anon=1"+"&"+add_other_option

        url = url_builder(action_type="repos",
                          user_name=self._user_name,
                          repo_name=repo,
                          search_path="contributors",
                          set_per_page_limit=True,
                          iterate_per_page=True,
                          other_option=other_option)
        print(url)

        _output = compile_by_page(self._api_session, url, _transform_function=contributors_commits_transformer)

        return _output

    def count_number_files(self, repo):

        num_files = 0
        num_files = compute_files(self._api_session, self._user_name, repo, None, num_files)

        return num_files

    def extract_branches(self, repo):

        url = url_builder(action_type="repos",
                          user_name=self._user_name,
                          repo_name=repo,
                        search_path="branches")

        r = self._api_session.get(url)
        data = pd.DataFrame(r.json())
        data = data[["name", "protected"]]

        return data

    def extract_releases(self, repo):
        url = url_builder(action_type="repos",
                          user_name=self._user_name,
                          repo_name=repo,
                          search_path="releases",
                          set_per_page_limit=True,
                          iterate_per_page=True)

        _output = compile_by_page(self._api_session, url, _transform_function=release_transformer)

        return _output

    def extract_pull_requests(self, repo, **kwargs):

        add_other_option = kwargs.get('add_other_option', None)

        if add_other_option is None:
            other_option = "state=all"
        else:
            other_option = "state=all"+"&"+add_other_option

        url = url_builder(action_type="repos",
                          user_name=self._user_name,
                          repo_name=repo,
                          search_path="pulls",
                          set_per_page_limit=True,
                          iterate_per_page=True,
                          other_option=other_option)

        _output = compile_by_page(self._api_session, url, _transform_function=pull_request_transformer)

        return _output

    def url_builder_app(self, action_type, **kwargs):

        url = "https://api.github.com/{}/".format(action_type)

        _repo = kwargs.get('repo_name', None)
        _search_path = kwargs.get('search_path', None)
        _set_per_page_limit = kwargs.get('set_per_page_limit', False)
        _is_iterator_per_page = kwargs.get('iterate_per_page', False)
        _other_option = kwargs.get('other_option', False)

        if _repo is None:
            url = url + str(self._user_name) + "/{}".format(_search_path) + "?"
        else:
            url = url + str(self._user_name) + "/{}".format(_repo) + "/{}".format(_search_path) + "?"

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

    def compile_by_page_app(self, url):

        i = 1
        _stop = False
        _output_set = dict()

        tic = time.time()
        while _stop == False:

            r = self._api_session.get(url.format(i))

            if (not r.json()) or (r.ok == False):
                _stop = True
            else:
                _output_set[i] = r.json()
                i += 1

        print("the api scrapper did his job in {} seconds".format(time.time() - tic))

        return _output_set

    def get_url_response(self, url, **kwargs):

        _response_format = kwargs.get('response_format', "json")

        r = self._api_session.get(url)

        if r.ok:
            if _response_format == "json":
                _output = r.json()
            elif _response_format == "dataframe":
                _output = pd.DataFrame(r.json())
            else:
                print("wrong input format, the response must be 'json' or 'dataframe'")
        else:
            _output = "< WRONG URL >"
            print("the url input is not reachable")

        return _output
