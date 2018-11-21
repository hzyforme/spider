import os
from apscheduler.schedulers.blocking import BlockingScheduler
from os.path import getsize

def clear_nohup():
    size = getsize('nohup.out')/(1024*1024)
    if size > 100:
        os.system('cp /dev/null nohup.out')

if __name__ == '__main__':
    sched = BlockingScheduler()
    sched.add_job(clear_nohup, 'interval', minutes=10)
    sched.start()
