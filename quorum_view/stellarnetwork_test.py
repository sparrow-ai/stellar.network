

import pytoml as toml
import networkx as nx
import requests
import pprint
import configparser
from networkx.readwrite import json_graph
import json
pp = pprint.PrettyPrinter(indent=4)
from geolite2 import geolite2 as gip


config =configparser.ConfigParser()
cfg = config.read("quorum_view.cfg")
save_loc = cfg['save-location']['save_root']
sc_cfg = cfg['stellar']['stellar_core_cfg']







#local_url = "http://127.0.0.1:11626"

#r = requests.get(local_url+"/quorum")
#output = r.json()


class StellarNetwork(object):

    def __init__(self):
        self.disagree_graph = nx.DiGraph()
        self.agree_graph = nx.DiGraph()
        self.missing_graph = nx.DiGraph()
        self.fail_with_graph = nx.DiGraph()
        self.node_ids = set([])
        self.num_nodes = len(self.node_ids)
        self.reader = gip.reader()
        with open(sc_cfg,"r") as fh:
            self.toml = toml.load(fh)

        self.node_names = self.parse_names(self.toml)



    def parse_names(self,the_toml):
        names = the_toml['NODE_NAMES']
        outdict = {}
        for ii in names:
            both = ii.split()
            if len(both) > 1:
                common = both[1].strip()
                pk = both[0].strip()
                outdict[common] = pk

        return outdict







    def get_peers(self):
        local_url = "http://127.0.0.1:11626"
        r = requests.get(local_url+"/peers")
        return r.json()['peers']

    def info(self):
        local_url = "http://127.0.0.1:11626"
        url = local_url + "/info"
        r = requests.get(url)
        return r.json()

    def update_nodes(self):
        peers = self.get_peers()
        #print("peers: " + repr(peers))
        #node_ids = ["GDI2VEQCULNQ63WZLX2WPYZ42GORBMX45ICS2TUZHHN5GPODFZGXE3AL"[0:5]]  # self
        node_ids = list(self.node_names.keys())

        node_ids.extend([ pe['id'] for pe in peers ])
        old = None
        new = set(node_ids)
        excluded = []
        while old != new:
            old = new.copy()
            potentials = []
            node_ids = list(new)
            for ii in node_ids:
                q = self.get_quorum(ii)
                try: 
                    le = self.get_most_recent_ledger(q)
                    #print(le)
                except KeyError:
                    print("Can't query data for node: {} \nLeaving out of network.\n\n".format(ii))
                    #potentials = [ pp for pp in potentials if pp!=ii]
                    #node_ids = [ nn for nn in node_ids if nn!=ii]
                    excluded.append(ii)
                    break
                new_peers = self.get_ledger_peers(le)
                if new_peers and new_peers['all'] is not None:
                    #print(new_peers['all'])
                    potentials.extend([ np for np in new_peers['all']])
                    #print("***** potentials ********: {}".format(potentials))
            node_ids.extend(potentials)
            #node_ids = [ nn for nn in node_ids if nn not in excluded ]
            #print("Final node ids: {}".format(node_ids))
            new = set(node_ids)

        self.node_ids = set(new)
        self.num_nodes = len(self.node_ids)


    def get_geo(self, ip):
        loc = self.reader.get(ip)
        return loc

    def get_quorum(self, peer_id):
        peer_id1 = '$' + peer_id
        #print("This is the peer_id1: {}".format(peer_id1))
        local_url = "http://127.0.0.1:11626"
        url = local_url + "/quorum"
        args = {'node': peer_id1, 'compact': False}
        r = requests.get(url, params=args)
        #pp.pprint(r.json())
        #print(r.url)
        if 'exception' in r.json():
            #print("Handling the exception.")
            #print("node id: {}".format(peer_id))
            if peer_id == "GDI2VEQCULNQ63WZLX2WPYZ42GORBMX45ICS2TUZHHN5GPODFZGXE3AL":   # self
                r = requests.get(url)
                #print("My node info: {}".format(r.json()))
                return r.json()

            else:
                peer_id1 = "@" + peer_id[0:5]
                #print("peer_id1: {}".format(peer_id1))
                args = {'node': peer_id1, 'compact': True}
                r = requests.get(url,params=args)
                #pp.pprint(r.url)
                #pp.pprint(r.json())
                return r.json()
        return r.json()



    def get_quorum_intersection(self):
        inter = set(self.node_ids)
        for ii in self.node_ids:
            q = self.get_quorum(ii)
            l = self.get_most_recent_ledger(q)
            p = self.get_ledger_peers(l)
            try:
                qset = p['agree']
                inter.intersection(set(qset))
            except KeyError:
                print("No links!")

        print(inter)


    def get_ledger_peers(self, ledger_q):
        if ledger_q is not None:
            if ledger_q['phase'] == 'expired':
                out_dict = {'disagree': 0, 'agree': 0, 'missing': 0, 'fail_with': 0, 'all':0, 'expired':1}
                return out_dict

            disagree = ledger_q['disagree'] if ledger_q['disagree'] is not None else []
            if 'value' in ledger_q.keys():
                agree = ledger_q['value']['v'] if ledger_q['value'] is not None else []
            else:
                agree = []
            missing = ledger_q['missing'] if ledger_q['missing'] is not None else []
            #print("missing peers: {}".format(missing))
            fail_with = ledger_q['fail_with'] if ledger_q['fail_with'] is not None else []
            all_peers = set(disagree) | set(agree) | set(missing) | set(fail_with)
            #print("all_peers: {}".format(all_peers))
            out_dict = {'disagree': disagree, 'agree': agree, 'missing': missing, 'fail_with': fail_with, 'all': all_peers, 'expired': 0}
            return out_dict
        else:
            return {}

    def get_most_recent_ledger(self, quorum_ret):
        #print("quorum_ret: {}".format(quorum_ret))
        all_slots = sorted(list(quorum_ret['slots']), reverse=True)
        last_slot = [ ii for ii in all_slots if 'hash' in quorum_ret['slots'][ii].keys() ]
        if last_slot:
            self.last_ledger = last_slot[0]
            ledger = quorum_ret['slots'][last_slot[0]]
            return ledger
        else:
            return None


    def update_disagree(self):
        self.update_nodes()
        peers = self.get_peers()
        self.disagree_graph.clear() 
        
        for pe in self.node_ids:
            q = self.get_quorum(pe)
            try: 
                this_id = q['node']
                ledger = self.get_most_recent_ledger(q)
                self.disagree_graph.add_node(this_id,ledger)
                #self.disagree_graph.add_node(this_id)
                disagree = self.get_ledger_peers(ledger)['disagree'] if 'disagree' in self.get_ledger_peers(ledger).keys() else None
            except KeyError:
                disagree = None

            if disagree is not None:
                for jj in disagree:
                    if jj != this_id:
                        self.disagree_graph.add_edge(this_id,jj)
        #print(self.disagree_graph.edges())

    def update_agree(self):
        self.update_nodes()
        self.agree_graph.clear()
        for pe in self.node_ids:
            #print(pe)
            q = self.get_quorum(pe)

            try: 
                this_id = q['node']
                if this_id in self.node_names:
                    pk = self.node_names[this_id]
                else:
                    pk = this_id

                ledger = self.get_most_recent_ledger(q)
                #self.agree_graph.add_node(this_id)
                peers = self.get_ledger_peers(ledger)

                if peers:
                    # Get ip address and then geo_loc
                    ps = self.get_peers()
                    print("This_id: {}".format(this_id))
                    #print("peers: {}".format(ps))
                    for pp in ps:
                        if pp['id'] == this_id:
                            the_ip = pp['ip']
                            geo = self.get_geo(the_ip)
                            # Get coords
                            try:
                                coords = [geo['location']['latitude'], geo['location']['longitude'] ]
                            except:
                                coords = None
                            try: 
                                city = geo['city']['names']['en']
                            except:
                                city = None
                            try: 
                                region = geo['subdivisions'][0]['names']['en']
                            except:
                                region = None
                            try:
                                country = geo['country']['names']['en']        
                            except:
                                country = None

                            if this_id == "sparrow_tw":
                                loc_string = 'Taipei, Taiwan'
                                coords = [25.0330, 121.5654]
                            elif city and region:
                                loc_string = city + ", " + region
                            elif city:
                                loc_string = city
                            elif region:
                                loc_string = region
                            elif country:
                                loc_string = country
                            elif this_id == "tempo.eu.com":
                                loc_string = "Frankfurt, Germany"
                                coords = [50.1109,  8.6821]
                            else:
                                loc_string = None
                    if this_id == 'dzham':
                        loc_string = 'Des Moines, Iowa'
                        coords = [41.6005, -93.6091]
                    if this_id == "tempo.eu.com":
                        loc_string = "Frankfurt, Germany"
                        coords = [50.1109, 8.6821]

                    if loc_string and coords :

                        self.agree_graph.add_node(this_id,ledger=ledger, expired=peers['expired'], public_key = pk, loc = loc_string, lat = coords[0], lon=coords[1]) 
                    else:
                        self.agree_graph.add_node(this_id,ledger=ledger, expired=peers['expired'], public_key = pk)


                    agree = peers['agree'] if 'agree' in peers.keys() else None
                    disagree = peers['disagree'] if 'disagree' in peers.keys() else None
                    missing = peers['missing'] if 'missing' in peers.keys() else None
                else:
                    self.agree_graph.add_node(this_id, ledger=None, expired=True, public_key=pk)
                    agree = []
                    missing = []
                    disagree = []

            except KeyError as e:
                print("Made it into except: " + repr(e))
                agree = []
                missing = []
                disagree = []

            for jj in agree:
                if jj == this_id:
                    #print("self link!")
                    pass
                else:
                    if jj in disagree:
                        #print("This node disagrees.")
                        self.agree_graph.add_edge(this_id,jj, disagree=1, missing=0)
                    elif jj in missing:
                        #print("This node is missing")
                        self.agree_graph.add_edge(this_id,jj, missing=1, disagree=0)
                    else:
                        self.agree_graph.add_edge(this_id, jj, missing=0, disagree=0)

        #print(self.agree_graph.node("sdf_watcher1"))
        #print(self.agree_graph.edges()) 
        

    def update_missing(self):
        self.update_nodes()
        self.missing_graph.clear()
        for pe in self.node_ids:
            q = self.get_quorum(pe)
            try:
                this_id = q['node']
                ledger = self.get_most_recent_ledger(q)
                self.agree_graph.add_node(this_id,ledger)
            #self.agree_graph.add_node(this_id)
                missing = self.get_ledger_peers(ledger)['missing'] if 'missing' in self.get_ledger_peers(ledger).keys() else None
            except KeyError:
                missing = None

            if missing is not None:
                for jj in missing:
                    if jj != this_id:
                        self.missing_graph.add_edge(this_id,jj)

        #print(self.missing_graph.edges()) 

    def update_fail_with(self):
        self.update_nodes()
        self.fail_with_graph.clear()
        for pe in self.node_ids:
            q = self.get_quorum(pe)
            try: 
                this_id = q['node']
                ledger = self.get_most_recent_ledger(q)
                self.fail_with_graph.add_node(this_id, ledger)
                #self.fail_with_graph.add_node(this_id)
                fail_with_peers = self.get_ledger_peers(ledger)
                fail_with = fail_with_peers['fail_with'] if 'fail_with' in fail_with_peers else None
            except KeyError:
                fail_with = None

            if fail_with is not None:
                for jj in fail_with:
                    if jj != this_id:
                        self.fail_with_graph.add_edge(this_id,jj)

        #print(self.fail_with_graph.edges())

    def network_statistics(self,nw):
        # Calculate network statistics

        num_nodes = nx.number_of_nodes(nw)
        #print("number of nodes: {}".format(num_nodes))

        nodes = nx.nodes(nw)
        degree = nx.degree(nw)
        #print("degree: {}".format(degree))

        #deg_hist = nx.degree_histogram(nw)
        #print("degree_histogram: {}".format(deg_hist))
    
        out = {'num_nodes': num_nodes,
                'degree': degree,
                'ledger': self.last_ledger}

        return out


    def update_all_statistics(self):
        with open(save_loc + "agree_stats.json","w") as fh:
            agreed_stats = self.network_statistics(self.agree_graph) 
            fh.write(json.dumps(agreed_stats))
        with open(save_loc + "disagree_stats.json","w") as fh:
            disagreed_stats = self.network_statistics(self.disagree_graph) 
            fh.write(json.dumps(disagreed_stats))

        with open(save_loc + "fail_with_stats.json","w") as fh:
            fail_with_stats = self.network_statistics(self.fail_with_graph) 
            fh.write(json.dumps(fail_with_stats))
        with open(save_loc + "missing_stats.json","w") as fh:
            missing_stats = self.network_statistics(self.missing_graph) 
            fh.write(json.dumps(missing_stats))


    def get_all_statistics(self):
        agreed_stats = self.network_statistics(self.agree_graph) 
        disagreed_stats = self.network_statistics(self.disagree_graph) 
        fail_with_stats = self.network_statistics(self.fail_with_graph) 
        missing_stats = self.network_statistics(self.missing_graph) 
        out = {'agree': agreed_stats, 'disagree': disagreed_stats, 'fail_with': fail_with_stats, 'missing': missing_stats}
        return out



    def get_network_json(self,graph):
        data = json_graph.node_link_data(graph)
        return data



    def update_all(self):
        self.update_missing()
        self.update_fail_with()
        self.update_agree()
        self.update_disagree()

    def export_gexf(self, graph, filename):
        nx.write_gexf(graph, filename)


    def export_json(self, graph, filename):
        data = json_graph.node_link_data(graph)
        with open(filename, 'w') as fh:
            fh.write(json.dumps(data))



if __name__ == '__main__':
    s = StellarNetwork()
    #pp.pprint(s.info())
    #pp.pprint(s.get_peers())
    #s.update_nodes()
    s.update_all()
    #s.get_quorum_intersection()
    #print(s.info())
    #print(s.get_geo('104.196.96.245'))
    #ids = ["lab1", "lab2", "lab3", "donovan", "nelisky1", "nelisky2", "jianing", "eno", "w00kie", "moni", "dzham", "ptarasov", "tempo.eu.com", "unknown"]
    #for ii in ids:
    #    s.get_quorum(ii)
    #print("Node ids: {}".format(s.node_ids))
    s.export_json(s.fail_with_graph, save_loc + "fail_with.json")
    s.export_json(s.disagree_graph, save_loc + "disagree.json")
    s.export_json(s.agree_graph, save_loc + "agree.json")
    s.export_json(s.missing_graph, save_loc + "missing.json")
    s.update_all_statistics()
    #print(s.node_ids)
