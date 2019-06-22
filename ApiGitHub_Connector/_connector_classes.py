from ApiGitHub_Connector._connector_functions import *



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

    def extract_contributors_stats(self, repo):
        url = url_builder(action_type="repos", user_name=self._user_name, repo_name=repo,
                            search_path="contributors", set_per_page_limit=True, iterate_per_page=True, other_option="anon=1")
        print(url)

        _output = compile_by_page(self._api_session, url, _transform_function=contributors_commits_transformer)

        return _output

    def count_number_files(self, repo):

        num_files = 0
        num_files = compute_files(self._api_session, self._user_name, repo, None, num_files)

        return num_files

    def extract_branches(self, repo):
        url = url_builder(action_type="repos", user_name=self._user_name, repo_name=repo,
                            search_path="branches")
        r = self._api_session.get(url)
        data = pd.DataFrame(r.json())
        data = data[["name", "protected"]]

        return data

    def extract_releases(self, repo):
        url = url_builder(action_type="repos", user_name=self._user_name, repo_name=repo,
                            search_path="releases", set_per_page_limit=True, iterate_per_page=True)

        _output = compile_by_page(self._api_session, url, _transform_function=release_transformer)

        return _output

    def extract_pull_requests(self, repo):

        url = url_builder(action_type="repos", user_name=self._user_name, repo_name=repo,
                          search_path="pulls", set_per_page_limit=True, iterate_per_page=True,other_option="state=all")

        _output = compile_by_page(self._api_session, url, _transform_function=pull_request_transformer)

        return _output
