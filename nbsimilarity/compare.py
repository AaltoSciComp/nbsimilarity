import argparse
import collections
from itertools import product
import logging
import os
import sys

import nbformat
import pycode_similar
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm, trange

from .util import remove_common_parts

LOG = logging.getLogger(__name__)



def read_file(nb):
    """Read a file, converting if necessary

    Wrapper to convert notebooks to plain Python files.
"""
    if nb.endswith('.ipynb'):
        with open(nb) as nbf:
            t_nb = nbformat.read(nbf, 4)
        return nb_to_doc(t_nb)
    return(open(nb).read())



def nb_to_doc(nb):
    """Convert .ipynb data to text
    """
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

    return nb



class Comparer:
    no_filter_lines = False
    def __init__(self):
        self.docs = [ ]
        self.vecs = [ ]
        self.has_template = False

    def template(self, doc):
        """Set the template document"""
        self.has_template = True
        self.t_doc = doc
        self.t_lines = self.t_doc.split('\n')

    def add(self, doc):
        """Add new document to the list"""
        doc = self.filter_doc(doc)
        LOG.debug('document length: %s', len(doc.split('\n')))
        self.docs.append(doc)

    def filter_doc(self, doc):
        """Filter a document, as it is added"""
        if ('RemoveDuplicateLines' in FILTERS
            and hasattr(self, 't_lines')
            and not self.no_filter_lines):
            # Remove lines in template
            doc = '\n'.join(x for x in doc.split('\n') if x not in self.t_lines)
        return doc

    def process(self):
        """Run once, to do any necessary computation"""
        pass

    def sim_template(self):
        raise NotImplementedError("Must be defined in subclass")
        #return [
        #    doc1_similarity_to_template,
        #    doc2_similarity_to_template]
    def sim_all(self):
        raise NotImplementedError("Must be defined in subclass")
        #return [
        #    (0, 1, similarity_01),
        #    (0, 2, similarity_02),
        #    (1, 2, similarity_12),
        #    ]



class Tfidf(Comparer):
    """Using a tf-idf algorithm

    state: unverified
    """
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
        for i in tqdm(range(len(self.docs))):
            s = cosine_similarity([self.t_vec, self.vecs[i]])[0][1]
            sims.append((i, s, ''))
        sims.sort(key=lambda x: x[1], reverse=True)
        return sims

    def sim_all(self):
        sims = [ ]
        for i in trange(len(self.docs), desc='first student'):
            for j in trange(i+1, len(self.docs), desc='second student', leave=False):
                s = cosine_similarity([self.vecs[i], self.vecs[j]])[0][1]
                sims.append((i, j, s, ''))
        sims.sort(key=lambda x: x[2], reverse=True)
        return sims



class PycodeSimilar(Comparer):
    def sim_template(self):
        sims = [ ]
        from pycode_similar import detect
        exceptions = collections.Counter()
        for i in tqdm(range(len(self.docs))):
            try:
                ret = detect([self.t_doc if True else '', self.docs[i]],
                             diff_method=pycode_similar.UnifiedDiff,
                             keep_prints=False,
                             module_level=True)
                s = ret[0][1][0].plagiarism_percent
            except Exception as e:  # pylint: disable=broad-except
                exceptions[e.__class__.__name__] += 1
                s = float('nan')
            sims.append((i, s, ''))
        #import IPython ; IPython.embed()
        if exceptions:
            print("Detected pycode_similar exceptions comparing to template:")
            for name, i in exceptions.items():
                print(i, name)
        sims.sort(key=lambda x: x[1], reverse=True)
        return sims

    def sim_all(self):
        sims = [ ]
        from pycode_similar import detect
        exceptions = collections.Counter()
        for i in trange(len(self.docs), desc='first student'):
            for j in trange(i+1, len(self.docs), desc='second student', leave=False):
                try:
                    ret = detect([self.docs[i], self.docs[j]],
                                 diff_method=pycode_similar.UnifiedDiff,
                                 keep_prints=False,
                                 module_level=True)
                    s = ret[0][1][0].plagiarism_percent
                except Exception as e:
                    exceptions[e.__class__.__name__] += 1
                    s = float('nan')
                sims.append((i, j, s, ''))
        if exceptions:
            print("Detected pycode_similar exceptions comparing to template:")
            for name, i in exceptions.items():
                print(i, name)
        #import IPython ; IPython.embed()
        sims.sort(key=lambda x: x[2], reverse=True)
        return sims



FILTERS = [
    'RemoveDuplicateLines',
    ]

def main(argv=sys.argv[1:]):
    global FILTERS
    parser = argparse.ArgumentParser()
    parser.add_argument('--template', '-t')
    parser.add_argument('--compare', '-c', default='Tfidf')
    parser.add_argument('--filter', '-f', default=','.join(FILTERS))
    parser.add_argument('--limit', type=int, help='Limit to the first N documents')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('notebooks', nargs='+')
    args = parser.parse_args(argv)
    #print(args)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        #LOG.setLevel(logging.DEBUG)

    FILTERS = args.filter.split(',')

    comparer = globals()[args.compare]()

    if args.template:
        comparer.template(read_file(args.template))

    names = args.notebooks
    names = filter(lambda x: not x.endswith('~'), names)
    names = list(names)

    for i, notebook in enumerate(names):
        if args.limit and i >= args.limit:
            break
        comparer.add(read_file(notebook))


        #print(nb)

    #results = pycode_similar.detect([t_doc, *docs], diff_method=pycode_similar.UnifiedDiff, keep_prints=False, module_level=False)
    #print(results)

    comparer.process()

    if comparer.has_template:
        print()
        print("Compare to template")
        sims = comparer.sim_template()
        names_short = remove_common_parts(names)
        for i, s, desc in sims:
            print(f"{names_short[i][-15:]:15}  {s:0.02}")


    print()
    print("Compare all students")
    sims = comparer.sim_all()
    for i, j, s, desc in sims:
        name1, name2 = remove_common_parts((names[i], names[j]))
        print(f"{name1[:15]:15}  {name2[:15]:15}  {s:0.02}      nbdiff -OD {names[i]} {names[j]} | less -R")
