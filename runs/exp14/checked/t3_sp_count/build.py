"""Build t3_sp_count: count shortest paths from s to t."""
import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, TRIE, ADJ, EDGE, INF

def build_t3_sp_count():
    P = Program()
    
    lg = P.lg()
    empty_adj = P.empty_adj()
    adj = P.adjacency()
    sssp_prim = P.sssp("sp")
    get_d = P.get("gt")
    
    def step(d, L, g, u, v):
        L1, L2 = d.fanout(L, 2)
        g2 = d.call(adj, G=g, u=u, L=L1, v=v, w=0)
        return L2, g2
    
    def fin(d, L, g):
        d.erase(L)
        return g
    
    w = P.stream("w", step, fin, state=[("L", DEPTH), ("g", ADJ)], elem=EDGE)
    
    def prog(d, n, s_val, t_val, edges):
        def empty(b, s, t, es):
            b.erase(s)
            b.erase(t)
            b.erase(es)
            return 0
        
        def nonempty(b, nm1, s, t, es):
            nm1a, nm1b = b.fanout(nm1, 2)
            n = b.op(nm1b, "+", 1)
            
            L = b.call(lg, x=nm1a)
            L1, L2, L3, L4 = b.fanout(L, 4)
            
            G = b.call(w, list=es, init=(L1, b.call(empty_adj, L=L2)))
            
            D = b.call(sssp_prim, n=n, s=s, L=L3, G=G)
            
            dist_t = b.call(get_d, t=D, k=t, L=L4)
            
            is_reachable = b.op(dist_t, "!", INF)
            
            return is_reachable
        
        return d.branch(n, empty, nonempty, s_val, t_val, edges)
    
    P.prog("t3_sp_count", prog)
    P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
    print("built net.hvm")

if __name__ == "__main__":
    build_t3_sp_count()
