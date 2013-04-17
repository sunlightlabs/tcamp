from __future__ import with_statement
import datetime
import glob

from fabric.api import *
from config.fabconfig import *

env.hosts = REMOTE_HOSTS
env.user = USER
env.key_filename = KEY_FILENAME


def setup_clean():
    with prefix('source %s/bin/activate' % VENV_PATH):
        with cd(WORKING_PATH):
            try:
                sudo("rm -rf %s" % CURRENT_DIR, user=FS_USER)
            except:
                pass
            try:
                sudo("rm -rf %s" % RELEASES_DIR, user=FS_USER)
            except:
                pass
            try:
                sudo("rm -rf %s" % CHECKOUT_DIR, user=FS_USER)
            except:
                pass
            sudo("mkdir -p %s %s" % (RELEASES_DIR, SHARED_DIR), user=FS_USER)
            sudo("git clone %s %s" % (GIT_URL, CHECKOUT_DIR), user=FS_USER)
    create_release()
    symlink_current()

def use_branch():
    with cd("%s/%s" % (WORKING_PATH, CHECKOUT_DIR)):
        sudo("git checkout %s" % GIT_BRANCH, user=FS_USER)


def update_remote_code():
    with cd("%s/%s" % (WORKING_PATH, CHECKOUT_DIR)):
        sudo("git pull", user=FS_USER)


def create_release():
    release = datetime.datetime.now().isoformat()
    release_dir = "%s/%s" % (RELEASES_DIR, release)
    with cd(WORKING_PATH):
        sudo("mkdir %s" % release_dir, user=FS_USER)
        sudo("cp -Rv %s/* %s/" % (CHECKOUT_DIR, release_dir), user=FS_USER)
        sudo("rm -rf %s/.git %s/.gitignore" % (release_dir, release_dir), user=FS_USER)


def symlink_current():
    with cd(WORKING_PATH):
        dirs = run("ls -d %s/*/" % RELEASES_DIR).split()
        dirs.sort()
        dirs.reverse()
        dir = dirs[0].strip('/')
        try:
            sudo("unlink %s" % CURRENT_DIR, user=FS_USER)
        except:
            pass
        sudo("ln -nfs %s %s" % (dir, CURRENT_DIR), user=FS_USER)
        with cd(dir):
            for path in SHARED_FILES:
                sudo("ln -nfs %s/%s/%s %s" % (WORKING_PATH, SHARED_DIR,
                                              path.split('/')[-1],
                                              path), user=FS_USER)
    with cd("%s/bin" % HOME_PATH):
        try:
            sudo("unlink ./run")
        except:
            pass
        sudo("ln -nfs %s/%s/run" % (WORKING_PATH, CURRENT_DIR), user=FS_USER)


def sync_remote_assets():
    with prefix("source %s/bin/activate" % VENV_PATH):
        with cd("%s/%s" % (WORKING_PATH, CURRENT_DIR)):
            sudo("./manage.py collectstatic --noinput", user=FS_USER)


def install_dependencies():
    with prefix("source %s/bin/activate" % VENV_PATH):
        with cd("%s/%s" % (WORKING_PATH, CURRENT_DIR)):
            sudo("pip install -r requirements.txt", user=FS_USER)


def restart():
    with cd(HOME_PATH):
        sudo("./bin/run", user=FS_USER)


def cleanup():
    with cd(WORKING_PATH):
        dirs = glob.glob('%s/*' % RELEASES_DIR)
        dirs.sort()
        dirs.reverse()
        try:
            to_clean = dirs[PAST_RELEASES:]
            for dir in to_clean:
                sudo("rm -rf %s" % dir, user=FS_USER)
        except IndexError:
            pass


def stage():
    local("git commit -am")
    local("git push heroku master")


def deploy():
    update_remote_code()
    create_release()
    symlink_current()
    install_dependencies()
    sync_remote_assets()
    restart()
    cleanup()


def rollback():
    with cd(WORKING_PATH):
        dirs = run("ls -d %s/*/" % RELEASES_DIR).split()
        dirs.sort()
        dirs.reverse()
        dir = dirs[1].strip('/')
        try:
            sudo("unlink %s" % CURRENT_DIR, user=FS_USER)
        except:
            pass
        sudo("ln -s %s %s" % (dir, CURRENT_DIR), user=FS_USER)
        sudo("rm -rf %s" % dirs[0].strip('/'))
    install_dependencies()
    sync_remote_assets()
    restart()
