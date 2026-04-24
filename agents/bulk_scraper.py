import requests
from bs4 import BeautifulSoup
import json
import time

import os  # Make sure this is imported at the top!

def load_processed_ids():
    """Reads the 'Memory' file to see what we already scraped."""
    if os.path.exists("data/processed_ids.txt"):
        with open("data/processed_ids.txt", "r") as f:
            return set(f.read().splitlines())
    return set()

def save_processed_id(job_id):
    """Adds a new Job ID to the 'Memory' file."""
    with open("data/processed_ids.txt", "a") as f:
        f.write(f"{job_id}\n")

def scrape_bulk_jobs(keywords, location, num_jobs=50):
    all_jobs = []
    # 1. Load the 'Memory' of jobs we already have
    processed_ids = load_processed_ids()
    
    # LinkedIn shows 25 jobs per "page". start=0, 25, 50...
    for start in range(0, num_jobs, 25):
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location={location}&start={start}"
        print(f"📡 Harvesting {keywords} from index: {start}...")
        
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all('li')
        except Exception as e:
            print(f"❌ Connection error: {e}")
            break

        for card in cards:
            try:
                # 2. Extract the Unique Job ID first
                base_card = card.find('div', {'class': 'base-card'})
                if not base_card:
                    continue
                
                job_id = base_card.get('data-entity-urn').split(':')[-1]
                
                # 3. THE CHECK: Skip if we've seen this ID before
                if job_id in processed_ids:
                    print(f"⏩ Skipping ID {job_id}: Already processed.")
                    continue

                title = card.find('h3', {'class': 'base-search-card__title'}).text.strip()
                
                # 4. Get the full job description
                job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
                job_res = requests.get(job_url)
                job_soup = BeautifulSoup(job_res.text, 'html.parser')
                
                description_element = job_soup.find('div', {'class': 'description__text'})
                if not description_element:
                    continue
                
                description = description_element.text.strip()

                # 5. Add to our results list
                all_jobs.append({
                    "title": title,
                    "description": description,
                    "id": job_id
                })

                # 6. SAVE TO MEMORY immediately so we don't lose progress
                save_processed_id(job_id)
                processed_ids.add(job_id) # Update current session memory

                print(f"✅ New Job Found: {title}")
                time.sleep(1) # Be nice to their servers!
                
            except Exception as e:
                # Log the error quietly and move to the next card
                continue

    return all_jobs

if __name__ == "__main__":
    # The list of roles you want to target
    target_roles = [
        "Data Scientist", 
        "Python Developer", 
        "Data Analyst", 
        "Data Engineer",
        "Machine Intelligence Engineer"
    ]
    
    all_harvested_jobs = []

    for role in target_roles:
        print(f"\n--- 🎯 Starting harvest for: {role} ---")
        # num_jobs=25 per role to keep it safe and diverse
        role_data = scrape_bulk_jobs(role, "Canada", num_jobs=25)
        all_harvested_jobs.extend(role_data)
        
        # Critical Infra Tip: Wait 5 seconds between roles to avoid IP blocks
        print("😴 Cooling down for 5 seconds...")
        time.sleep(5)

    # Save everything into one master file for the RAG system
    with open("data/bulk_jobs_master.json", "w") as f:
        json.dump(all_harvested_jobs, f, indent=4)
        
    print(f"\n✨ DONE! Total jobs collected across all roles: {len(all_harvested_jobs)}")