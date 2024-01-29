import requests
import os
import json
from datetime import datetime

# 環境変数からGitHub Personal Access Tokenとユーザー名を取得
token = os.getenv('GITHUB_TOKEN')
username = os.getenv('GITHUB_USERNAME')

# 環境変数が設定されていない場合のエラーチェック
if not token or not username:
    raise ValueError("GitHub token and username must be set as environment variables.")

# GitHub APIのヘッダー設定
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
}

def fetch_and_save_merged_prs(user, target_dir, start_date, end_date):
    page = 1

    while True:
        print(f"Processing page {page}...")

        output_file = f'{target_dir}/merged_prs_data_page_{page}.json'
        if os.path.exists(output_file):
            print(f"Skipping page {page}, file already exists.")
            page += 1
            continue

        url = (f'https://api.github.com/search/issues?q=is:pr+author:{user}+is:merged+created:{start_date}..{end_date}'
               f'&type=Issues&page={page}')
        response = requests.get(url, headers=headers)
        data = response.json()
        prs = data['items']

        if not prs:
            break

        with open(output_file, 'w') as file:
            json.dump(prs, file, indent=4)

        page += 1

# 日付範囲の設定
start_date = '2023-07-01'
end_date = '2023-12-31'
target_dir = f'data/{username}'
# ディレクトリが存在しない場合にのみ作成
if not os.path.exists(target_dir):
    os.mkdir(target_dir)

# マージされたPRの情報を取得し、ファイルに保存
fetch_and_save_merged_prs(username, target_dir, start_date, end_date)

# PRをカウント
def count_prs_by_repo(file_paths):
    repo_pr_count = {}

    for file_path in file_paths:
        with open(file_path, 'r') as file:
            prs = json.load(file)
            for pr in prs:
                repo_name = pr['repository_url'].split('/')[-1]
                repo_pr_count[repo_name] = repo_pr_count.get(repo_name, 0) + 1

    return repo_pr_count

# 'data/' ディレクトリ内のJSONファイルを取得
cache_files = [f'{target_dir}/{f}' for f in os.listdir(target_dir) if f.startswith('merged_prs_data_page_')]

# リポジトリごとのPR数をカウント
pr_count_by_repo = count_prs_by_repo(cache_files)

# 結果の表示
print(f'{pr_count_by_repo}')

for repo, count in pr_count_by_repo.items():
    print(f'{repo} {count}')

print(f'{username} Total Merged PRs: {sum(pr_count_by_repo.values())}')
