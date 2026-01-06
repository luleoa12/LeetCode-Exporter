import requests
import os
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
from rich import print 
from rich.style import Style
import time
from getpass import getpass

def display_welcome():
    console = Console()
    console.print("\033c", end="")
    console.print("\033c", end="")
    console.print(Panel.fit(
        """[bold blue]
    ██╗      ██████╗      ███████╗██╗  ██╗██████╗  ██████╗ ██████╗ ████████╗
    ██║     ██╔════╝      ██╔════╝╚██╗██╔╝██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝
    ██║     ██║           █████╗   ╚███╔╝ ██████╔╝██║   ██║██████╔╝   ██║   
    ██║     ██║           ██╔══╝   ██╔██╗ ██╔═══╝ ██║   ██║██╔══██╗   ██║   
    ███████╗╚██████╗      ███████╗██╔╝ ██╗██║     ╚██████╔╝██║  ██║   ██║   
    ╚══════╝ ╚═════╝      ╚══════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
    [bold cyan]View and export LeetCode problems directly from your terminal[/bold cyan]
        """,
        border_style="blue",
        padding=(1, 2)
    ))

def get_credentials():
    display_welcome()
    
    console = Console()
    # intructions
    console.print("To use this tool, you'll need to provide your LeetCode session information.")
    console.print("You can find these values in your browser's cookies:")
    console.print("1. Open LeetCode in your browser")
    console.print("2. Open Developer Tools (F12 or Right-click -> Inspect)")
    console.print("3. Go to Application/Storage -> Cookies -> https://leetcode.com")
    console.print("4. Find and copy the values for 'LEETCODE_SESSION' and 'csrftoken'\n")
    console.print("[italic white dim]Note: For security, characters will not be visible while typing.[/italic white dim]\n")
    # credentials
    console.print("🔑 [bold cyan]LEETCODE_SESSION:[/bold cyan] ", end="")
    leetcode_session = getpass("")
    console.print("🔑 [bold cyan]LEETCODE_CSRF:[/bold cyan] ", end="")
    leetcode_csrf = getpass("")
    
    console.print("\033c", end="")
    
    return leetcode_session, leetcode_csrf

LEETCODE_SESSION, LEETCODE_CSRF = get_credentials()

session = requests.Session()
session.cookies.set("LEETCODE_SESSION", LEETCODE_SESSION)
session.cookies.set("csrftoken", LEETCODE_CSRF)
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://leetcode.com",
    "x-csrftoken": LEETCODE_CSRF,
    "Content-Type": "application/json"
})

GRAPHQL_URL = "https://leetcode.com/graphql"

SUBMISSION_LIST_QUERY = """
query submissionList($offset: Int!, $limit: Int!) {
  submissionList(offset: $offset, limit: $limit) {
    hasNext
    submissions {
      id
      titleSlug
      statusDisplay
      lang
      timestamp
    }
  }
}
"""

SUBMISSION_DETAILS_QUERY = """
query submissionDetails($id: Int!) {
  submissionDetails(submissionId: $id) {
    code
  }
}
"""

QUESTION_ID_QUERY = """
query questionTitle($slug: String!) {
  question(titleSlug: $slug) {
    questionFrontendId
  }
}
"""

def fetch_all_accepted():
    offset = 0
    limit = 50
    accepted = []

    while True:
        resp = session.post(
            GRAPHQL_URL,
            json={
                "query": SUBMISSION_LIST_QUERY,
                "variables": {"offset": offset, "limit": limit}
            }
        )

        payload = resp.json()
        if "errors" in payload:
            raise RuntimeError(payload["errors"])

        data = payload["data"]["submissionList"]

        for s in data["submissions"]:
            if s["statusDisplay"] == "Accepted":
                accepted.append(s)

        if not data["hasNext"]:
            break

        offset += limit

    return dedupe_latest(accepted)

def dedupe_latest(subs):
    latest = {}
    for s in subs:
        slug = s["titleSlug"]
        if slug not in latest or int(s["timestamp"]) > int(latest[slug]["timestamp"]):
            latest[slug] = s
    return list(latest.values())

