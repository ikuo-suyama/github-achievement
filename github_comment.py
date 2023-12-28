import requests
import os
import json
from datetime import datetime

# 環境変数からGitHub Personal Access Tokenを取得
token = os.getenv('GITHUB_TOKEN')
your_username = os.getenv('GITHUB_USERNAME')  # あなたのGitHubユーザー名

# GitHub APIのヘッダー設定
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
}

def fetch_and_cache_commented_prs(username, start_date, end_date):
    page = 1
    while True:
        cache_file = f'data/commented_prs_page_{page}.json'

        # キャッシュが既に存在する場合はスキップ
        if os.path.exists(cache_file):
            print(f"Skipping page {page}, cache file already exists.")
            page += 1
            continue

        print(f"Fetching page {page}...")
        url = (f'https://api.github.com/search/issues?q=is:pr+is:merged+commenter:{username}+-author:{username}+created:{start_date}..{end_date}' 
               f'&type=Issues&page={page}')
        response = requests.get(url, headers=headers)
        data = response.json()
        print(data)
        prs = data['items']

        if not prs:
            break

        with open(cache_file, 'w') as file:
            json.dump(prs, file, indent=4)

        page += 1

def count_prs_by_repo(file_paths):
    repo_pr_count = {}

    for file_path in file_paths:
        with open(file_path, 'r') as file:
            prs = json.load(file)
            for pr in prs:
                repo_name = pr['repository_url'].split('/')[-1]
                repo_pr_count[repo_name] = repo_pr_count.get(repo_name, 0) + 1

    return repo_pr_count


# 日付範囲の設定
start_date = '2023-07-01'
end_date = datetime.now().strftime('%Y-%m-%d')

# APIからデータを取得してキャッシュに保存
fetch_and_cache_commented_prs(your_username, start_date, end_date)

# キャッシュされたデータからコメントをカウント
cache_files = [f'data/{f}' for f in os.listdir('data/') if f.startswith('commented_prs_page_')]

your_comments_count_by_repo = count_prs_by_repo(cache_files)
print(f'{your_comments_count_by_repo}')

for repo, count in your_comments_count_by_repo.items():
    print(f'{repo} {count}')
