from horizon import Horizon
import base64
from peewee import *
from stellarcoredb import *
from collections import defaultdict
import pprint
import datetime
import requests
pp = pprint.PrettyPrinter(indent=4)


def get_offers(sellingassetcode=None, buyingassetcode=None):
    offers = Offers.select()
    if buyingassetcode is not None and sellingassetcode is not None:
        offers = offers.where((Offers.buyingassetcode==buyingassetcode) & (Offers.sellingassetcode==sellingassetcode))
    if sellingassetcode is not None and buyingassetcode is None:
        offers = offers.where((Offers.sellingassetcode==sellingassetcode) & (Offers.buyingassetcode >> None))
    if buyingassetcode is not None and sellingassetcode is None:
        offers = offers.where((Offers.buyingassetcode==buyingassetcode) & (Offers.sellingassetcode >> None))

    out = []
    for ii in offers:
        outdict = {'amount': ii.amount,
                   'buyingassetcode': ii.buyingassetcode,
                   'buyingassettype': ii.buyingassettype,
                   'buyingassetissuer': ii.buyingissuer,
                   'flags': ii.flags,
                   'lastmodified': ii.lastmodified,
                   'offerid': ii.offerid,
                   'price': ii.price,
                   'priced': ii.priced,
                   'pricen': ii.pricen,
                   'sellerid': ii.sellerid,
                   'sellingassetcode': ii.sellingassetcode,
                   'sellingassettype': ii.sellingassettype,
                   'sellingissuer': ii.sellingissuer}
        out.append(outdict)
        #outdict = { jj:ii.__dict__[jj] for jj in Offers.__dict__.keys() }
    return out

def get_home_domains():
    total_accounts = Accounts.select()
    accounts_with_home_domain = Accounts.select().where(Accounts.homedomain != "")
    domains = defaultdict(int)
    for aa in accounts_with_home_domain:
        print(aa.homedomain)
        domains[aa.homedomain] += 1

    pp.pprint(domains)

    for dd in domains.keys():
        try:
            r = requests.get('https://' + dd + "/.well-known/stellar.toml")
            print(r.raw())
        except requests.exceptions.MissingSchema as e:
            print("Bad domain?")
            print(e)



def decode_tx(tx):
    pass




def get_last_txs(num_txs):
    txs = Txhistory.select().limit(num_txs)
    out = []
    for ii in txs:
        outdict = {'ledgerseq': ii.ledgerseq,
                   'txbody': ii.txbody,
                   'txid': ii.txid,
                   'txindex': ii.txindex,
                   'txmeta': ii.txmeta,
                   'txresult': ii.txresult
                   }
        out.append(outdict)
    return out


def get_tx_for_ledger(ledger_number):
    txs = Txhistory.select().where(Txhistory.ledgerseq == ledger_number).count()
    return txs


def get_accounts():
    total_accounts = Accounts.select().count()
    return total_accounts






if __name__ == '__main__':
    #pp.pprint(get_offers(sellingassetcode="JPY"))
    #pp.pprint(get_accounts())
    #pp.pprint(get_tx_for_ledger(5031910))
    txs = get_last_txs(200)
    pp.pprint(txs)
    #pp.pprint(get_offers(buyingassetcode="JPY"))
    #get_home_domains()

    #pp.pprint([ii.amount, ii.buyingassetcode, ii.buyingassettype, ii.buyingissuer, ii.flags, ii.lastmodified, ii.offerid, ii.price, ii.priced, ii.pricen, ii.sellerid, ii.sellingassetcode, ii.sellingassettype, ii.sellingissuer])

"""
quorums = Scpquorums.select()

for jj in quorums:
    outdict = {'lastledgerseq': jj.lastledgerseq,
               'qset': jj.qset,
               'qsethash': jj.qsethash}

    pp.pprint(outdict)
"""
"""
peers = Peers.select()

for kk in peers:
    outdict = {'ip': kk.ip,
               'nextattempt': kk.nextattempt,
               'numfailures': kk.numfailures,
               'port': kk.port
               }


pp.pprint(outdict)
"""


