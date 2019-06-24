# ApiGitHub_Connector

This python package helps connecting to [GitHub REST API v3](https://developer.github.com/v3/) and extracting data from github **public** projects and their associated repositories.

## Getting Started

The followings instructions help installing and use the python package ApiGitHub_Connector.

### Prerequisites

* A python 3.6 installed on your machine is requiered.
* It is recommended to have a [GitHub account](https://github.com) to better use the API.  

### Installing

It is recommended to install the package within a created 3.6 python environment (using virtual env or anaconda)

* the package can be directly installed from GitHub using:

```
pip install git+https://github.com/JustinValet/ApiGitHub_Connector.git
```

## Example by usage

In this example, the ApiGitHub_Connector will extract some statistics from the famous [Pandas project](https://github.com/pandas-dev) on GitHub.

* Connection to the Pandas project using GitHub REST API v3

```
# import the package
from ApiGitHub_Connector._connector_classes import GitHub_API_Connector

user = "****" # your github user name account
pwd = "****"  # you githut password 
project_name = "pandas-dev" # the name of the targeted project that must be scrapped

# create the GitHub connection object using your credentials and 
# the name of the targeted project
git_hub_connection = GitHub_API_Connector(user=user, pwd=pwd, user_name=project_name)


>>> the api scrapper did his job in 0.4506540298461914 seconds
```

* Get basic statistics from repositories of the Pandas project

```
# the ApiGitHub_Connector automatically extracts
# some statistics about each repository stored 
# into the property _user_stats associated to GitHub_API_Connector

stats_repos = git_hub_connection._user_stats # this is a pandas DataFrame (get more infos)
print(stats_repos)

>>>              created_at default_branch  ... total_issues  total_pull_requests
0  2010-08-24T01:37:33Z         master  ...        15169                11704
1  2019-01-04T20:34:38Z         master  ...            0                    1
2  2018-02-14T11:44:59Z         master  ...            1                    5
3  2017-06-10T14:31:39Z         master  ...            0                    0
4  2016-01-07T01:24:58Z         master  ...            0                   10
5  2018-05-15T17:55:01Z         master  ...            5                    3
6  2018-04-19T15:37:27Z         master  ...            0                    3
7  2012-01-23T22:55:12Z         master  ...           34                   38
8  2016-08-23T18:31:28Z         master  ...           62                   15
9  2017-06-08T14:36:56Z         master  ...            0                    0
[10 rows x 17 columns]

```

* Plot the number of stars per repository

```
import pandas as pd

stats_repos.plot.bar(x="name",y="stargazers_count",
                     title="Number of stars per repository",
                     legend=False,
                     fontsize=5,
                     sort_columns=True)

```

<p align="center">
  <img src="https://github.com/JustinValet/ApiGitHub_Connector/blob/master/doc/Figure_1.png" width="350">
</p>


* Use a method for extracting the number of files of the pandas repository

```
# This method extract recursively the number of files 
# in each sub-directory of the pandas repository
print(git_hub_connection.count_number_files(repo="pandas"))

>>> 1561

```

## Documentation 
*comming soon*

## Authors

* **Justin Valet** - *Data Scientist* 

