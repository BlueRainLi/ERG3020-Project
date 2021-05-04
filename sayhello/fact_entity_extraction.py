from allennlp.predictors.predictor import Predictor
import os
import sys
from sayhello import app
from nltk.stem.wordnet import WordNetLemmatizer
from sayhello.commonDataProcess import CommonDatabase, CommonFunction


class OpenInfoPredictor:
    def __init__(self):
        # self.source_tgz = os.path.dirname(app.root_path) + "/sayhello/source/openie-model.2020.03.26.tar.gz"
        self.source_tgz = "https://storage.googleapis.com/allennlp-public-models/openie-model.2020.03.26.tar.gz"
        # print(source_tgz)
        # print("Start Loading")
        self.predictor = Predictor.from_path(self.source_tgz)
        # print("End Loading")

    def query(self, comment):
        output = self.predictor.predict(sentence=comment)
        return output


class EntailmentPredictor:
    def __init__(self):
        # self.source_tgz = os.path.dirname(app.root_path) + "/sayhello/source/decomposable-attention-elmo-2020.04.09.tar.gz"
        self.source_tgz = "https://storage.googleapis.com/allennlp-public-models/decomposable-attention-elmo-2020.04.09.tar.gz"
        self.predictor = Predictor.from_path(self.source_tgz)

    def query(self, pre, hyp):
        output = self.predictor.predict(premise=pre,hypothesis=hyp)['label']
        return output


class NameEntityPredictor:
    def __init__(self):
        # self.source_tgz = os.path.dirname(app.root_path) + "/sayhello/source/ner-elmo.2021-02-12.tar.gz"
        self.source_tgz = "https://storage.googleapis.com/allennlp-public-models/ner-elmo.2021-02-12.tar.gz"
        self.predictor = Predictor.from_path(self.source_tgz)
        print('load finish ner-elmo.2021-02-12.tar.gz')

    def query(self, comment):
        output = self.predictor.predict(sentence=comment)
        return output


