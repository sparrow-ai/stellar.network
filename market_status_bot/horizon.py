


import pprint
pp = pprint.PrettyPrinter(indent=4)
import requests


class Horizon(object):

    def __init__(self,url):
        self.base_url = url


    def ledgers(self,cursor=False, limit=False, order=False):
        url = self.base_url + "/ledgers"
        args = {}
        arg_names = ('cursor','limit','order')
        args = { ii:jj for ii,jj in zip(arg_names,(cursor,limit,order)) if jj}
        print("args: {}".format(args))
        r = requests.get(url, params=args)
        resp = r.json()
        return resp

    def accounts(self,acct):
        url = self.base_url + "/accounts/" + acct
        r = requests.get(url)
        pp.pprint(r.json())


    def orderbook(self):
        url = self.base_url + '/orderbook'
        args = {'selling_asset_type':'native',
                'buying_asset_type': 'native'}
        r = requests.get(url, params=args)
        pp.pprint(r.json())
    
    def offers(self,acct):
        url = self.base_url + "/accounts/"+acct
        r = requests.get(url)
        pp.pprint(r.json())
        return r.json()


    def orderbook_details(self, selling_asset_type, 
                          selling_asset_code, selling_asset_issuer, 
                          buying_asset_type,
                          buying_asset_issuer,
                          cursor=None,
                          order='asc',
                          limit=10):

        url = self.base_url + "/order_book"
        args = {'selling_asset_type': selling_asset_type,
                'selling_asset_code': selling_asset_code,
                'selling_asset_issuer': selling_asset_issuer,
                'buying_asset_type': buytin_asset_issuer,
                'cursor': cursor,
                'order': order,
                'limit': limit}
        r = requests.get(url, params=args)
        resp = r.json()
        return resp











if __name__ == '__main__':
    h = Horizon('http://127.0.0.1:8000')
    pp.pprint(h.ledgers())

