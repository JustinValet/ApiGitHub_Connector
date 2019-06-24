from ApiGitHub_Connector._connector_functions import *
import time
import pandas as pd

class connect_to_GitHub_API:

    """
     A class used to interact with the
     GitHub REST API v3 and compute advanced
     and basic statistics

     ...

     Attributes
     ----------
    user : str
       username of your GitHub account
    pwd : str
          password of your GitHub account
    _api_session: object
         the requests.session object to make GET
         to the GitHub REST API v3

     """

    def __init__(self, user, pwd):

        """
               Parameters
               ----------
               user : str
                   username of your GitHub account
               pwd : str
                   password of your GitHub account

               """

        self.user = user
        self.pwd = pwd
        self._api_session = create_session(self.user,
                                           self.pwd)

class GitHub_API_Connector(connect_to_GitHub_API):

    """
     A class used to interact with the
     GitHub REST API v3 and compute advanced
     and basic statistics

     ...

     Attributes
     ----------
     _user_name : str
         the name of the GitHub project
    _api_session: object
         the requests.session object to make GET
         to the GitHub REST API v3
     _user_stats : DataFrame
         statistics of each repository of a project
     _repos_names : list
         list of repositories names associated to a project

     Methods
     -------
     extract_contributors_stats()
         compute contributions of each contributors for a repository

     count_number_files()
         compute the number of files for a repository

     count_number_files()
         compute the number of files for a repository

     extract_branches()
         extract information about each branch of a repository

    extract_releases()
         extract information about each release of a repository

    extract_pull_requests()
         extract information about each pull request of a repository

    url_builder_app()
         method to build an url for interacting with the GitHub REST API v3

    compile_by_page_app()
         compute url answer for each page

    get_url_response()
         extract data from by calling the GitHub REST API v3

     """

    def __init__(self, user, pwd, user_name):

        """
              Parameters
              ----------
              user : str
                  username of your GitHub account
              pwd : str
                  password of your GitHub account
              user_name : str
                  name of the targeted GitHub project
              """


        self._user_name = user_name
        connect_to_GitHub_API.__init__(self, user, pwd)
        self._user_stats = compile_repos_stats(self._api_session,
                                               self._user_name)
        self._repos_names = list(self._user_stats["name"])
        self._user_stats = update_stats(self._api_session,
                                        self._user_stats,
                                        self._repos_names,
                                        self._user_name)

    def extract_contributors_stats(self, repo, **kwargs):

        """compute contributions of each contributors for each repository

        Requiered parameters
        ----------
        repo : str
            name of the targeted repository

        Optional parameters
        ----------
        add_other_option : str
            arguments that can be added to the url

        Returns
        -------
        _output : dataframe
            contribution of each contributors structured in a
            pandas DataFrame
        """

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

        _output = compile_by_page(self._api_session,
                                  url,
                                  _transform_function=contributors_commits_transformer)

        return _output

    def count_number_files(self, repo):

        """compute the total number of files of a repository

        Requiered parameters
        ----------
        repo : str
            name of the targeted repository

        Returns
        -------
        num_files : int
            total number of files into a repository
        """

        num_files = 0
        num_files = compute_files(self._api_session,
                                  self._user_name,
                                  repo,
                                  None,
                                  num_files)

        return num_files

    def extract_branches(self, repo):

        """extract information about each branch of a repository

        Requiered parameters
        ----------
        repo : str
            name of the targeted repository

        Returns
        -------
        data : dataframe
            information about branches of a repository
        """

        url = url_builder(action_type="repos",
                          user_name=self._user_name,
                          repo_name=repo,
                        search_path="branches")

        r = self._api_session.get(url)
        data = pd.DataFrame(r.json())
        data = data[["name", "protected"]]

        return data

    def extract_releases(self, repo):

        """extract information about each releases of a repository

        Requiered parameters
        ----------
        repo : str
            name of the targeted repository

        Returns
        -------
        _output : dataframe
            information about releases of a repository
        """

        url = url_builder(action_type="repos",
                          user_name=self._user_name,
                          repo_name=repo,
                          search_path="releases",
                          set_per_page_limit=True,
                          iterate_per_page=True)

        _output = compile_by_page(self._api_session, url,
                                  _transform_function=release_transformer)

        return _output

    def extract_pull_requests(self, repo, **kwargs):

        """extract information about pull requests of a repository

        Requiered parameters
        ----------
        repo : str
            name of the targeted repository

        Optional parameters
        ----------
        add_other_option : str
            arguments that can be added to the url

        Returns
        -------
        _output : dataframe
            information about pull requests of a repository
        """

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

        _output = compile_by_page(self._api_session,
                                  url,
                                  _transform_function=pull_request_transformer)

        return _output

    def url_builder_app(self, action_type, **kwargs):

        """method to build an url for interacting
           with the GitHub REST API v3

        Requiered parameters
        ----------
        action_type : str
            detailed representation (see the API docs)
            ex: repos, user, etc...

        Optional parameters
        ----------
        repo_name : str
            name of the targeted repository
        search_path : str
            name of path for research
            ex: issues, repos, repos/commits, ...
        set_per_page_limit : boolean (default False)
            if True --> for each page, 100 elements are extracted
        iterate_per_page : boolean (default False)
            if True, page={} is added to the url in order
            extract information for a specific page
        _other_option : str
            user manual other option to be added to the url
            ex: since>X, state=all, etc...

        Returns
        -------
        url : str
            build url from input paramaters
        """

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

        """ compute url answer for each page

        Requiered parameters
        ----------
        url : str
            url for interacting with the API

        Returns
        -------
        _output_set : dict
            dict that stores json of each page answer
        """

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

        """ extract data from by calling the GitHub REST API v3

        Requiered parameters
        ----------
        url : str
            url for interacting with the API

        Optional parameters
        ----------
        response_format : str
            choose the format of the output ('json' or 'dataframe')
        search_path : str

        Returns
        -------
        _output : 'json' or 'dataframe'
            answer of a call to the API
        """

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
