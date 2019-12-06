import random
import time

from github import Github

"""
https://api.github.com/search/repositories?q=apache+language:java&sort=stars&order=desc&type=Repositories&page=1&per_page=100

https://github.com/search?l=java&p=5&q=stars%3A%3E1000&type=Repositories

https://help.github.com/en/articles/searching-for-repositories#search-based-on-whether-a-repository-is-archived

https://developer.github.com/v3/search/#constructing-a-search-query

# def parse_apache():
#     repositories = g.search_repositories(
#         query='apache', sort='stars',
#         **{'language': 'java', "stars": ":>=1000", "archived": "false", "user": "apache", "fork": "false"})
#     List = []
#     for repo in repositories:
#         List.append(repo)
#         print(len(List), repo.clone_url)
#     with open("apache_repos.txt", "w") as fw:
#         for repo in List:
#             url = repo.clone_url.replace(".git", "")
#             fw.write(url)
#             fw.write("\n")
"""

tokens = ""


class ProjectList:

    def __init__(self):
        self.project_list_file = "java_list_11000.csv"
        self.github = Github(tokens)
        self.repo_list = []
        self.min_stars = 2500
        self.max_stars = 10000000
        self.index = 0

    def search(self):
        repositories = self.github.search_repositories(
            query='',
            sort="stars",
            order="desc",
            **{
                'language': 'java',
                "stars": str(self.min_stars) + ".." + str(self.max_stars),
                "archived": "false",
                # "license": "apache-2.0",
                "fork": "false",
            }
        )
        return repositories

    def get_1000_repos(self):
        """
        **{'language': 'java', "stars": ">=1500", "archived": "false", "license": "apache-2.0", "fork": "false"})
        """
        # repositories = self.github.search_repositories(
        #     query='NOT example NOT android NOT Android', sort='stars',
        #     **{'language': 'java', "stars": "10.." + str(self.max_stars), "archived": "false",
        #     "license": "apache-2.0", "fork": "false"})
        repositories = self.search()
        print(repositories.totalCount)
        # assert repositories.totalCount < 900
        for repo in repositories:
            time.sleep(0.05 + random.random() / 10)
            if repo not in self.repo_list:
                self.repo_list.append(repo)
                self.index += 1
                print(self.index, repo, repo.stargazers_count)
                if repo.stargazers_count < self.max_stars:
                    self.max_stars = repo.stargazers_count

    def save_repo_list(self):
        for i in range(1000):
            print("step %d" % (i + 1))
            self.get_1000_repos()
            self.min_stars = min(self.max_stars, self.min_stars)
            self.max_stars = self.max_stars + 1
            if self.min_stars // 100 >= 1:
                self.min_stars -= self.min_stars // 50
            elif self.min_stars // 50 >= 1:
                self.min_stars -= 1
                self.max_stars -= 1
            else:
                self.min_stars -= 1
                self.max_stars -= 2
            if self.min_stars < 30 or len(self.repo_list) >= 30000:
                break
            print()
            time.sleep(10 + random.random() * 5)

        self.project_list_file = "repos_" + str(len(self.repo_list)) + ".csv"
        with open(self.project_list_file, "w") as fw:
            # template = '{},{},{},{},{}\n'
            # fw.write(template.format("index", "repo", "stars", "size", "url"))
            template = '{},{},{},{},{} ,{}\n'
            fw.write(template.format("repo", "full_name", "stars", "size", "url", "description"))
            index = 0
            self.repo_list.sort(key=lambda github_repo: github_repo.stargazers_count, reverse=True)
            for repo in self.repo_list:
                index += 1
                repo_name = repo.name
                repo_full_name = repo.full_name
                repo_star = repo.stargazers_count
                repo_size = repo.size
                repo_url = repo.html_url
                repo_description = repo.description
                if repo_description is not None:
                    repo_description = repo_description.replace(",", "|")
                    repo_description = repo_description.replace("\n", "  ").replace("\r", "  ")
                # owner_user = repo.owner.login
                # forks = repo.forks_count
                # line_str = template.format(index, repo_name, repo_star, repo_size, repo_url)
                line_str = template.format(repo_name, repo_full_name, repo_star, repo_size, repo_url, repo_description)
                fw.write(line_str)
                # print(line_str.strip())


if __name__ == "__main__":
    projects = ProjectList()
    projects.save_repo_list()
