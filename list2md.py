from datetime import datetime
import json
import requests
import sys


head = '''# Top Homepage
A list of popular projects related tohomepage, homelab, self-hosted, startpage, single-page(ranked by stars automatically)
Please update **list.txt** (via Pull Request)

Tips：这是一份关于 homepage, homelab, self-hosted, startpage, single-page 的导航页名单，每天 UTC 时间上午 9 点自动更新 github 状态，如果有新的导航页，可以 issues 或者 pr “list.txt” 文件给我。

source of inspiration：[jnmcfly/awesome-startpage](https://github.com/jnmcfly/awesome-startpage) and [Reddit startpages](https://www.reddit.com/r/startpages/)

| Project Name | Stars | Forks | Open Issues | Description | Last Commit |
| ------------ | ----- | ----- | ----------- | ----------- | ----------- |
'''
tail = '\n*Last Automatic Update: {}*'

warning = "⚠️ No longer maintained ⚠️  "

deprecated_repos = list()
repos = list()


def main():
    access_token = get_access_token()

    with open('list.txt', 'r') as f:
        for url in f.readlines():
            url = url.strip()
            if url.startswith('https://github.com/'):
                repo_api = 'https://api.github.com/repos/{}'.format(url[19:])
                print(repo_api)

                r = requests.get(repo_api, headers={'Authorization': 'token {}'.format(access_token)})
                if r.status_code != 200:
                    raise ValueError('Can not retrieve from {}'.format(url))
                repo = json.loads(r.content)

                commit_api = 'https://api.github.com/repos/{}/commits/{}'.format(url[19:], repo['default_branch'])
                # print(repo_api)

                r = requests.get(commit_api, headers={'Authorization': 'token {}'.format(access_token)})
                if r.status_code != 200:
                    raise ValueError('Can not retrieve from {}'.format(url))
                commit = json.loads(r.content)

                repo['last_commit_date'] = commit['commit']['committer']['date']
                # print(repo['stargazers_count'])
                # print(type(repo))
                repos.append(repo)
            # elif "github" not in url:
            #     repo['name'] = url
            #     print(url)
            #     repos.append(repo)
            else:
                url=url.split(",")
                # print("not in github", url)
                # print("not in github", url[1])
                data={'name': '{}'.format(url[1]),'url': '{}'.format(url[0]), 'html_url': '{}'.format(url[0]),'stargazers_count': 0, 'forks_count': 0, 'open_issues_count': 0, 'description': '{}'.format(url[2]), 'last_commit_date': '2006-01-02T03:04:05Z'}
                # 'stargazers_count': 0, 'forks_count': 0, 'open_issues_count': 0, 'description': '',
                # print(type(data))
                # repo=json.loads(data)
                # print(data['stargazers_count'])
                repos.append(data)
        repos.sort(key=lambda r: r['stargazers_count'], reverse=True)
        save_ranking(repos)
   

def get_access_token():
    if len(sys.argv) > 1 and sys.argv[1] != None:
        return sys.argv[1].strip()
    else:
        with open('access_token.txt', 'r') as f:
            return f.read().strip()


def save_ranking(repos):
    with open('README.md', 'w') as f:
        f.write(head)
        for repo in repos:
            # print(repo)
            if is_deprecated(repo['url']):
                repo['description'] = warning + repo['description']
            f.write('| [{}]({}) | {} | {} | {} | {} | {} |\n'.format(repo['name'],
                                                                     repo['html_url'],
                                                                     repo['stargazers_count'],
                                                                     repo['forks_count'],
                                                                     repo['open_issues_count'],
                                                                     repo['description'],
                                                                     datetime.strptime(repo['last_commit_date'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')))
        f.write(tail.format(datetime.now().strftime('%Y-%m-%dT%H:%M:%S%Z')))


def is_deprecated(repo_url):
    return repo_url in deprecated_repos


if __name__ == '__main__':
    main()