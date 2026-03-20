import subprocess, time, sys

BRANCH = "AstroFilterBOT"
CHECK_INTERVAL = 30

def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()

def pull():
    subprocess.run(["git", "pull", "origin", BRANCH])

def start():
    return subprocess.Popen([sys.executable, "bot.py"])

pull()
commit = run("git", "rev-parse", "HEAD")
print(f"🚀 Starting With: {commit[:7]}")
bot = start()

try:
    while True:
        time.sleep(CHECK_INTERVAL)
        run("git", "fetch", "origin", BRANCH)
        remote = run("git", "rev-parse", f"origin/{BRANCH}")
        if remote != commit:
            print(f"🆕 New commit {remote[:7]}, restarting...")
            pull()
            commit = run("git", "rev-parse", "HEAD")
            bot.terminate()
            bot.wait()
            bot = start()
            print(f"✅ Restarted on {commit[:7]}")
except KeyboardInterrupt:
    print("\n👋 Stopping...")
    bot.terminate()
    bot.wait()