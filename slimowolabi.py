import re
import requests
import random
import json
import os
import sys
import time

# ============================================================
#  COLOR CODES (ANSI)
# ============================================================
class C:
    RESET   = '\033[0m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'
    RED     = '\033[91m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    BLUE    = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN    = '\033[96m'
    WHITE   = '\033[97m'

if os.name == 'nt':
    os.system('color')
    os.system('')

# ============================================================
#  LOGO
# ============================================================
LOGO = f"""{C.CYAN}{C.BOLD}
                ███████╗██╗██╗     ███████╗     
                ██╔════╝██║██║     ██╔════╝    
                █████╗  ██║██║     █████╗      
                ██╔══╝  ██║██║     ██╔══╝      
                ██║     ██║███████╗███████╗    
                ╚═╝     ╚═╝╚══════╝╚══════╝     
{C.MAGENTA}            ── F B   F O L L O W E R   S C R A P E R ──
{C.YELLOW}                ⚡ Powered by SLIMOWOLABI ⚡
{C.RESET}"""

LINE = f"{C.CYAN}{'─' * 56}{C.RESET}"

# ============================================================
#  HEADERS
# ============================================================
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'cache-control': 'max-age=0',
    'dpr': '1.125',
    'priority': 'u=0, i',
    'sec-ch-prefers-color-scheme': 'dark',
    'sec-ch-ua': '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36',
    'viewport-width': '924',
}

# ============================================================
#  GLOBAL SESSION STATE
# ============================================================
SESSION = {
    "logged_in": False,
    "cookie":    None,
    "data":      None,
    "name":      None,
    "uid":       None,
}

# ============================================================
#  HELPERS
# ============================================================
def log(tag, msg, color=C.WHITE):
    ts = time.strftime("%H:%M:%S")
    print(f"{C.DIM}[{ts}]{C.RESET} {color}{C.BOLD}[{tag}]{C.RESET} {color}{msg}{C.RESET}")

def ok(msg):    log("✔", msg, C.GREEN)
def err(msg):   log("✘", msg, C.RED)
def info(msg):  log("i", msg, C.CYAN)
def warn(msg):  log("!", msg, C.YELLOW)
def proc(msg):  log("»", msg, C.MAGENTA)

def banner():
    os.system("cls" if os.name == "nt" else "clear")
    print(LOGO)

def _safe(regex, text, group=1, default=None):
    m = re.search(regex, text)
    return m.group(group) if m else default

def require_login():
    if not SESSION["logged_in"]:
        print()
        err(f"{C.BOLD}First login with fresh cookies!{C.RESET}")
        warn("Use menu option [3] to login.")
        print(LINE)
        input(f"{C.DIM}Press Enter to return to menu...{C.RESET}")
        return False
    return True

# ============================================================
#  PARSER
# ============================================================
def GetData(req):
    try:
        req = str(req)
        av       = _safe(r'"actorID":"(.*?)"', req)
        __user   = av
        __a      = str(random.randrange(1, 6))
        __hs     = _safe(r'"haste_session":"(.*?)"', req)
        __ccg    = _safe(r'"connectionClass":"(.*?)"', req)
        __spin_r = _safe(r'"__spin_r":(.*?),', req)
        __spin_b = _safe(r'"__spin_b":"(.*?)"', req)
        __spin_t = _safe(r'"__spin_t":(.*?),', req)
        __hsi    = _safe(r'"hsi":"(.*?)"', req)
        fb_dtsg  = _safe(r'"DTSGInitialData",\[\],{"token":"(.*?)"}', req)
        jazoest  = _safe(r'jazoest=(.*?)"', req)
        lsd      = _safe(r'"LSD",\[\],{"token":"(.*?)"}', req)

        if not (av and fb_dtsg and lsd):
            return {}

        return {
            'av': av, '__user': __user, '__a': __a, '__hs': __hs,
            'dpr': '1.5', '__ccg': __ccg, '__rev': __spin_r,
            '__spin_r': __spin_r, '__spin_b': __spin_b, '__spin_t': __spin_t,
            '__hsi': __hsi, '__comet_req': '15',
            'fb_dtsg': fb_dtsg, 'jazoest': jazoest, 'lsd': lsd
        }
    except Exception as e:
        err(f"Token parse failed: {e}")
        return {}

