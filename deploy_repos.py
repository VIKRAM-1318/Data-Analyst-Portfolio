"""
Automated GitHub Repository Creator & Multi-Project Deployment Script
Author: R Vikram (VIKRAM-1318)
Purpose: 
  1. Creates 7 repositories on GitHub (1 Master Portfolio + 6 Individual Projects)
  2. Pushes the Master Portfolio repository
  3. Deploys and pushes each of the 6 analytics projects individually to its own GitHub repository
"""

import os
import sys
import json
import shutil
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

# Mapping of Local Project Folder -> Remote GitHub Repository Name & Description
PROJECTS = [
    {
        "local_folder": "Blinkit Grocery Analytics",
        "repo_name": "Blinkit-Grocery-Analytics",
        "description": "Blinkit Quick-Commerce Sales & Logistics Analytics — 4-Page Power BI Dashboard, Star Schema, SQL & Python ETL"
    },
    {
        "local_folder": "HR Analytics Dashboard",
        "repo_name": "HR-Analytics-Employee-Attrition",
        "description": "HR Analytics & Employee Attrition Intelligence — Turnover Risk Multipliers, Power BI, SQL & Python ETL"
    },
    {
        "local_folder": "Netflix Content Analytics",
        "repo_name": "Netflix-Content-Analytics",
        "description": "Netflix Content & Streaming Analytics — Catalog Composition, Star Schema Normalization, Power BI & SQL"
    },
    {
        "local_folder": "Olist_Cleaned",
        "repo_name": "Olist-Ecommerce-Marketplace",
        "description": "Olist Brazilian E-Commerce Marketplace Analytics — 8 Relational Tables, Logistics SLA, Power BI & SQL"
    },
    {
        "local_folder": "Customer Segmentation Analysis",
        "repo_name": "Customer-Segmentation-RFM-Analysis",
        "description": "Customer Segmentation & RFM Behavioral Engine — 805K Transactions, Python Quantile Pipeline & Power BI"
    },
    {
        "local_folder": "superstore_sales_dashboard",
        "repo_name": "Superstore-Sales-Analytics",
        "description": "Superstore Sales & Commercial Pricing Analytics — Profitability Bleed, Discount Elasticity & Power BI"
    }
]

MASTER_REPO = {
    "repo_name": "Data-Analyst-Portfolio",
    "description": "Data Analytics Engineering Portfolio — 6 End-to-End Projects in Power BI, SQL, Python & DAX by R Vikram"
}

GITHUB_USER = "VIKRAM-1318"


def get_token():
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return sys.argv[1].strip()
    env_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if env_token:
        return env_token.strip()
    return None


def create_github_repo(token, name, description):
    url = "https://api.github.com/user/repos"
    payload = json.dumps({
        "name": name,
        "description": description,
        "private": False,
        "has_issues": True,
        "has_projects": True,
        "has_wiki": False
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "Vikram-Portfolio-Deployer"
    })

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"  [CREATED] https://github.com/{GITHUB_USER}/{name}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 422 and "name already exists" in body.lower():
            print(f"  [EXISTS] https://github.com/{GITHUB_USER}/{name} already exists.")
            return True
        elif e.code == 401:
            print("  [ERROR 401] Invalid or expired GitHub Personal Access Token.")
            return False
        else:
            print(f"  [ERROR {e.code}] Failed to create {name}: {body}")
            return False


def run_cmd(cmd, cwd=None):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if res.returncode != 0 and res.stderr:
        print(f"    Command warning/error: {res.stderr.strip()[:200]}")
    return res


def deploy_master_repo(token, base_dir):
    print("\n" + "=" * 60)
    print("STEP 2: DEPLOYING MASTER PORTFOLIO REPOSITORY")
    print("=" * 60)
    remote_url = f"https://{token}@github.com/{GITHUB_USER}/{MASTER_REPO['repo_name']}.git"
    run_cmd(f'git remote set-url origin "{remote_url}"', cwd=base_dir)
    print(f"  Pushing master portfolio to https://github.com/{GITHUB_USER}/{MASTER_REPO['repo_name']}...")
    res = run_cmd("git push -u origin main --force", cwd=base_dir)
    if res.returncode == 0:
        print("  [SUCCESS] Master portfolio pushed successfully!")
    else:
        print(f"  [FAILED] {res.stderr.strip()}")


