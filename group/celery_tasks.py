from __future__ import absolute_import
from django.utils import timezone
import pytz
import os
import requests
import json
from celery import Celery
from celery import shared_task
from group.models import *
from group.scripts import *
import imp
import concurrent.futures
from ignite.conf import RMQ_USERNAME, RMQ_PASSWORD, RMQ_VHOST
from ignite.settings import BASE_DIR
import datetime
from group.job import *

SCRIPTS_DIR = os.path.join(BASE_DIR, "group/scripts")
CELERY_ENABLE_UTC = True
BROKER = "amqp://" + RMQ_USERNAME + ":" + RMQ_PASSWORD + "@127.0.0.1/" + RMQ_VHOST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ignite.settings')
app = Celery("ignite", backend="amqp", broker=BROKER)


def run_task_on_single_switch(switch, task):
    file_name = os.path.join(SCRIPTS_DIR, str(task['file']))
    dummy = imp.load_source('module', file_name)
    method = getattr(dummy, task['function'])
    print 'try number: '+str(switch['retry'])+' on '+switch['name']
    return switch, method(switch, task)


def run_task_switches(switches, task, pool):
    switch_count = len(switches)
    count = 0
    break_flag = 0
    runsize = int(task['run_size'])
    pending_switches = []
    if task['failure_action_ind']!='continue':
        pending_switches = switches[runsize:]
        switches = switches[:runsize]
    while switches:
        retry_switches = []
        threads = {pool.submit(run_task_on_single_switch, switch, task) for switch in switches}
        for future in concurrent.futures.as_completed(threads):
            switch, status = future.result()
            switch['retry'] = switch['retry'] - 1
            if status['status'] == 'SUCCESS' or not (switch['retry'] > 0):
                state = {}
                state['id'] = switch['id']
                state['name'] = switch['name']
                state['status'] = status['status']
                state['log'] = status['log']
                ctime = str(datetime.datetime.utcnow())
                ctime = datetime.datetime.strptime(ctime, '%Y-%m-%d %H:%M:%S.%f')
                ctime = timezone.make_aware(ctime, pytz.timezone('UTC'))
                state['ctime'] = ctime
                task['status']['switches'].append(state)
                if(status["status"] == 'SUCCESS'):
                    count = count + 1
                elif task['failure_action_ind']!='continue':
                    break_flag = 1
            else:
                retry_switches.append(switch)
        switches = retry_switches
        if break_flag and not switches:
            for switch in pending_switches: 
                state = {}
                state['id'] = switch['id']
                state['name'] = switch['name']
                state['status'] = 'SKIPPED'
                task['status']['switches'].append(state)
            break
        elif not switches:
            switches = pending_switches[:runsize]
            pending_switches=pending_switches[runsize:]    
    print count
    if count == switch_count:
        task['status']['status'] = 'SUCCESS'
    else:
        task['status']['status'] = 'FAILURE'
    return task['status']['status']


def get_all_switches(task):
    gid = task['group_id']
    grp = Group.objects.get(id=int(gid))
    gsh = GroupSwitch.objects.filter(group__id=int(gid))
    switches = []
    task['status'] = {}
    task['status']['switches'] = []
    index = 0
    for i in gsh:
        sw = {}
        sw['ip'] = i.grp_switch.boot_detail.mgmt_ip
        sw['id'] = i.grp_switch.id
        sw['name'] = i.grp_switch.name
        sw['user'] = grp.username
        #i.username if i.username else grp.username
        sw['pwd'] = grp.password
        #i.password if i.password else grp.password
        sw['retry'] = int(task['retry_count']) + 1
        switches.append(sw)
    return switches


def run_single_sequence(task):
    print 'Running sequence ' + ' on group ' + str(task['group_id'])
    switches = get_all_switches(task)
    image_profile = ImageProfile.objects.get(pk=int(task['image_id']))
    image = {}
    image['name'] = image_profile.profile_name
    image['path'] = image_profile.system_image
    image['id'] = image_profile.id
    image['ip'] = image_profile.image_server_ip
    image['user'] = image_profile.image_server_username
    image['pwd'] = image_profile.image_server_password
    task['image'] = image
    runsize = task['run_size']
    #create a threadpool of size runsize
    with concurrent.futures.ThreadPoolExecutor(max_workers=runsize) as pool:
        run_task_switches(switches, task, pool)
    ctime = str(datetime.datetime.utcnow())
    ctime = datetime.datetime.strptime(ctime, '%Y-%m-%d %H:%M:%S.%f')
    ctime = timezone.make_aware(ctime, pytz.timezone('UTC'))
    task['ctime'] = ctime
    return task['status']['status']

@shared_task
def run_single_job(jid, time):
    print 'celery worker got a job with id ' + str(jid) + ' and time ' + str(time)
    jb = Job.objects.get(id=jid)
    jb.status = 'RUNNING'
    jb.save()
    tasks = []
    count = 0
    break_flag=0
    for task in jb.tasks:
        if break_flag  == 1:
            task['status']= {'status':'SKIPPED'}
            task['status']['switches']=[]
        elif task['type'] == 'switch_upgrade':
            task['function'] = 'update_os_image_single_switch'
            task['file'] = 'upgrade.py'
            status = run_single_sequence(task)
            if status == 'SUCCESS':
                count = count + 1
            elif task['failure_action_grp']!='continue':
                break_flag = 1
        tasks.append(task)
    if count == len(tasks):
        jb.status = 'SUCCESS'
    else:
        jb.status = 'FAILURE'
    jb.tasks = tasks
    ref_count_delete(jb)
    ctime = str(datetime.datetime.utcnow())
    ctime = datetime.datetime.strptime(ctime, '%Y-%m-%d %H:%M:%S.%f')
    ctime = timezone.make_aware(ctime, pytz.timezone('UTC'))
    jb.ctime = ctime
    print tasks
    jb.save()