# ============================================================
#  LOGIN / LOGOUT
# ============================================================
def login_with_cookie(ck):
    if not ck or not ck.strip():
        err("Cookie is empty.")
        return None, None

    try:
        r = requests.get(
            "https://www.facebook.com/me",
            cookies={"cookie": ck},
            headers=headers,
            timeout=25,
            allow_redirects=True
        )
    except Exception as e:
        err(f"Network error while logging in: {e}")
        return None, None

    html = r.text

    if "/login" in r.url or "login_form" in html or "checkpoint" in r.url:
        err("Cookie is INVALID or expired (redirected to login/checkpoint).")
        return None, None

    data = GetData(html)
    if not data:
        err("Could not extract session tokens — cookie likely invalid.")
        return None, None

    name = (
        _safe(r'"NAME":"(.*?)"', html) or
        _safe(r'<title>(.*?)</title>', html) or
        "Unknown"
    ).strip()

    return data, name

def do_login():
    banner()
    print(f"{C.MAGENTA}{C.BOLD}  ┌── LOGIN ──────────────────────────────────────┐{C.RESET}")

    if SESSION["logged_in"]:
        warn(f"Already logged in as {C.BOLD}{SESSION['name']}{C.RESET}")
        warn("Logout first (menu option 4) if you want to switch accounts.")
        print(LINE)
        input(f"{C.DIM}Press Enter to return to menu...{C.RESET}")
        return

    ck = input(f"{C.YELLOW} ➤ Enter Fresh Cookie : {C.GREEN}").strip()
    print(LINE)

    info("Validating cookie with Facebook...")
    data, name = login_with_cookie(ck)

    if not data:
        print(LINE)
        err("Login failed. Get a fresh cookie and try again.")
        print(LINE)
        input(f"{C.DIM}Press Enter to return to menu...{C.RESET}")
        return

    SESSION.update({
        "logged_in": True,
        "cookie":    ck,
        "data":      data,
        "name":      name,
        "uid":       data.get("av"),
    })

    print(LINE)
    ok(f"Login SUCCESS  •  Account: {C.BOLD}{name}{C.RESET}")
    ok(f"Session Actor ID: {C.BOLD}{SESSION['uid']}{C.RESET}")
    print(LINE)
    input(f"{C.DIM}Press Enter to return to menu...{C.RESET}")

def do_logout():
    banner()
    print(f"{C.MAGENTA}{C.BOLD}  ┌── LOGOUT ─────────────────────────────────────┐{C.RESET}")

    if not SESSION["logged_in"]:
        warn("You are not logged in.")
        print(LINE)
        input(f"{C.DIM}Press Enter to return to menu...{C.RESET}")
        return

    confirm = input(f"{C.YELLOW} Are you sure you want to logout? (y/n) : {C.RESET}").strip().lower()
    if confirm != "y":
        info("Logout cancelled.")
        print(LINE)
        input(f"{C.DIM}Press Enter to return to menu...{C.RESET}")
        return

    SESSION.update({
        "logged_in": False,
        "cookie":    None,
        "data":      None,
        "name":      None,
        "uid":       None,
    })

    print(LINE)
    ok("Logged out successfully. Session cleared.")
    print(LINE)
    input(f"{C.DIM}Press Enter to return to menu...{C.RESET}")

