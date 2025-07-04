import requests
import os
import json
import click
from datetime import datetime

def fetch_and_cache_commented_prs(headers, username, target_dir, start_date, end_date):
    page = 1
    while True:
        cache_file = f'{target_dir}/commented_prs_page_{page}.json'

        if os.path.exists(cache_file):
            print(f"Skipping page {page}, cache file already exists.")
            page += 1
            continue

        print(f"Fetching page {page}...")
        url = (f'https://api.github.com/search/issues?q=is:pr+is:merged+commenter:{username}+-author:{username}+created:{start_date}..{end_date}' 
               f'&type=Issues&page={page}')
        response = requests.get(url, headers=headers)
        data = response.json()
        if 'items' in data:
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


def create_pr_list(target_dir, file_paths):
    print('Creating PR list...')
    pr_list = {}
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            prs = json.load(file)
            for pr in prs:
                repo_name = pr['repository_url'].split('/')[-1]
                pr_list[repo_name] = pr_list.get(repo_name,[]) + [{'title': pr['title'], 'url': pr['html_url']}]

    buffer = ''
    for repo, prs in pr_list.items():
        buffer += f'## {repo}\n'
        for pr in prs:
            buffer += f'- [{pr["title"]}]({pr["url"]})\n'

    # save buffer to file
    with open(f'{target_dir}/reviewed_pr_list.md', 'w') as file:
        file.write(buffer)

@click.command()
@click.option('-u', '--user_name', required=True, help='Start date in YYYY-MM-DD format')
@click.option('-s', '--start_date', required=True, help='Start date in YYYY-MM-DD format')
@click.option('-e', '--end_date', required=True, help='End date in YYYY-MM-DD format')
def main(user_name, start_date, end_date):
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise ValueError("GitHub token and must be set as environment variables.")

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }


    target_dir = f'data/{user_name}'

    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    fetch_and_cache_commented_prs(headers, user_name, target_dir, start_date, end_date)

    cache_files = [f'{target_dir}/{f}' for f in os.listdir(target_dir) if f.startswith('commented_prs_page_')]

    create_pr_list(target_dir, cache_files)

    your_comments_count_by_repo = count_prs_by_repo(cache_files)
    print(f'{your_comments_count_by_repo}')

    for repo, count in your_comments_count_by_repo.items():
        print(f'{repo} {count}')

    print(f'{user_name} Total PR Reviews: {sum(your_comments_count_by_repo.values())}')



if __name__ == '__main__':
    main()