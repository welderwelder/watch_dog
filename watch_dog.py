# coding: utf-8
import time, sys
import tokenbot                     # .gitignore !
import dfu                          # Data_File_Use: strings constants etc.
import subprocess                   # to run ffmpeg install ffmpeg ? via website+build! + apt

from Msg import Msg
from Robot import Robot
from Dog import Dog

reload(sys)                         # after class-ing: err ascii decode heb str
sys.setdefaultencoding('UTF-8')     # still heb strings log lft->rgt reversed(?)

dfu.setup_logging()                 # https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/


#
# ___________________________________________________________________________
def main():

    running = True

    r = Robot(tokenbot.token_bot)
    dog = Dog()
    m_flow = Msg('flw')
    m_dr = Msg('dr')    #daily route

    lst_id = r.get_f_lst_id()

    while running:
        time.sleep(r.dyn_delay)                 # (0.9)

        r.get_lst_msg_bot()
        if (not r.skippy):
            if r.lst_msg_id > int(lst_id):
                m_flow.init_xtnd(r.lst_msg)

                m_flow.chk_msg_type()
                if m_flow.v_msg_fid != None:
                    m_flow.v_msg_f_pth = r.bot.get_file(m_flow.v_msg_fid)['file_path']
                    m_flow.v_msg_rcgz()

                m_flow.analyze_txt_in_msg()

                r.snd_msg(m_flow.anlz_msg_cht_id, m_flow.cre_msg_txt_new)

                r.upd_f_lst_id()
                lst_id = str(r.lst_msg_id)


        m_dr.daily_route()
        if m_dr.dr_sw_warn:
            r.snd_msg(m_dr.anlz_msg_cht_id, m_dr.cre_msg_txt_new)
            m_dr.dr_sw_warn = False


        if m_flow.sw_dog_act:
            dog.dog_act()
            if dog.sw_dog_msg:
                r.snd_msg(tokenbot.dr_usr_id, dog.dog_msg)
                if m_flow.sw_dogpic:
                    r.snd_photo(tokenbot.dr_usr_id, dog.dd_jpg)
        else:
            dog.rmss_l = []


        if m_flow.sw_ssh:
            dog.ssh_act()
            m_flow.sw_ssh = False



# ___________________________________________________________________________
# ___________________________________________________________________________
if __name__ == "__main__":
        main()
# ___________________________________________________________________________
# ___________________________________________________________________________



