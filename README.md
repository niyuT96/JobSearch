# AI-powered Job Search and Application Optimization System
This project is a personal job application automation tool designed for job seekers. It combines web crawling, structured job data extraction, and AI-driven document optimization into a single pipeline. LinkedIn is crawled via joeyism/linkedin_scraper.
  
The system generates job search URLs based on user-defined keywords and location, and uses Playwright-based crawlers to collect job URLs and job descriptions from platforms such as Xing, StepStone, and Accso. LinkedIn uses a dedicated scraper.  
  
Extracted job descriptions are analyzed using AI models to derive structured job information and key requirements. Based on this context, the system optimizes user-provided CVs and motivation letters to improve relevance, keyword coverage, and Applicant Tracking System (ATS) compatibility.  
  
To balance quality and cost, the system employs a dual-model architecture: a lightweight model for job information extraction and a more advanced model for CV and motivation letter optimization.  

### Architecture Overview

1. Keyword-based job search URL generation
2. Playwright crawler collects job URLs and raw job descriptions
3. AI-powered job description analysis and requirement extraction (Developing...)
- Lightweight LLM extracts structured job fields and core requirements
- Advanced LLM optimizes CV and motivation letter using job context
4. Output optimized keywords and application-ready content
![Flowchart](flowchart.png)
### Tech Stack

- Python
- Playwright (web crawling and data collection)
- LangChain (LLM orchestration and prompt pipelines)（Not Finish...）
- Large Language Models (LLMs)

### Crawling Dependencies

- `pip install playwright bs4`
- `playwright install`
- `pip install linkedin_scraper`

### LinkedIn Session (Recommended)

You can save a session once and reuse it to avoid repeated logins:

```
setx LINKEDIN_EMAIL "your@email.com"
setx LINKEDIN_PASSWORD "yourpassword"
setx LINKEDIN_SAVE_SESSION "1"
setx LINKEDIN_SESSION_PATH "session.json"
```

The crawler will automatically load `session.json` if it exists.

### Run Example (Fetch Any URL) 

```python
from crawling.site_registry import detect_site
from crawling.playwright_client import PlaywrightClient

url = "https://www.stepstone.de/..."
client = PlaywrightClient()
site = detect_site(url)

html = client.fetch(
    url,
    wait_for=None,
    wait_jobposting=site.wait_jobposting if site else False,
)

if site and site.follow_iframe:
    html = client.fetch_iframe(url, site.iframe_selector)

print(html[:500])
```

# Set up your google drive credential （Not Finish...）
Set up your google drive OAuth in the cloud and create a desktop OAuth and download the json to your computer and change the name of the json into GoogleOAuth_Desktop.json
Add it to your os env variables and run
And type the following in your computer
$env:GOOGLE_CREDENTIALS_PATH_Desktop="d:\Credential\GoogleOAuth_Desktop.json"
$env:GOOGLE_TOKEN_PATH="d:\Credential\token.json"
Then run the googleDriveOperations.py to finish the set up of the credential
