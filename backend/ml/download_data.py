"""
Download historical match data from football-data.co.uk

CSV URL pattern: https://www.football-data.co.uk/mmz4281/{season}/{league_code}.csv
Example: https://www.football-data.co.uk/mmz4281/2425/E0.csv  (Premier League 2024-25)
"""

import os
import sys
import time
import requests
from pathlib import Path

# Add parent directory so we can import from api/
sys.path.insert(0, str(Path(__file__).parent.parent))
from api.leagues import get_leagues_with_csv, DOWNLOAD_SEASONS

BASE_URL = "https://www.football-data.co.uk/mmz4281"
RAW_DIR = Path(__file__).parent.parent / "data" / "raw"


def download_csv(league_slug: str, csv_code: str, season: str) -> bool:
    """Download a single CSV file from football-data.co.uk"""
    url = f"{BASE_URL}/{season}/{csv_code}.csv"
    filename = f"{league_slug}_{season}.csv"
    filepath = RAW_DIR / filename

    if filepath.exists():
        print(f"  [SKIP] {filename} already exists")
        return True

    try:
        print(f"  [GET]  {url}")
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            content = response.text
            # Verify it looks like a CSV (has common headers)
            first_line = content.split("\n")[0] if content else ""
            if "HomeTeam" in first_line or "Home" in first_line:
                filepath.write_text(content, encoding="utf-8")
                lines = len(content.strip().split("\n")) - 1  # minus header
                print(f"  [OK]   {filename} ({lines} matches)")
                return True
            else:
                print(f"  [WARN] {filename} - unexpected format, skipping")
                return False
        else:
            print(f"  [FAIL] {filename} - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"  [ERR]  {filename} - {e}")
        return False


def download_all():
    """Download all available CSV data"""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    leagues = get_leagues_with_csv()
    total = 0
    success = 0

    print(f"\nDownloading historical data from football-data.co.uk")
    print(f"Seasons: {', '.join(DOWNLOAD_SEASONS)}")
    print(f"Leagues: {len(leagues)}")
    print("=" * 60)

    for slug, info in leagues.items():
        csv_code = info["csv_code"]
        print(f"\n{info['name']} ({info['country']}) - code: {csv_code}")

        for season in DOWNLOAD_SEASONS:
            total += 1
            if download_csv(slug, csv_code, season):
                success += 1
            time.sleep(0.5)  # Be polite to the server

    print(f"\n{'=' * 60}")
    print(f"Downloaded: {success}/{total} files")
    print(f"Location: {RAW_DIR}")

    return success


if __name__ == "__main__":
    download_all()
