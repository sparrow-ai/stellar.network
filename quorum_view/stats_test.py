from stellarnetwork import StellarNetwork


s = StellarNetwork()
s.update_all()

s.network_statistics(s.agree_graph)