def deploy_individual_repos(token, base_dir):
    print("\n" + "=" * 60)
    print("STEP 3: DEPLOYING INDIVIDUAL PROJECT REPOSITORIES")
    print("=" * 60)

    temp_deploy_root = Path(os.environ.get("TEMP", "/tmp")) / "git_deploy_vikram"
    if temp_deploy_root.exists():
        shutil.rmtree(temp_deploy_root, ignore_errors=True)
    temp_deploy_root.mkdir(parents=True, exist_ok=True)

    for p in PROJECTS:
        local_src = base_dir / p["local_folder"]
        repo_name = p["repo_name"]
        print(f"\n--- Deploying {p['local_folder']} -> {repo_name} ---")

        if not local_src.exists():
            print(f"  [SKIP] Folder not found: {local_src}")
            continue

        target_dir = temp_deploy_root / repo_name
        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)

        # Copy project assets excluding __pycache__
        shutil.copytree(
            local_src,
            target_dir,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git")
        )

        # Initialize clean Git repo for the standalone project
        run_cmd("git init -b main", cwd=target_dir)
        run_cmd('git config user.name "R VIKRAM"', cwd=target_dir)
        run_cmd('git config user.email "rv367629@gmail.com"', cwd=target_dir)
        run_cmd("git add .", cwd=target_dir)
        folder_name = p['local_folder']
        run_cmd(f'git commit -m "feat: initial release of {folder_name}"', cwd=target_dir)

        remote_url = f"https://{token}@github.com/{GITHUB_USER}/{repo_name}.git"
        run_cmd(f'git remote add origin "{remote_url}"', cwd=target_dir)
        print(f"  Pushing to https://github.com/{GITHUB_USER}/{repo_name}...")
        res = run_cmd("git push -u origin main --force", cwd=target_dir)
        if res.returncode == 0:
            print(f"  [SUCCESS] {repo_name} deployed successfully!")
        else:
            print(f"  [FAILED] {repo_name}: {res.stderr.strip()[:200]}")

    print("\n[COMPLETE] All projects processed!")


def main():
    base_dir = Path(__file__).resolve().parent
    print("=" * 70)
    print("VIKRAM DATA ANALYTICS PORTFOLIO GITHUB DEPLOYER")
    print("=" * 70)

    token = get_token()
    if not token:
        print("\n[ERROR] No GitHub Personal Access Token (PAT) provided.")
        print("Usage:")
        print("  python deploy_repos.py <YOUR_GITHUB_TOKEN>")
        print("\nHow to get your token:")
        print("  1. Visit: https://github.com/settings/tokens")
        print("  2. Click 'Generate new token (classic)'")
        print("  3. Check the 'repo' scope (Full control of private repositories & public repositories)")
        print("  4. Copy the token (starts with ghp_...) and run this script.")
        sys.exit(1)

    print("\nSTEP 1: CREATING GITHUB REPOSITORIES VIA API...")
    # 1. Create master repo
    create_github_repo(token, MASTER_REPO["repo_name"], MASTER_REPO["description"])
    # 2. Create individual repos
    for p in PROJECTS:
        create_github_repo(token, p["repo_name"], p["description"])

    # 3. Deploy master repo
    deploy_master_repo(token, base_dir)

    # 4. Deploy each individual repo
    deploy_individual_repos(token, base_dir)

    # Clean up token from local git config
    master_name = MASTER_REPO['repo_name']
    run_cmd(f'git remote set-url origin "https://github.com/{GITHUB_USER}/{master_name}.git"', cwd=base_dir)
    print(f"\n[DONE] All repositories live on https://github.com/{GITHUB_USER}")


if __name__ == "__main__":
    main()
