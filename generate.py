from __future__ import annotations

import calendar
import json
import os
import urllib.request
from datetime import date
from pathlib import Path


# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

USERNAME = "irohitkun"
BIRTHDAY = date(2008, 11, 28)


ASCII_ART = r"""
..........................................
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
##%%#######%%###%%%#*===--:.............:::
"""


# ─────────────────────────────────────────────
# Uptime
# ─────────────────────────────────────────────

def age_parts(born: date, today: date):
    years = today.year - born.year
    months = today.month - born.month
    days = today.day - born.day

    if days < 0:
        previous_month = today.month - 1 or 12

        previous_year = (
            today.year
            if today.month > 1
            else today.year - 1
        )

        days += calendar.monthrange(
            previous_year,
            previous_month
        )[1]

        months -= 1

    if months < 0:
        months += 12
        years -= 1

    return years, months, days


# ─────────────────────────────────────────────
# GitHub API
# ─────────────────────────────────────────────

def get_json(url):
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "irohitkun-profile"
        }
    )

    token = os.getenv("GITHUB_TOKEN")

    if token:
        request.add_header(
            "Authorization",
            f"Bearer {token}"
        )

    with urllib.request.urlopen(request) as response:
        return json.load(response)


def github_stats():

    user = get_json(
        f"https://api.github.com/users/{USERNAME}"
    )

    repos = []

    page = 1

    while True:

        batch = get_json(
            f"https://api.github.com/users/"
            f"{USERNAME}/repos"
            f"?per_page=100&page={page}"
        )

        repos.extend(batch)

        if len(batch) < 100:
            break

        page += 1

    stars = sum(
        repo.get("stargazers_count", 0)
        for repo in repos
    )

    forks = sum(
        repo.get("forks_count", 0)
        for repo in repos
    )

    return {
        "repos": user.get("public_repos", 0),
        "stars": stars,
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "forks": forks
    }


# ─────────────────────────────────────────────
# SVG helpers
# ─────────────────────────────────────────────

