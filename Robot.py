import telegram
from datetime import datetime
import dfu
from telegram import ParseMode
import logging
import os

cnfg_file = "cnfg.txt"

# ___________________________________________________________________________
class Robot:
    def __init__(self, tokn):
        self.logger = logging.getLogger(__name__)
        self.token = tokn
        self.bot = telegram.Bot(token=self.token)
        self.logger.info("bot init: " + str(self.bot))
        self.dyn_delay = 0.9

    # def get_bot(self):
    #     return self.bot

    #
    def get_lst_msg_bot(self):
        # try:
        #     data = urllib.urlopen("https://www.google.com")
        # except e:
        #     self.logger.info('get_lst_msg_bot: NO NETWORK')
        #     self.logger.info(e)

        self.skippy = True
        try:
            # self.lst_msg = self.bot.get_updates()[-1].message     # take whole buffer(srvr_max=100) and take last.
            self.lst_msg = self.bot.get_updates(-1)[0].message      # 'forgets' all but last!
            self.lst_msg_id = self.lst_msg.message_id
            self.skippy = False
            self.dyn_delay = 0.9
        except telegram.error.TimedOut:
            print dfu.str_time_out.format(datetime.now())
            self.dyn_delay = 5
        except IndexError:
            print dfu.str_idx_err.format(datetime.now())
            self.dyn_delay = 10
        except Exception as e:
            self.logger.info('get_lst_msg_bot:')
            self.logger.info(e)


    #
    def snd_msg(self, cht_id_to, msg_txt_new):
        try:
            self.bot.send_message(chat_id=cht_id_to, text=msg_txt_new,
                                  parse_mode=ParseMode.HTML)
        except Exception as e:
            self.logger.info('snd_msg:')
            self.logger.info(e)

    #
    def get_f_lst_id(self):
        try:                                    # if os.path.exists(cnfg_file):
            f = open(cnfg_file, "r")
            self.f_rd_ln = f.readline()
            self.logger.info("get_f_lst_id: " + str(self.f_rd_ln))
            f.close()
        except Exception as e:
            self.logger.exception(e)

        return self.f_rd_ln

    #
    def upd_f_lst_id(self):
        try:
            f = open(cnfg_file, "r+")           # r+ The stream is positioned at the beginning of file  # f.seek(0)
            f.write(str(self.lst_msg_id) + "\n")
            self.logger.info("upd_f_lst_id: " + str(self.lst_msg))
            f.close()
        except Exception as e:
            self.logger.exception(e)
            sys.exit()                          # stop run - erroneous upd but level='info'


    #
    def snd_photo(self, cht_id_to, i_pic_fnam):
        try:
            if os.path.isfile(i_pic_fnam):
                self.bot.send_photo(chat_id=cht_id_to, photo=open(i_pic_fnam, 'rb'))  # open gets fid
                #:caption ----> potentioal field
                # os.remove(i_pic_fnam)
            else:
                self.bot.send_message(chat_id=cht_id_to, text='No photo')
        except Exception as e:
            self.logger.info('%s %s', 'ERROR snd_photo: ', e)


