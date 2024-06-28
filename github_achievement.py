import requests
import os
import json
import click
from datetime import datetime

def fetch_and_save_merged_prs(headers, user, target_dir, start_date, end_date):
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
    with open(f'{target_dir}/merged_pr_list.md', 'w') as file:
        file.write(buffer)


def count_prs_by_repo(file_paths):
    repo_pr_count = {}

    for file_path in file_paths:
        with open(file_path, 'r') as file:
            prs = json.load(file)
            for pr in prs:
                repo_name = pr['repository_url'].split('/')[-1]
                repo_pr_count[repo_name] = repo_pr_count.get(repo_name, 0) + 1

    return repo_pr_count

@click.command()
@click.option('-u', '--user_name', required=True, help='Start date in YYYY-MM-DD format')
@click.option('-s', '--start_date', required=True, help='Start date in YYYY-MM-DD format')
@click.option('-e', '--end_date', required=True, help='End date in YYYY-MM-DD format')
def main(user_name, start_date, end_date):
    # Prepare global value
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise ValueError("GitHub token and must be set as environment variables.")

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }

    print('f {username}: {start_date} {end_date}')
    target_dir = f'data/{user_name}'
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    fetch_and_save_merged_prs(headers, user_name, target_dir, start_date, end_date)

    cache_files = [f'{target_dir}/{f}' for f in os.listdir(target_dir) if f.startswith('merged_prs_data_page_')]

    create_pr_list(target_dir, cache_files)

    pr_count_by_repo = count_prs_by_repo(cache_files)

    print(f'{pr_count_by_repo}')

    for repo, count in pr_count_by_repo.items():
        print(f'{repo} {count}')

    print(f'{user_name} Total Merged PRs: {sum(pr_count_by_repo.values())}')


if __name__ == '__main__':
    main()