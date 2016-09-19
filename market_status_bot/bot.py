import time
import json
from slackclient import SlackClient
from peewee import *
import threading as th
import requests
import pprint
import stellarnetwork
import db_explore as db
pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict



import stellarnetwork


class Bot1(object):

    def __init__(self,token):
        self.client = SlackClient(token)
        #self.user = 'U1KFBF9SN'
        self.user = 'U1N703XRP'
        #self.user = 
        self.s = stellarnetwork.StellarNetwork()

    def _send_to_slack(self,msg):
        #self.client.api_call("chat.postMessage",text=msg,channel="G1KF0R3PH",type="message",id=1)
        json_att = json.dumps([msg])
        self.client.api_call("chat.postMessage",channel="C04FCJXG9",parse="full",attachments=json_att)

    def process_message(self,msg):
            #self.client.rtm_send_message('testing',json_msg)
            #self.client.rtm_send_message('testing',fut.result())
        for mm in msg:
            print(mm)
            if 'text' in mm and 'user' in mm:
                if 'user' != self.user:
                    self.parse_message(mm['text'])
            #if 'type' in mm and mm['type'] == 'message' and 'user' in mm and mm['user'] != self.user:
            #    print(mm)
                #self.send_to_agents(self.rd_requester,mm['text'])
            #    self.send_to_agents(self.wne_requester,mm['text'])
    


    def nodes(self):
        self.s.update_nodes()
        node_ids = self.s.node_ids
        node_dict = {}
        for nn in node_ids:
            if len(nn) > 40:
                name = "@" + nn[0:6]
            else:
                name = nn
            ans = self.s.get_quorum(nn)
            if 'exception' in ans:
                node_dict[name] = 'missing'
            else:
                ledger = self.s.get_most_recent_ledger(ans)
                if ledger is None:
                    node_dict[name] = 'missing'
                else:
                    node_dict[name] = 'agree'

        num_nodes = len(self.s.node_names)
        items = list(node_dict.items())
        sorted_items = sorted(items, key=lambda v: v[1])
        node_status = "\n".join(["*{}*: _{}_".format(ii,jj) for ii,jj in sorted_items])
        text = "\n*Ledger:* {}".format(self.s.last_ledger) +  "\n\n(*Node name*: _status_)\n" +  node_status


        att = {}
        att['title'] = "Nodes: {}".format(num_nodes)
        att['title_link'] = "http://stellar.network"
        att['text'] = text
        att['color'] = "#000"
        att['fallback'] = pp.pformat(node_dict)
        att['footer'] = "http://stellar.network"
        att['ts'] = int(time.time())
        #att['author_name'] = "stellar-core"
        att['mrkdwn_in'] = ['text', 'title', 'footer','author']
        self._send_to_slack(att)
        return None






    def quorum(self,node_name):
        ans = self.s.get_quorum(node_name)
        if 'exception' in ans:
            att = {}
            att['title'] = "Error"
            att['title_link'] = "http://stellar.network"
            att['text'] = "_I_ _thought_ _that_ _you_ _asked_ _me_ _about_ _a_ _node_ _named_ `{}`, _but_ _stellar-core_ _returned_ `{}`".format(node_name, repr(ans))
            att['color'] = "#ff0000"
            att['fallback'] = pp.pformat(ans)
            att['footer'] = "http://stellar.network"
            att['ts'] = int(time.time())
            #att['author_name'] = "stellar-core"
            att['mrkdwn_in'] = ['text', 'title', 'footer','author']
            self._send_to_slack(att)
            return None

        ledger = self.s.get_most_recent_ledger(ans)
        if node_name in self.s.node_names:
            pk = self.s.node_names[node_name]
        else:
            pk = node_name

        if ledger is None:

            att = {}
            att['title'] = "Node: {}".format(ans['node'])
            att['title_link'] = "http://stellar.network"
            att['text'] = "*Public Key:* {}\n*Status:* _missing_".format(pk)
            att['color'] = "#000"
            att['fallback'] = pp.pformat(ans)
            att['footer'] = "http://stellar.network"
            att['ts'] = int(time.time())
            #att['author_name'] = "stellar-core"
            att['mrkdwn_in'] = ['text', 'title', 'footer','author']
            self._send_to_slack(att)
            return None

        att = {}
        if ledger['missing']:
            miss = ", ".join(ledger['missing'])
        else:
            miss = ""
        qset = ", ".join(ledger['value']['v'])
        fw = ", ".join(ledger['fail_with'])
        att['title'] = "Node: {}".format(ans['node'])
        att['title_link'] = "http://stellar.network"
        att['color'] = "#000"
        att['text'] = "*Ledger:* {}\n" \
                      "*Public Key:* {}\n" \
                      "*Quorum Set:* {}\n" \
                      "*Missing:* {}\n" \
                      "*Fail with:* {}".format(self.s.last_ledger,
                                               pk,
                                               qset,
                                               miss,
                                               fw)
        att['fallback'] = pp.pformat(ans)
        att['footer'] = "http://stellar.network"
        att['ts'] = int(time.time())
        #att['author_name'] = "stellar-core"
        att['mrkdwn_in'] = ['text', 'title', 'footer','author']
        self._send_to_slack(att)


    def send_error(self,error_text):
        att = {}
        att['title'] = "_Error_"
        att['title_link'] = "http://stellar.network"
        att['color'] = "#000"
        att['text'] = "_{}_".format(error_text)
        att['fallback'] = error_text
        #att['footer'] = "http://stellar.network"
        att['ts'] = int(time.time())
        #att['author_name'] = "stellar-core"
        att['mrkdwn_in'] = ['text', 'title', 'footer','author']
        self._send_to_slack(att)
        return None

    def parse_message(self,text):
        tokens = text.split()
        if "?nodes" in [ii.lower() for ii in tokens]:
            self.nodes()


        if "?node" in tokens:
            idx = tokens.index('?node')
            try: 
                node_name = tokens[idx + 1]
                self.quorum(node_name)
            except IndexError:
                self.send_error("Please enter a node name (e.g. ?node sdf_watcher1)")

        if "?offers" in tokens:
            idx = tokens.index('?offers')
            try:
                buying_asset_code = tokens[idx + 1].upper()
                selling_asset_code = tokens[idx + 2].upper()
            except IndexError:
                self.send_error("Please enter two asset names (e.g. ?offers XLM JPY)")
                return None

            self.offers(selling_asset_code, buying_asset_code)


        if "?book" in tokens:
            idx = tokens.index('?book')
            try: 
                buying_asset_code = tokens[idx + 1].upper()
                selling_asset_code = tokens[idx + 2].upper()
            except:
                self.send_error("Please enter two asset names (e.g. ?book XLM XRP)")
                
            self.offers(selling_asset_code, buying_asset_code)
            self.offers(buying_asset_code, selling_asset_code)


    def build_orderbook(self,offers):
        ob = defaultdict(int)
        buyingasset = offers[0]['buyingassetcode']
        sellingasset = offers[0]['sellingassetcode']
        for oo in offers:
            ob[oo['price']] += oo['amount']
        return ob

    def offers(self, selling_asset_code=None, buying_asset_code=None):
        if buying_asset_code == 'XLM':
            offers = db.get_offers(selling_asset_code, None)
        elif selling_asset_code == 'XLM':
            offers = db.get_offers(None, buying_asset_code)
        else:
            offers = db.get_offers(selling_asset_code, buying_asset_code)
        if offers:
            ob = self.build_orderbook(offers)
            textout = "\n".join(["*{}:* {}".format(oo,ob[oo]) for oo in sorted(list(ob.keys())) ])
            att = {}
            att['title'] = "Offers: {} (buy) <-- {} (sell)".format(buying_asset_code, selling_asset_code)
            att['title_link'] = "http://stellar.network"
            att['color'] = "#000"
            att['text'] = textout
            att['fallback'] = pp.pformat(offers)
            #att['footer'] = "http://stellar.network"
            att['ts'] = int(time.time())
            #att['author_name'] = "stellar-core"
            att['mrkdwn_in'] = ['text', 'title', 'footer','author']
            self._send_to_slack(att)
        else:
            att = {}
            att['title'] = "Offers: {} (buy) <-- {} (sell)".format(buying_asset_code, selling_asset_code)
            att['title_link'] = "http://stellar.network"
            att['color'] = "#000"
            att['text'] = "_No_ _offers_ _found_"
            att['fallback'] = "No offers found"
            #att['footer'] = "http://stellar.network"
            att['ts'] = int(time.time())
            #att['author_name'] = "stellar-core"
            att['mrkdwn_in'] = ['text', 'title', 'footer','author']
            self._send_to_slack(att)


    def _listen(self):
        if self.client.rtm_connect():
            #self.channels = self.client.server.channels.find('testing')
            #print(self.channels)
            while True:
                msg = self.client.rtm_read()
                self.process_message(msg)
                #time.sleep(1)





    def run(self):
        self.listen_thread = th.Thread(target=self._listen)
        self.listen_thread.start()


if __name__ == '__main__':
    token = "xoxb-56238133873-4IoaFLR9hX6SvNXdXmsxJTXN"
    b = Bot1(token)
    b.run()
