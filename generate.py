from __future__ import annotations
import calendar, json, os, urllib.request
from datetime import date
from pathlib import Path

USERNAME = "irohitkun"
BIRTHDAY = date(2008, 11, 28)
ASCII_ART = r"""..........................................
..........................................
.............:---+**+****+++=-::..........
...........-*#%%@@@@@@@@%%%@@%%#*+=-:.....
........-+#%@@@@%%%@%%%%%%%%@%%%%%%%#=::::
......:*%@@@@@@@%%@@@@@@@@%%@%%@@%%%%#+-::
.....-*@@@@@@@@@@@@@@@@@@@@@%%%@@@%%%%#*::
....:#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%#*--
....-%@@@@@@@@@@@@@@@@@@@@@%%%%@@@@@%##+--
....:*@@@@@@@@@@@@@@@@@@@%%*+==*%@@@%##+--
.....:#@@%#%%@@@@%%%%%%%%#**#*+==#@%%#+---
......*@%##%%%%@@%##***#%%**#%####*==--:-:
......-%@%##%%@@%%%#*+==+====+=+*--:::::::
.......+@@%%%%@@%%%%##*+-::+*==---:-----::
.......:#%%%%%@@%%%%%##**++*###+-::-------
.......-#%%%%@@@@@%%%%%%%%%%##+-::::::----
......-#%%%%%%@@@@@@@%%%###%*=:..:::::::--
....:=#%%%%%%%%%%@@@@@%%###+:......:::::::
-=++*%%###%%%##%%%%%%%-::::...........::::
##%%#######%%###%%%#*===--:.............::"""

def age_parts(born, today):
    years, months, days = today.year-born.year, today.month-born.month, today.day-born.day
    if days < 0:
        pm, py = (today.month-1 or 12), (today.year if today.month > 1 else today.year-1)
        days += calendar.monthrange(py, pm)[1]
        months -= 1
    if months < 0:
        months += 12
        years -= 1
    return years, months, days

def get_json(url):
    req = urllib.request.Request(url, headers={"Accept":"application/vnd.github+json","User-Agent":"irohitkun-profile"})
    token = os.getenv("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def github_stats():
    user = get_json(f"https://api.github.com/users/{USERNAME}")
    repos, page = [], 1
    while True:
        batch = get_json(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}")
        repos.extend(batch)
        if len(batch) < 100: break
        page += 1
    return {"repos": user["public_repos"], "stars": sum(r["stargazers_count"] for r in repos), "followers": user["followers"]}

def esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def make_svg(theme, stats):
    dark = theme == "dark"
    bg, fg = ("#0d1117","#c9d1d9") if dark else ("#ffffff","#24292f")
    muted, accent = ("#8b949e","#58a6ff") if dark else ("#57606a","#0969da")
    warm, border = ("#d29922","#30363d") if dark else ("#9a6700","#d0d7de")
    y, right = 58, []
    years, months, days = age_parts(BIRTHDAY, date.today())
    lines = [
      ("OS","Windows 11, Android 11, Linux"),
      ("Uptime",f"{years} years, {months} months, {days} days"),
      ("Kernel","ECE Diploma Student"),
      ("IDE","Arduino IDE, VS Code"), ("",""),
      ("Languages.Programming","C, Arduino"),
      ("Languages.Real","English, Telugu"), ("",""),
      ("Hobbies.Software","Linux, Minecraft, Self-Hosting, Modding"),
      ("Hobbies.Hardware","Arduino, Electronics, Embedded Systems"), ("",""),
      ("Contact",""),
      ("Email.Personal","rohitseeramsetti@gmail.com"),
      ("Discord","irohitkun"), ("",""),
      ("GitHub Stats",""),
      ("Repos",stats["repos"]), ("Stars",stats["stars"]), ("Followers",stats["followers"])
    ]
    right.append(f'<text x="500" y="{y}" class="mono title" fill="{fg}"><tspan fill="{accent}">{USERNAME}</tspan>@github</text>')
    y += 22
    right.append(f'<line x1="500" y1="{y}" x2="930" y2="{y}" stroke="{border}"/>'); y += 28
    for key, value in lines:
        if not key: y += 12; continue
        if key in ("Contact","GitHub Stats"):
            right.append(f'<text x="500" y="{y}" class="mono section" fill="{fg}">{key}</text>')
            y += 10; right.append(f'<line x1="500" y1="{y}" x2="930" y2="{y}" stroke="{border}"/>'); y += 24
        else:
            right.append(f'<text x="500" y="{y}" class="mono small"><tspan fill="{warm}">{esc(key)}:</tspan><tspan x="690" fill="{muted}">{esc(value)}</tspan></text>')
            y += 24
    portrait, ay = [], 58
    for line in ASCII_ART.splitlines():
        portrait.append(f'<text x="32" y="{ay}" class="ascii" fill="{muted}">{esc(line)}</text>'); ay += 15
    style = '.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}.ascii{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;font-size:13px;white-space:pre}.title{font-size:18px;font-weight:700}.section{font-size:15px;font-weight:700}.small{font-size:13px}'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="620" viewBox="0 0 960 620"><style>{style}</style><rect x="1" y="1" width="958" height="618" rx="14" fill="{bg}" stroke="{border}"/>{"".join(portrait)}{"".join(right)}</svg>'

def main():
    try: stats = github_stats()
    except Exception as e:
        print("GitHub stats unavailable:", e)
        stats = {"repos":"?","stars":"?","followers":"?"}
    Path("dark_mode.svg").write_text(make_svg("dark",stats),encoding="utf-8")
    Path("light_mode.svg").write_text(make_svg("light",stats),encoding="utf-8")

if __name__ == "__main__":
    main()
