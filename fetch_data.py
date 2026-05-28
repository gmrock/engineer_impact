import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "PostHog/posthog"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28" 
}

if GITHUB_TOKEN:
    # Clean up any accidental leading/trailing quotes or whitespace from terminal exports
    token_clean = GITHUB_TOKEN.strip().strip('\"').strip("'")
    HEADERS["Authorization"] = f"Bearer {token_clean}"
else:
    print("⚠️ WARNING: GITHUB_TOKEN environment variable not found.")
    print("Using unauthenticated requests. GitHub will rate-limit this instantly.")

engineers = {}

def get_or_init(user):
    if not user or user.endswith("[bot]"): 
        return None
    if user not in engineers:
        engineers[user] = {
            "prs_merged": 0, 
            "bug_fixes": 0, 
            "reverts_triggered": 0,
            "review_actions": 0, 
            "review_words_written": 0, 
            "multiplier_impact": 0
        }
    return engineers[user]

print("🏁 Extracting Advanced Impact Metrics matched to PostHog Topology...")
cutoff_date = datetime.now() - timedelta(days=90)

# -------------------------------------------------------------
# Phase 1: Scan PR Stream (Execution, Complexity, Reverts)
# -------------------------------------------------------------
print("\n📦 Phase 1: Fetching recent Pull Requests...")
pr_url = f"https://api.github.com/repos/{REPO}/pulls"
phase_1_success = False

for page in range(1, 11):
    params = {
        "state": "closed", 
        "sort": "updated", 
        "direction": "desc", 
        "per_page": 100, 
        "page": page
    }
    res = requests.get(pr_url, headers=HEADERS, params=params)
    
    if res.status_code != 200:
        print(f"❌ Phase 1 Error on page {page}: API returned {res.status_code} - {res.json().get('message')}")
        break
        
    prs = res.json()
    if not prs: 
        break
    phase_1_success = True
    
    for pr in prs:
        if not pr.get("merged_at"): 
            continue
            
        merged_at = datetime.strptime(pr["merged_at"], "%Y-%m-%dT%H:%M:%SZ")
        if merged_at < cutoff_date: 
            continue
        
        author = pr["user"]["login"]
        eng = get_or_init(author)
        if not eng: 
            continue
        
        # Track raw baseline engineering velocity
        eng["prs_merged"] += 1
        
        # Extract textual fields for heuristics matching
        title = pr.get("title", "").lower()
        
        # Metric: System Quality (Avoidable Revert Tracking)
        if "revert" in title:
            eng["reverts_triggered"] += 1
 

        # Extract native labels payload once for all downstream metric evaluations
        labels = [l["name"].lower() for l in pr.get("labels", [])]

        # Condition A: Structural Complexity Multiplier (Title Analysis)
        if any(x in title for x in ["lib", "core", "infra", "architecture", "critical"]):
            eng["multiplier_impact"] += 1
            
        # Condition B: High Severity Multiplier (Native Priority Label Analysis)
        # Adds an extra point if the PR is explicitly flagged as a P0 or P1 incident/initiative
        if any(p in labels for p in ["p0", "p1"]):
            eng["multiplier_impact"] += 1

        # Metric: Native Bug Tracking
        if "bug" in labels or any("bug" in label_name for label_name in labels):
            eng["bug_fixes"] += 1

# -------------------------------------------------------------
# Phase 2: Scan Review Comments Stream (Citizenship & Depth)
# -------------------------------------------------------------
print("\n💬 Phase 2: Fetching repository-wide review comments...")
comments_url = f"https://api.github.com/repos/{REPO}/pulls/comments"
phase_2_success = False

for page in range(1, 11):
    params = {
        "sort": "created", 
        "direction": "desc", 
        "per_page": 100, 
        "page": page
    }
    res = requests.get(comments_url, headers=HEADERS, params=params)
    
    if res.status_code != 200:
        print(f"❌ Phase 2 Error on page {page}: API returned {res.status_code} - {res.json().get('message')}")
        break
        
    comments = res.json()
    if not comments: 
        break
    phase_2_success = True
    
    for comment in comments:
        created_at = datetime.strptime(comment["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        if created_at < cutoff_date:
            continue
            
        reviewer = comment["user"]["login"]
        eng = get_or_init(reviewer)
        if not eng: 
            continue
        
        # Track raw volume of code review interaction
        eng["review_actions"] += 1
        
        # Metric: Meaningful Review Depth (Filters out superficial "LGTM" comments)
        body = comment.get("body", "")
        word_count = len(body.split())
        if word_count > 15:  
            eng["review_words_written"] += word_count

# -------------------------------------------------------------
# Phase 3: Defensive Data Processing and Export
# -------------------------------------------------------------
print("\n📊 Phase 3: Processing and Exporting Data...")
if engineers and (phase_1_success or phase_2_success):
    df = pd.DataFrame.from_dict(engineers, orient='index').reset_index().rename(columns={'index': 'engineer'})
    
    # Defensive Schema Guard: Force-initialize expected columns to protect against downstream KeyErrors
    expected_cols = ["prs_merged", "review_actions", "bug_fixes", "reverts_triggered", "multiplier_impact", "review_words_written"]
    for expected_col in expected_cols:
        if expected_col not in df.columns:
            df[expected_col] = 0
        df[expected_col] = df[expected_col].fillna(0)
            
    # Prune inactive records to keep dataset compact
    df = df[(df['prs_merged'] > 0) | (df['review_actions'] > 0)]
    
    if not df.empty:
        df.to_csv("posthog_impact_data.csv", index=False)
        print("🚀 Advanced metrics pipeline successfully saved to posthog_impact_data.csv")
    else:
        print("⚠️ DataFrame filtered down to 0 rows. No matching active engineers found in this window.")
else:
    print("❌ Critical Error: No data payload compiled. Please check the API error codes printed above.")
