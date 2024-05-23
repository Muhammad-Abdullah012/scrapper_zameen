import os

LOCK_FILE = os.getcwd() + "/scrapper_job.lock"


def create_lock():
    with open(LOCK_FILE, "w") as lockfile:
        lockfile.write(str(os.getpid()))


def remove_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


def is_locked():
    return os.path.exists(LOCK_FILE)
