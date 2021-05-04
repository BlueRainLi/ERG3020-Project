
from pracmln import MLN, Database
from pracmln import query, learn
from pracmln.mlnlearn import EVIDENCE_PREDS
import time
from pracmln.utils import locs



class InferenceMachine:
    def __init__(self, mln_path='alarm/mlns/alarm-kreator.mln', db_path='alarm/dbs/query1.db'):
        self.db_path = db_path
        self.mln_path = mln_path

    def inference(self, inference_query='steal,lie'):
        mln = MLN(mlnfile=self.mln_path,
                  grammar='StandardGrammar')
        db = Database(mln, dbfile=self.db_path)
        for method in ['EnumerationAsk'
                       # 'MC-SAT',
                       # 'WCSPInference',
                       # 'GibbsSampler'
                        ]:
            print('=== INFERENCE TEST:', method, '===')
            result = query(queries=inference_query,
                  method=method,
                  mln=mln,
                  db=db,
                  verbose=True,
                  multicore=False).run()
            print(result)

    def learning(self):
        mln = MLN(mlnfile=self.mln_path, grammar='StandardGrammar')
        db = Database(mln, dbfile=self.db_path)
        for method in ('BPLL', 'BPLL_CG', 'CLL'):
            print('=== LEARNING TEST:', method, '===')
            learn(method=method,
                  mln=mln,
                  db=db,
                  verbose=True,
                  multicore=False).run()

    def run_all(self):
        start = time.time()
        try:
            self.inference()
        except:
            print("BUG KILLED")
        # test_inference_taxonomies()

        try:
            print("Learning..")
            # self.learning()
        except:
            print("BUG KILLED")

        print()
        print('all test finished after', time.time() - start, 'secs')


a = InferenceMachine()
a.inference()