# ============================================================
#  SCRAPER
#  Console  → UID only  [FILE] style
#  File     → uid|name
# ============================================================
def get_followers(uid, data, ck, filename, counter):
    """
    counter : dict like {"total": 0}
    Returns list of dicts: {"uid": ..., "name": ...}
    """
    try:
        req2 = requests.get(
            f"https://www.facebook.com/{uid}/followers",
            cookies={"cookie": ck}, headers=headers, timeout=25
        )
        html = req2.text
        end_cursor = _safe(r'"end_cursor":"(.*?)"', html)
        cltoken    = _safe(r'"collectionToken":"(.*?)"', html)

        if not end_cursor or not cltoken:
            warn(f"No followers / private / not found for {uid}")
            return []

    except Exception as e:
        err(f"Fetch failed for {uid}: {e}")
        return []

    results = []
    page = 1

    while end_cursor:
        payload = dict(data)
        payload.update({
            '__crn': 'comet.fbweb.CometProfileFollowersTabRoute',
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
            'server_timestamps': 'true',
            'variables': json.dumps({
                'count': 8,
                'cursor': end_cursor,
                'scale': 1,
                'search': None,
                'id': cltoken,
                '__relay_internal__pv__FBProfile_enable_perf_improv_gkrelayprovider': True
            }),
            'doc_id': '26157687557261750'
        })

        try:
            r = requests.post('https://www.facebook.com/api/graphql/',
                              cookies={"cookie": ck}, headers=headers,
                              data=payload, timeout=30)
            datax = r.json()
            edges = datax["data"]["node"]["pageItems"]["edges"]
            end   = datax["data"]["node"]["pageItems"]["page_info"]["end_cursor"]
        except Exception as e:
            err(f"GraphQL page {page} error: {e}")
            break

        for item in edges:
            node = item.get("node", {})
            name = node.get("title", {}).get("text")
            nid  = node.get("node", {}).get("id")

            if nid:
                results.append({"uid": nid, "name": name or ""})
                counter["total"] += 1

                # ---------- SAVE TO FILE: uid|name ----------
                with open(filename, "a", encoding="utf-8") as f:
                    f.write(f"{nid}|{name or ''}\n")

                # ---------- PRINT TO CONSOLE: UID only ----------
                print(f"{C.MAGENTA}[FILE]{C.RESET} {C.GREEN}SUCCESSFULLY EXTRACTED FROM{C.RESET} "
                      f"{C.DIM}:{C.RESET} {C.BOLD}{C.CYAN}{nid}{C.RESET}")

        proc(f"Page {page} done  •  collected {len(results)}")
        page += 1
        end_cursor = end

    return results

# ============================================================
#  OPTION 1 : FILE CREATE
# ============================================================
def do_file_create():
    banner()
    print(f"{C.MAGENTA}{C.BOLD}  ┌── FILE CREATE ────────────────────────────────┐{C.RESET}")

    if not require_login():
        return
    print("Enter UID from Public followers account.")
    start_uid = input(f"{C.YELLOW} ➤ Enter Public UID : {C.RESET}").strip()
    print(LINE)
    filename = input(f"{C.YELLOW} ➤ Output File Name     : {C.RESET}").strip()
    print(LINE)

    if not start_uid:
        err("No target UID given.")
        input(f"{C.DIM}Press Enter to return to menu...{C.RESET}")
        return

    if not filename:
        filename = "followers.txt"
    if not filename.endswith(".txt"):
        filename += ".txt"

    info(f"Saving results to → {C.BOLD}{filename}{C.RESET}")
    print(LINE)

    data = SESSION["data"]
    ck   = SESSION["cookie"]

    uids = [start_uid]
    processed = set()
    counter = {"total": 0}

    i = 0
    while i < len(uids):
        current_uid = uids[i]
        if current_uid in processed:
            i += 1
            continue

        print()
        proc(f"Processing [{C.BOLD}{i+1}/{len(uids)}{C.RESET}] → {C.CYAN}{current_uid}{C.RESET}")
        print(LINE)

        processed.add(current_uid)
        followers = get_followers(current_uid, data, ck, filename, counter)

        for user in followers:
            uid = user["uid"]
            if uid not in processed and uid not in uids:
                uids.append(uid)

        i += 1

        print(LINE)
        info(f"Queue: {C.BOLD}{len(uids)}{C.RESET}  |  "
             f"Processed: {C.BOLD}{len(processed)}{C.RESET}  |  "
             f"Total: {C.BOLD}{counter['total']}{C.RESET}")
        print(LINE)

    print()
    print(f"{C.MAGENTA}{C.BOLD}[FILE]{C.RESET} {C.YELLOW}TOTAL EXTRACTED{C.RESET} "
          f"{C.DIM}:{C.RESET} {C.GREEN}{C.BOLD}[{counter['total']}]{C.RESET}")
    print(LINE)
    ok(f"File: {C.BOLD}{filename}{C.RESET}  (format: uid|name)")
    print(LINE)
    input(f"{C.DIM}Press Enter to return to menu...{C.RESET}")