def esc(value):

    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def make_svg(theme, stats):

    dark = theme == "dark"

    if dark:
        background = "#0d1117"
        foreground = "#c9d1d9"
        muted = "#8b949e"
        accent = "#58a6ff"
        label = "#d2a8ff"
        border = "#30363d"

    else:
        background = "#ffffff"
        foreground = "#24292f"
        muted = "#57606a"
        accent = "#0969da"
        label = "#8250df"
        border = "#d0d7de"


    # ─────────────────────────────────────────
    # Calculate uptime
    # ─────────────────────────────────────────

    years, months, days = age_parts(
        BIRTHDAY,
        date.today()
    )

    uptime = (
        f"{years} years, "
        f"{months} months, "
        f"{days} days"
    )


    # ─────────────────────────────────────────
    # SVG dimensions
    # ─────────────────────────────────────────

    WIDTH = 850
    HEIGHT = 700

    INFO_X = 360
    VALUE_X = 550
    svg = []


    # ─────────────────────────────────────────
    # ASCII portrait
    # ─────────────────────────────────────────

    y = 75

    for line in ASCII_ART.splitlines():

        svg.append(
            f'''
            <text
                x="35"
                y="{y}"
                class="ascii"
                fill="{muted}"
            >{esc(line)}</text>
            '''
        )

        y += 18


    # ─────────────────────────────────────────
    # Username
    # ─────────────────────────────────────────

    y = 65

    svg.append(
        f'''
        <text
            x="{INFO_X}"
            y="{y}"
            class="title"
            fill="{accent}"
        >
            {USERNAME}
        </text>
        '''
    )

    y += 20

    svg.append(
        f'''
        <line
            x1="{INFO_X}"
            y1="{y}"
            x2="1000"
            y2="{y}"
            stroke="{border}"
        />
        '''
    )

    y += 35


    # ─────────────────────────────────────────
    # Information rows
    # ─────────────────────────────────────────

    rows = [
    ("OS", "Windows 11, Android 11, Linux"),
    ("Uptime", uptime),
    ("Kernel", "ECE Diploma Student"),
    ("Shell", "Bash, Termux"),
    ("Editor", "VS Code, Arduino IDE"),

    ("Languages.Programming", "C"),
    ("Languages.Real", "English, Telugu"),

    ("Core.Embedded", "Arduino, Electronics"),
    ("Core.Systems", "Linux, Embedded Systems"),
    ("Core.Hardware", "Circuit Prototyping"),

    ("Interests", "Low-Level Systems, Hardware, Linux"),
]

    for key, value in rows:

        svg.append(
            f'''
            <text
                x="{INFO_X}"
                y="{y}"
                class="text"
            >
                <tspan fill="{label}">
                    {esc(key)}:
                </tspan>

                <tspan
                    x="{VALUE_X}"
                    fill="{foreground}"
                >
                    {esc(value)}
                </tspan>
            </text>
            '''
        )

        y += 31


    # ─────────────────────────────────────────
    # Contact
    # ─────────────────────────────────────────

    y += 10

    svg.append(
        f'''
        <text
            x="{INFO_X}"
            y="{y}"
            class="section"
            fill="{foreground}"
        >
            Contact
        </text>
        '''
    )

    y += 14

    svg.append(
        f'''
        <line
            x1="{INFO_X}"
            y1="{y}"
            x2="1000"
            y2="{y}"
            stroke="{border}"
        />
        '''
    )

    y += 28


    contacts = [

        (
            "Email.Personal",
            "rohitseeramsetti@gmail.com"
        ),

        (
            "Discord",
            "irohitkun"
        )

    ]


    for key, value in contacts:

        svg.append(
            f'''
            <text
                x="{INFO_X}"
                y="{y}"
                class="text"
            >

                <tspan fill="{label}">
                    {esc(key)}:
                </tspan>

                <tspan
                    x="{VALUE_X}"
                    fill="{foreground}"
                >
                    {esc(value)}
                </tspan>

            </text>
            '''
        )

        y += 28


    # ─────────────────────────────────────────
    # GitHub stats
    # ─────────────────────────────────────────

    y += 10

    svg.append(
        f'''
        <text
            x="{INFO_X}"
            y="{y}"
            class="section"
            fill="{foreground}"
        >
            GitHub Stats
        </text>
        '''
    )

    y += 14

    svg.append(
        f'''
        <line
            x1="{INFO_X}"
            y1="{y}"
            x2="1000"
            y2="{y}"
            stroke="{border}"
        />
        '''
    )

    y += 30


    stats_text = (

        f"Repos: {stats['repos']}    "

        f"Stars: {stats['stars']}    "

        f"Forks: {stats['forks']}    "

        f"Followers: {stats['followers']}"

    )


    svg.append(
        f'''
        <text
            x="{INFO_X}"
            y="{y}"
            class="stats"
            fill="{foreground}"
        >
            {esc(stats_text)}
        </text>
        '''
    )


    # ─────────────────────────────────────────
    # CSS
    # ─────────────────────────────────────────

    style = f"""

    .ascii {{
        font-family:
            ui-monospace,
            SFMono-Regular,
            Menlo,
            Monaco,
            Consolas,
            monospace;

        font-size: 11px;
        white-space: pre;
    }}

    .title {{
        font-family:
            ui-monospace,
            SFMono-Regular,
            Menlo,
            Monaco,
            Consolas,
            monospace;

        font-size: 21px;
        font-weight: 700;
    }}

    .section {{
        font-family:
            ui-monospace,
            SFMono-Regular,
            Menlo,
            Monaco,
            Consolas,
            monospace;

        font-size: 15px;
        font-weight: 700;
    }}

    .text {{
        font-family:
            ui-monospace,
            SFMono-Regular,
            Menlo,
            Monaco,
            Consolas,
            monospace;

        font-size: 13px;
    }}

    .stats {{
        font-family:
            ui-monospace,
            SFMono-Regular,
            Menlo,
            Monaco,
            Consolas,
            monospace;

        font-size: 13px;
    }}

    """


    return f'''

    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="{WIDTH}"
        height="{HEIGHT}"
        viewBox="0 0 {WIDTH} {HEIGHT}"
    >

        <style>
            {style}
        </style>

        <rect
            x="1"
            y="1"
            width="{WIDTH - 2}"
            height="{HEIGHT - 2}"
            rx="12"
            fill="{background}"
            stroke="{border}"
        />

        {"".join(svg)}

    </svg>

    '''


# ─────────────────────────────────────────────
# Generate files
# ─────────────────────────────────────────────

def main():

    try:

        stats = github_stats()

        print(
            "GitHub stats:",
            stats
        )

    except Exception as error:

        print(
            "Could not fetch GitHub stats:",
            error
        )

        stats = {
            "repos": "?",
            "stars": "?",
            "forks": "?",
            "followers": "?",
            "following": "?"
        }


    Path(
        "dark_mode.svg"
    ).write_text(
        make_svg(
            "dark",
            stats
        ),
        encoding="utf-8"
    )


    Path(
        "light_mode.svg"
    ).write_text(
        make_svg(
            "light",
            stats
        ),
        encoding="utf-8"
    )


    print(
        "Generated dark_mode.svg "
        "and light_mode.svg"
    )


if __name__ == "__main__":
    main()
