import socket
import time
import dalek as Dalek


kai = Dalek.Dalek()


ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.bind(("10.0.0.7", 6388))
#ss.bind((socket.gethostname(), 6388))
ss.listen(5)
kai.doCommand("eye on")
kai.doCommand("say ah-way-ting <or->ders")
kai.doCommand("eye off")
(cs, addr) = ss.accept()
kai.doCommand("eye on")
kai.doCommand("say en-ah-me dee-<tech-ted. in-true-der-ah->lert. in-true-der-ah->lert")
time.sleep(1.5)
kai.doCommand("fire")
time.sleep(1.5)
kai.doCommand("say en-ah-me has been dee-<stroyed")
kai.doCommand("eye off")
kai.doCommand("reset")
cs.close()
ss.close()
kai.doCommand("exit")
exit()

