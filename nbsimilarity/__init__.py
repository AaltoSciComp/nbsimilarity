from ._version import __version__

import argparse
from collections import namedtuple
import sys

import nbformat
import pycode_similar
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def read_file(nb):
    if nb.endswith('.ipynb'):
        with open(nb) as nbf:
            t_nb = nbformat.read(nbf, 4)
        return nb_to_doc(t_nb)
    return(open(nb).read())


def nb_to_doc(nb):
    data = [ ]
    for cell in nb.cells:
        s = cell.source
        if cell.cell_type == 'markdown':
            s = '\n'.join('# '+x for x in s.split('\n'))
            #print(s)
            data.append(s)
        elif cell.cell_type == 'code':
            s = '\n'.join('# '+x if not x or x[0] in '!%' else x for x in s.split('\n'))
            data.append(s)
    return '\n'.join(data)

    #import IPython ; IPython.embed()
    return nb


class Comparer:
    def __init__(self):
        self.docs = [ ]
        self.vecs = [ ]
        self.has_template = False

    def template(self, doc):
        self.has_template = True
        self.t_doc = doc
        self.t_lines = self.t_doc.split('\n')

    def filter_doc(self, doc):
        if hasattr(self, 't_lines'):
            # Remove lines in template
            doc = '\n'.join(x for x in doc.split('\n') if x not in self.t_lines)
        return doc


class Tfidf(Comparer):

    def add(self, doc):
        doc = self.filter_doc(doc)
        print(len(doc.split('\n')))
        self.docs.append(doc)

    def process(self):
        docs = self.docs
        if self.has_template:
            docs = self.docs + [self.t_doc]
        self.vecs = TfidfVectorizer().fit_transform(docs).toarray()
        if self.has_template:
        #print(vecs)
            self.t_vec = self.vecs[-1]
            self.vecs = self.vecs[:-1]

    def sim_template(self):
        sims = [ ]
        for i in range(len(self.docs)):
            s = cosine_similarity([self.t_vec, self.vecs[i]])[0][1]
            sims.append((i, s, ''))
        sims.sort(key=lambda x: x[1], reverse=True)
        return sims

    def sim_all(self):
        sims = [ ]
        for i in range(len(self.docs)):
            for j in range(i+1, len(self.docs)):
                s = cosine_similarity([self.vecs[i], self.vecs[j]])[0][1]
                sims.append((i, j, s, ''))
        sims.sort(key=lambda x: x[2], reverse=True)
        return sims

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--template', '-t')
    parser.add_argument('--compare', '-c', default='Tfidf')
    #parser.add_argument('--template', '-t')
    parser.add_argument('notebooks', nargs='+')
    args = parser.parse_args(argv)
    #print(args)
    comparer = globals()[args.compare]()

    if args.template:
        comparer.template(read_file(args.template))

    names = args.notebooks
    names = filter(lambda x: not x.endswith('~'), names)
    names = list(names)

    for notebook in names:
        comparer.add(read_file(notebook))


        #print(nb)

    #results = pycode_similar.detect([t_doc, *docs], diff_method=pycode_similar.UnifiedDiff, keep_prints=False, module_level=False)
    #print(results)

    comparer.process()

    if comparer.has_template:
        print()
        print("Compare to template")
        sims = comparer.sim_template()
        for i, s, desc in sims:
            print(f"{names[i][-20:]:20}   {s:0.02}")


    print()
    print("Compare all students")
    sims = comparer.sim_all()
    for i, j, s, desc in sims:
        print(f"{names[i][-20:]:20}   {names[j][-20:]:20}   {s:0.02}")