# ============================================================
#  OPTION 2 : REMOVE DUPLICATE
#  Works with both "uid" and "uid|name" lines
# ============================================================
def do_remove_duplicate():
    banner()
    print(f"{C.MAGENTA}{C.BOLD}  ┌── REMOVE DUPLICATE ───────────────────────────┐{C.RESET}")

    if not require_login():
        return

    src = input(f"{C.YELLOW} ➤ Input File  (with duplicates) : {C.RESET}").strip()
    print(LINE)

    if not os.path.exists(src):
        err(f"File not found: {src}")
        input(f"{C.DIM}Press Enter to return to menu...{C.RESET}")
        return

    out = input(f"{C.YELLOW} ➤ Output File (clean)           : {C.RESET}").strip()
    print(LINE)

    if not out:
        out = "clean_" + os.path.basename(src)
    if not out.endswith(".txt"):
        out += ".txt"

    seen = set()
    kept = 0
    dup  = 0

    try:
        with open(src, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        err(f"Read error: {e}")
        input(f"{C.DIM}Press Enter to return to menu...{C.RESET}")
        return

    info(f"Loaded {C.BOLD}{len(lines)}{C.RESET} lines from {src}")

    with open(out, "w", encoding="utf-8") as f:
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Key = UID (part before |), works for both formats
            key = line.split("|")[0].strip()
            if key in seen:
                dup += 1
                continue
            seen.add(key)
            f.write(line + "\n")
            kept += 1

    print(LINE)
    ok(f"Original  : {C.BOLD}{len(lines)}{C.RESET}")
    ok(f"Kept      : {C.BOLD}{kept}{C.RESET}")
    ok(f"Removed   : {C.BOLD}{dup}{C.RESET}")
    ok(f"Output    : {C.BOLD}{out}{C.RESET}")
    print(LINE)
    input(f"{C.DIM}Press Enter to return to menu...{C.RESET}")

# ============================================================
#  MENU
# ============================================================
def menu():
    while True:
        banner()

        status = (
            f"{C.GREEN}● LOGGED IN  ({SESSION['name']}){C.RESET}"
            if SESSION["logged_in"]
            else f"{C.RED}● NOT LOGGED IN{C.RESET}"
        )

        print(f"""{C.CYAN}╔══════════════════════════════════════════════════════╗
║{C.YELLOW}                   📋  M A I N   M E N U              {C.CYAN}║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║   {C.WHITE}[1]{C.CYAN}  📁  File Create                                  ║
║   {C.WHITE}[2]{C.CYAN}  🧹  Remove Duplicate                             ║
║   {C.WHITE}[3]{C.CYAN}  🔐  Login with Cookies                           ║
║   {C.WHITE}[4]{C.CYAN}  🚪  Logout                                       ║
║   {C.WHITE}[0]{C.CYAN}  ❌  Exit                                         ║
║                                                      ║
╠══════════════════════════════════════════════════════╣
║  Status : {status}
╚══════════════════════════════════════════════════════╝{C.RESET}
""")

        choice = input(f"{C.YELLOW} ➤ Select option : {C.RESET}").strip()

        if choice == "1":
            do_file_create()
        elif choice == "2":
            do_remove_duplicate()
        elif choice == "3":
            do_login()
        elif choice == "4":
            do_logout()
        elif choice == "0":
            print()
            info("Goodbye! 👋")
            sys.exit(0)
        else:
            err("Invalid option. Choose 0-4.")
            time.sleep(1)

# ============================================================
#  ENTRY
# ============================================================
if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print()
        warn("Interrupted by user. Goodbye!")
        sys.exit(0)
