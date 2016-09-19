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


geo_defaults = {'sdf_watcher3': {'geo': 'Ashburn, Virginia, U.S.',
                                 'version': 'v0.5.0-2-g676719e'},
                'sdf_watcher1': {'geo': 'Ashburn, Virginia, U.S.',
                                 'version': 'v0.5.0-2-g676719e'},
                "GARR42FIQNK6V5BSQ5H6AXWTD3JBPBMGOWIXUV65B2SOQSCUAKBNGXYK": {'geo': 'Japan', 'version': 'v0.5.0-21-g6d8b27c'},
                'telindus': {'geo': 'Esch-sur-Alzette, District de Luxembourg, Luxembourg', 'version': "v0.5.0-37-g6f07377"},
                "eno": {'geo': 'San Francisco, California, United States', 'version': 'v0.5.0-7-g19f2905'},
                "sparrow_tw": {'geo': "Taipei, Taiwan", 'version': 'v0.5.0-20-gd5dfd5b'},
                "nelisky1": {'geo': "Amsterdam, North Holland, Netherlands", 'version': 'v0.5.0-36-g9905cb2'},
                "nelisky2": {'geo': "Faro, Portugal", 'version': 'v0.5.0-36-g9905cb2'},
                "jianing": {'geo': "Changsha, Hunan, China", 'version': 'v0.5.0-7-g19f2905'},
                "sdf_watcher2": {'geo': 'Ashburn, Virginia, U.S.', 'version': 'v0.5.0-2-g676719e'},
                "moni": {'geo': "Espoo, Uusimaa, Finland", 'version': 'v0.5.0-6-g1d3f687'},
                "dzham": {'geo': "Des Moines, Iowa, U.S.", 'version': 'v0.5.0-6-g1d3f687'},
                "fuxi": {'geo': "Tokyo, Tokyo, Japan", 'version': 'v0.5.0-21-g6d8b27c'},
                "huang": {'geo': "Hangzhou, Zhejiang, China", 'version': 'v0.5.0-21-g6d8b27c'},
                "nezha": {'geo': "Beijing, Beijing, China", 'version': 'v0.5.0-6-g1d3f687-dirty'},
                "SnT.Lux": {'geo': "Leudelange, District de Luxembourg, Luxembourg", 'version': "v0.5.0-33-g05bd79c"},
                "tempo.eu.com": {"geo": "Frankfurt am Main, Hesse, Germany", "version": "v0.5.0-7-g19f2905"}
        }



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
        print(new)
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


    def get_geo(self, ip, the_name):
        loc = self.reader.get(ip)
        geo = loc

        try:
            city = geo(the_ip)['city']['names']['en']
        except:
            city = None
        try: 
            region = geo(the_ip)['subdivisions'][0]['names']['en']
        except:
            region = None
        try:
            country = geo(the_ip)['country']['names']['en']        
        except:
            country = None

        # If one of city, region or country is not None then use this data
       
        temp_string = [ ii for ii in [city, region, country] if ii is not None ]
        if temp_string:
            print(temp_string)
            loc_string = ", ".join(temp_string)
        else:
            loc_string = geo_defaults[the_name['id']]['geo']
            print("geo_defaults")
            print(geo_defaults[the_name['id']]['geo'])
        
        print(loc_string)

        return loc_string

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


                print("??????????  peers  ???????????")
                print(peers)

                if peers:
                    # Get ip address and then geo_loc
                    ps = self.get_peers()
                    this_one = [ pp for pp in ps if pp['id'] == this_id ]
                    loc_string = ""
                    if this_one:
                        the_ip = this_one[0]['ip']
                        loc_string = self.get_geo(the_ip, this_one[0])
                       

                    ver = [ ii for ii in self.get_peers() if ii['id'] == this_id]
                    print("ID: {}, Version: {}".format(this_id,ver))
                    if ver:
                        version = ver[0]['ver']
                    else:
                        version = ""

                    self.agree_graph.add_node(this_id,ledger=ledger, expired=peers['expired'], public_key = pk, loc = loc_string, version=version)


                    agree = peers['agree'] if 'agree' in peers.keys() else None
                    disagree = peers['disagree'] if 'disagree' in peers.keys() else None
                    missing = peers['missing'] if 'missing' in peers.keys() else None
                else:
                    self.agree_graph.add_node(this_id, ledger=None, expired=True, public_key=pk)
                    agree = []
                    missing = []
                    disagree = []

            except KeyError as e:
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
    #for ii in ids:
    #s.get_quorum("SnT.Lux")
    #print("Node ids: {}".format(s.node_ids))
    s.export_json(s.fail_with_graph, save_loc + "fail_with.json")
    s.export_json(s.disagree_graph, save_loc + "disagree.json")
    s.export_json(s.agree_graph, save_loc + "agree.json")
    s.export_json(s.missing_graph, save_loc + "missing.json")
    s.update_all_statistics()
    #print(s.node_ids)
