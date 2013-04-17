from __future__ import with_statement
import datetime
import glob

from fabric.api import *
from config.fabconfig import *

env.hosts = REMOTE_HOSTS
env.user = USER
env.sudo_user = FS_USER
env.key_filename = KEY_FILENAME


def setup_clean():
    with prefix('source %s/bin/activate' % VENV_PATH):
        with cd(WORKING_PATH):
            try:
                sudo("rm -rf %s" % CURRENT_DIR)
            except:
                pass
            try:
                sudo("rm -rf %s" % RELEASES_DIR)
            except:
                pass
            try:
                sudo("rm -rf %s" % CHECKOUT_DIR)
            except:
                pass
            sudo("mkdir -p %s %s" % (RELEASES_DIR, SHARED_DIR))
            sudo("git clone %s %s" % (GIT_URL, CHECKOUT_DIR))
    create_release()
    symlink_current()


def use_branch():
    with cd("%s/%s" % (WORKING_PATH, CHECKOUT_DIR)):
        sudo("git checkout %s" % GIT_BRANCH)


def update_remote_code():
    with cd("%s/%s" % (WORKING_PATH, CHECKOUT_DIR)):
        sudo("git pull")


def create_release():
    release = datetime.datetime.now().isoformat()
    release_dir = "%s/%s" % (RELEASES_DIR, release)
    with cd(WORKING_PATH):
        sudo("mkdir %s" % release_dir)
        sudo("cp -Rv %s/* %s/" % (CHECKOUT_DIR, release_dir))
        sudo("rm -rf %s/.git %s/.gitignore" % (release_dir, release_dir))


def symlink_current():
    with cd(WORKING_PATH):
        dirs = run("ls -d %s/*/" % RELEASES_DIR).split()
        dirs.sort()
        dirs.reverse()
        dir = dirs[0].strip('/')
        try:
            sudo("unlink %s" % CURRENT_DIR)
        except:
            pass
        sudo("ln -nfs %s %s" % (dir, CURRENT_DIR))
        with cd(dir):
            for path in SHARED_FILES:
                sudo("ln -nfs %s/%s/%s %s" % (WORKING_PATH, SHARED_DIR,
                                              path.split('/')[-1],
                                              path))
    with cd("%s/bin" % HOME_PATH):
        try:
            sudo("unlink ./run")
            sudo("unlink ./stop")
        except:
            pass
        sudo("ln -nfs %s/%s/config/run" % (WORKING_PATH, CURRENT_DIR))
        sudo("ln -nfs %s/%s/config/stop" % (WORKING_PATH, CURRENT_DIR))


def sync_remote_assets():
    with prefix("source %s/bin/activate" % VENV_PATH):
        with cd("%s/%s" % (WORKING_PATH, CURRENT_DIR)):
            sudo("./manage.py collectstatic --noinput")


def install_dependencies():
    with prefix("source %s/bin/activate" % VENV_PATH):
        with cd("%s/%s" % (WORKING_PATH, CURRENT_DIR)):
            sudo("pip install -r requirements.txt")


def run_migrations():
    with prefix("source %s/bin/activate" % VENV_PATH):
        with cd("%s/%s" % (WORKING_PATH, CURRENT_DIR)):
            try:
                sudo("./manage.py createcachetable %s" % CACHE_TABLE_NAME)
            except:
                pass
            sudo("./manage.py syncdb --noinput")
            sudo("./manage.py migrate --noinput")


def stop():
    with cd(HOME_PATH):
        sudo("./bin/stop")


def restart():
    with prefix("source %s/bin/activate" % VENV_PATH):
        with cd(HOME_PATH):
            sudo("./bin/run")


def cleanup():
    with cd(WORKING_PATH):
        dirs = run("ls -d %s/*/" % RELEASES_DIR).split()
        dirs.sort()
        dirs.reverse()
        try:
            to_clean = dirs[PAST_RELEASES:]
            for dir in to_clean:
                sudo("rm -rf %s" % dir)
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
    run_migrations()
    cleanup()
    restart()


def rollback():
    with cd(WORKING_PATH):
        dirs = run("ls -d %s/*/" % RELEASES_DIR).split()
        dirs.sort()
        dirs.reverse()
        dir = dirs[1].strip('/')
        try:
            sudo("unlink %s" % CURRENT_DIR)
        except:
            pass
        sudo("ln -s %s %s" % (dir, CURRENT_DIR))
        sudo("rm -rf %s" % dirs[0].strip('/'))
    install_dependencies()
    sync_remote_assets()
    restart()
