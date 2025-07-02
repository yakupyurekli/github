import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Ayarlar
TOPIC = "machine-learning"
MIN_STARS = 100
REPO_LIMIT = 10
GITHUB_API_URL = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}


def load_previous_repos():
    if not os.path.exists("repos.json"):
        return []
    with open("repos.json", "r") as f:
        return json.load(f)


def save_repos(repos):
    with open("repos.json", "w") as f:
        json.dump(repos, f, indent=2)


def fetch_repos():
    query = f"topic:{TOPIC} stars:>={MIN_STARS} sort:stars"
    url = f"{GITHUB_API_URL}/search/repositories?q={query}&per_page={REPO_LIMIT}"

    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print("❌ GitHub API isteği başarısız:", response.status_code)
        return []

    data = response.json()
    return data.get("items", [])


def update_readme(repos):
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(f"# 🔍 Top {TOPIC.capitalize()} Repositories\n\n")
        f.write(f"_Güncelleme tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n")
        for repo in repos:
            line = f"- [{repo['full_name']}]({repo['html_url']}) 🌟 {repo['stargazers_count']}\n"
            f.write(line)


def main():
    print("🚀 Repos taranıyor...")
    new_repos = fetch_repos()
    if not new_repos:
        print("Yeni repo bulunamadı.")
        return

    previous_repos = load_previous_repos()
    new_unique_repos = []

    for repo in new_repos:
        if repo["id"] not in [r["id"] for r in previous_repos]:
            new_unique_repos.append(repo)

    all_repos = previous_repos + new_unique_repos
    all_repos = sorted(all_repos, key=lambda x: x["stargazers_count"], reverse=True)[:REPO_LIMIT]

    if new_unique_repos:
        save_repos(all_repos)
        update_readme(all_repos)
        print(f"✅ {len(new_unique_repos)} yeni repo eklendi ve README güncellendi.")
    else:
        print("🔄 Yeni repo yok, README değişmedi.")


if __name__ == "__main__":
    main()