def fetch_code(submission_id):
    try:
        resp = session.post(
            GRAPHQL_URL,
            json={
                "query": SUBMISSION_DETAILS_QUERY,
                "variables": {"id": int(submission_id)}
            },
            timeout=10  
        )
        resp.raise_for_status() 

        payload = resp.json()
        
        if "errors" in payload:
            error_msg = f"Error fetching submission {submission_id}: {payload['errors']}"
            print(f"[yellow]{error_msg}[/yellow]")
            return None
            
        if not payload.get("data") or not payload["data"].get("submissionDetails"):
            return None
            
        return payload["data"]["submissionDetails"].get("code")
        
    except requests.exceptions.RequestException as e:
        print(f"[red]Request failed for submission {submission_id}: {str(e)}[/red]")
        return None
    except (ValueError, KeyError) as e:
        print(f"[red]Error processing response for submission {submission_id}: {str(e)}[/red]")
        return None

problem_id_cache = {}

def get_problem_id(slug):
    if slug in problem_id_cache:
        return problem_id_cache[slug]

    resp = session.post(
        GRAPHQL_URL,
        json={
            "query": QUESTION_ID_QUERY,
            "variables": {"slug": slug}
        }
    )

    payload = resp.json()
    if "errors" in payload:
        raise RuntimeError(payload["errors"])

    pid = payload["data"]["question"]["questionFrontendId"]
    problem_id_cache[slug] = pid
    return pid

EXTENSIONS = {
    "python3": "py",
    "python": "py",
    "cpp": "cpp",
    "java": "java"
}

def save_solution(submission, code):
    lang = submission["lang"].lower()
    slug = submission["titleSlug"]

    ext = EXTENSIONS.get(lang)
    if not ext:
        return

    pid = get_problem_id(slug).zfill(4)
    filename = f"{pid}-{slug}.{ext}"

    path = os.path.join("leetcode", lang)
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, filename), "w", encoding="utf-8") as f:
        f.write(code)

def main():
    console = Console()
    display_welcome()
    
    # debug mode - set to True to process only first 5 submissions
    DEBUG_MODE = False
    
    if not LEETCODE_SESSION or not LEETCODE_CSRF:
        console.print("[red]Error: Missing LeetCode credentials[/red]")
        console.print("Please set LEETCODE_SESSION and LEETCODE_CSRF environment variables")
        return
    
    console.print("\n[cyan]Fetching accepted submissions...[/cyan]")
    accepted = fetch_all_accepted()
    
    if not accepted:
        console.print("[yellow]No accepted submissions found![/yellow]")
        return
    else:
        console.print(f"[bold]Found 5 accepted submissions[/bold]\n")
    
    table = Table(
        show_header=True,
        header_style=Style(color="magenta", bold=False)
    )
    table.add_column("#", width=4)
    table.add_column("Problem", style="cyan", no_wrap=True)
    table.add_column("Language", style="green")
    table.add_column("Date", style="yellow")

    submissions_to_process = accepted[:5] if DEBUG_MODE else accepted
    total_submissions = len(submissions_to_process)
    
    with Progress() as progress:
        process_task = progress.add_task(
            "[cyan]Processing submissions...", 
            total=total_submissions
        )
        
        for i, submission in enumerate(submissions_to_process, 1):
            progress.update(process_task, 
                         advance=1, 
                         description=f"[cyan]Processing {i}/{total_submissions}: {submission['titleSlug']}")
            
            table.add_row(
                str(i),
                submission['titleSlug'],
                submission['lang'],
                time.strftime('%Y-%m-%d', time.localtime(int(submission['timestamp'])))
            )
            
            try:
                code = fetch_code(submission['id'])
                if code:
                    save_solution(submission, code)
            except Exception as e:
                print(f"[yellow]Warning: Could not process {submission['titleSlug']}: {str(e)}[/yellow]")
            
            time.sleep(0.1)
    
    console.print("[bold]Processed Submissions:[/bold]")
    console.print(table)
    console.print("\n[bold green]✓ All submissions processed successfully![/bold green]")
    console.print("[yellow]Solutions have been saved to their respective directories.[/yellow]")

if __name__ == "__main__":
    main()