class UserPredict:
    def __init__(self, debug_mode=False):
        if not debug_mode:

            self.openInfoEngine = OpenInfoPredictor()
            # self.entailEngine = EntailmentPredictor()
            self.nameEntityEngine = NameEntityPredictor()

        self.commonDB = CommonDatabase("nen.cmdata")
        self.funcDB = CommonFunction("func.cmdata")

        self.verb_database = []
        self.entity_database_per = []
        self.entity_database_org = []
        self.entity_database_loc = []

    def query(self, comment):
        result_dict = self.openInfoEngine.query(comment)
        print(result_dict)

        # Determine the principal verb
        tags_0 = []
        n = 0
        for verb_dict in result_dict["verbs"]:
            # print(verb_dict)
            description = verb_dict['description']
            tags = verb_dict['tags']
            # print(tags)
            # print("determine the principal according to the number of 0 tags")
            this = 0
            for i in tags:
                # print(i)
                if i == "O":
                    this += 1
            # print(this)
            tags_0.append(this)
            n += 1
        # print(tags_0)

        # We want the minimal number of tag O
        index_desire = tags_0.index(min(tags_0))
        best_verb_dict = result_dict["verbs"][index_desire]
        print("*********************")
        print(best_verb_dict)
        print("*********************")

        # Principal determined!

        self.verb_database.append(best_verb_dict['verb'])

        # To extract the structure of this sentence:
        # Input : '[ARG0: Tom] [V: accuses] [ARG1: Bob] [ARG2: of stealing the money] .'
        string = best_verb_dict['description']
        stack = []
        switch = False
        this_word = ''
        for i in string:
            if i == '[':
                switch = True
            elif i == ']':
                switch = False
                stack.append(this_word)
                this_word = ''
            elif switch:
                this_word += i
            else:
                pass
        string_list = stack
        # Output: ['ARG0: Tom', 'V: accuses', 'ARG1: Bob', 'ARG2: of stealing the money']

        # Convert the verb into standard form.
        verb_standard = WordNetLemmatizer().lemmatize(best_verb_dict['verb'], 'v')

        this_atom_clauses = {'verb': verb_standard, 'neg': False, 'args': None}

        """        arg_list = []
        for i in string_list:
            if 'NEG' in i:
                this_atom_clauses['neg'] = True
            elif 'ARG' in i:
                obj = i.split(': ')[1]
                arg_list.append(obj)
        # print(arg_list)
        # Process the args:
        this_atom_clauses['args'] = arg_list
        # print(this_atom_clauses)"""

        # ...

        this_atom_clauses = {'verb': verb_standard, 'neg': False, 'args': None, 'grammar': None}

        arg_list = {}
        orders = []
        for i in string_list:
            if 'NEG' in i:
                this_atom_clauses['neg'] = True
                orders.append('NEG')
            elif 'ARG' in i:
                ref = i.split(': ')[0]
                obj = i.split(': ')[1]
                orders.append(ref)
                arg_list[ref] = obj
            elif 'V' in i:
                obj = i.split(': ')[1]
                orders.append('V')
        print(arg_list)
        print(orders)

        # arg_list = {'ARG0': 'Jerry', 'ARG2': 'Tom', 'ARG1': 'that he wanted to fuck him'}

        this_atom_clauses['args'] = arg_list
        this_atom_clauses['grammar'] = orders

        print(this_atom_clauses)

        # ...

        final_result = False
        entity_result_list = []

        for i in this_atom_clauses['args'].keys():
            j = this_atom_clauses['args'][i]
            result = self.entity_processing(j)
            entity_result_list.append(result)
            # print(result)
            if result:
                final_result = True

        if not final_result:
            print('This may not be a fact')
            return False

        this_atom_clauses_dict = this_atom_clauses

        # Add suffix
        for i in range(len(arg_list)):
            # print(arg_list)
            if not entity_result_list[i]:
                args_split = arg_list[list(arg_list.keys())[i]].split(' ')
                # print(args_split)
                # print(this_atom_clauses_dict['verb'])
                this_list = [this_atom_clauses_dict['verb']] + args_split
                # print(this_list)
                this_atom_clauses_dict['verb'] = '_'.join(this_list)
                # print(this_atom_clauses_dict['verb'])

        # Remove the False arguments
        new_list = []
        no_false_list = []
        for i in range(len(arg_list)):
            a = arg_list[list(arg_list.keys())[i]]
            b = entity_result_list[i]
            if b:
                no_false_list.append(b)
                new_list.append(a)

        this_atom_clauses['args'] = new_list

        atom_clause = ''
        if this_atom_clauses_dict['neg']:
            atom_clause += '!'
        atom_clause = atom_clause + this_atom_clauses_dict['verb'] + '(' + ','.join(this_atom_clauses_dict['args']) + ')'
        print(this_atom_clauses_dict)

        return this_atom_clauses_dict, atom_clause, entity_result_list, this_atom_clauses['args'], no_false_list

    def entity_processing(self, arg):

        tag_result = self.nameEntityEngine.query(arg)['tags']
        print(tag_result)
        result_per = True
        result_org = True
        result_loc = True

        for i in tag_result:
            if 'PER' not in i:
                result_per = False
                break
        if result_per:
            self.entity_database_per.append(arg)
            return 'PER'
        for i in tag_result:
            if 'ORG' not in i:
                result_org = False
                break
        if result_org:
            self.entity_database_per.append(arg)
            return 'ORG'
        for i in tag_result:
            if 'LOC' not in i:
                result_loc = False
                break
        if result_loc:
            self.entity_database_per.append(arg)
            return 'LOC'
        return False

    def breakdown(self, comment):
        if "or" in comment:
            pass

        else:
            pass


"""test = UserPredict(True)
# print(test.query("Tom accuses Bob."))
test.query("Tom does not accuse Bob of stealing the money.")



"""