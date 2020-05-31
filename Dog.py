import os
import logging
import subprocess
from datetime import datetime, timedelta
import platform

from PIL import Image
from PIL import ImageChops
import numpy as np
import math, operator

import pickle
from googleapiclient.discovery import build             # pip install --upgrade google-api-python-client
from google_auth_oauthlib.flow import InstalledAppFlow  # pip install google-auth-oauthlib
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload

if 'pi' in platform.node():
    import RPi.GPIO as GPIO


#_______________________________________________________________________________________________________
class Dog:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cmd_l = ['raspistill',
                 '-rot', '90',
                 '-w', '1200', '-h', '900',
                 #'--colfx', '128:128',     # greyscale
                 '-n',                      # --nopreview
                 '-t', '1000',              # timeout in ms before take pic =~ 1 sec
                 '-o']

        # cmd_l_bb = ['raspistill', '-rot', '270',
        # #'-n',
        # '-t', '1000', '-o', bb_jpg]

        self.aa_jpg = 'pic/aa.jpg'
        self.bb_jpg = 'pic/bb.jpg'
        self.aa_grey_jpg = 'pic/aa_grey.jpg'
        self.bb_grey_jpg = 'pic/bb_grey.jpg'
        self.dd_jpg = 'pic/dd.jpg'
        # self.pic_file = self.aa_jpg
        self.rmss_l = []
        self.rmss_l_pic_warn = []
        self.rmss_idx = 0

        if 'pi' in platform.node():
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(26, GPIO.IN)  # PIR

        try:
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            self.gd_service = build('drive', 'v3', credentials=creds, cache_discovery=False)
        except Exception as e:
            self.logger.info('%s %s', 'ERROR connect GoogleDrive: ', e)

    #
    def rmsdiff(self, im1, im2):
        diff = ImageChops.difference(im2, im1)
        diff.save(self.dd_jpg, 'JPEG')       # dd_sz = os.stat(dd_jpg).st_size
        h = diff.histogram()
        sq = (value * ((idx % 256) ** 2) for idx, value in enumerate(h))
        sum_of_squares = sum(sq)
        rms = math.sqrt(sum_of_squares / float(im1.size[0] * im1.size[1]))
        return rms                      #, dd_sz

    #
    def dog_act(self):
        cur_rms = 0
        self.sw_dog_msg = False

        try:
            process1 = subprocess.call(self.cmd_l + [self.aa_jpg])
            process2 = subprocess.call(self.cmd_l + [self.bb_jpg])
            process3 = subprocess.call([ 'convert', self.aa_jpg, '-colorspace', 'Gray', self.aa_grey_jpg ])
            process4 = subprocess.call([ 'convert', self.bb_jpg, '-colorspace', 'Gray', self.bb_grey_jpg ])
                                        # rpi: 'sudo update' + 'sudo apt-get install imagemagick'
            cur_rms = self.rmsdiff(Image.open(self.aa_grey_jpg), Image.open(self.bb_grey_jpg))

            # if abs(rms_a - rms_b) > 2:  # ????????????????????????????????
            # if rms_ > 2:  # ????????????????????????????????
                # print ' \n I N T R U D E R', datetime.now(), '\n'
                # cpy_cmd = 'cp dog*.jpg alarm*' + ''
                # os.popen('cp source.txt destination.txt')
                # sw_alarm = True
        except Exception as e:
            self.logger.info('%s %s', 'ERROR dog_act, subprocess: ', e)

        if 'pi' in platform.node():
            try:
                if GPIO.input(26):
                    sw_intruder = True  # <-----------------------------------------------------
                else:
                    sw_intruder = False
            except Exception as e:
                self.logger.info('%s %s', 'ERROR GPIO: ', e)
                GPIO.cleanup()

        cur_rms = round(cur_rms, 2)
        print 'cur_rms: ', cur_rms, ',  ', self.rmss_idx, ',  ', self.rmss_l_pic_warn

        if len(self.rmss_l) < 10:
            self.rmss_idx += 1
            self.rmss_l.append(cur_rms)
        else:
            avg_rmss_l = round(sum(self.rmss_l) / len(self.rmss_l), 2)
            per = round((cur_rms - avg_rmss_l) / avg_rmss_l * 100, 2)
            print 'avg: ', avg_rmss_l, datetime.now(), sw_intruder, ',  ', per

            if avg_rmss_l * 1.2 < cur_rms:  # and max(rmss_l) * 1.3 < cur_rms:
                self.rmss_l_pic_warn.append(cur_rms)
                if sw_intruder or len(self.rmss_l_pic_warn) == 3:     # <--------------------
                    self.dog_msg = 'cur:' + str(cur_rms) + ' avg:' + str(avg_rmss_l) + ', ' + str(per) + '%'  # str(datetime.now())
                    self.sw_dog_msg = True
                    self.copy_jpgs()
                    del self.rmss_l_pic_warn[0:2]       # remove 2 elements
            else:
                self.rmss_l.pop(0)
                self.rmss_l.append(cur_rms)
                self.rmss_l_pic_warn = []

        # print 'rmss_l: ', self.rmss_l

    #
    def copy_jpgs(self):
        try:
            aa_jpg_new = self.aa_jpg.replace('.jpg', '-' + str(datetime.now()).replace(' ', '-') + '.jpg')
            cmd = 'cp ' + self.aa_jpg + ' ' + aa_jpg_new
            os.popen(cmd)                                # os.popen('cp source.txt destination.txt')
            os.popen(cmd.replace('aa', 'bb'))
            os.popen(cmd.replace('aa', 'dd'))

            self.gd_upload(aa_jpg_new)
            bb_jpg_new = aa_jpg_new.replace('aa', 'bb')
            self.gd_upload(bb_jpg_new)
            dd_jpg_new = aa_jpg_new.replace('aa', 'dd')
            self.gd_upload(dd_jpg_new)

            os.remove(aa_jpg_new)
            os.remove(bb_jpg_new)
            os.remove(dd_jpg_new)
        except Exception as e:
            self.logger.info('%s %s', 'ERROR copy_jpgs: ', e)

    #
    def gd_upload(self, fnam):
        fnam_split = fnam.split('/')[1]
        file_metadata = {'name': fnam_split, 'parents': ['1LupPY42Gk0euH-sQ7NED4jdZ-gUxODvJ']}  # dog
        media = MediaFileUpload(fnam, mimetype='image/jpeg')
        file = self.gd_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        # self.pic_fid_gd_pic_handle = file.get('id')  # chk gd id

    #
    def ssh_act(self):
        cmd1 = ['sudo', 'systemctl', 'enable', 'ssh.service']
        cmd2 = ['sudo', 'systemctl', 'start', 'ssh.service']
        try:
            process = subprocess.call(cmd1)
            print 'enable ssh ok'
            process = subprocess.call(cmd2)
            print 'start ssh ok'
        except Exception as e:
            self.logger.info('%s %s', 'ERROR ssh_act: ', e)






