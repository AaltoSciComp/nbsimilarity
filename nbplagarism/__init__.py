from ._version import __version__

import argparse
from collections import namedtuple
import sys

import nbformat
import pycode_similar
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

Student = namedtuple('Student', ['name', 'nb', 'doc', 'vec'],
                     defaults=[None]*4)

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


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--template', '-t')
    #parser.add_argument('--template', '-t')
    parser.add_argument('notebooks', nargs='+')
    args = parser.parse_args(argv)
    #print(args)

    if args.template:
        with open(args.template) as nbf:
            t_nb = nbformat.read(nbf, 4)
            t_doc = nb_to_doc(t_nb)
            #t_vec = TfidfVectorizer().fit_transform(t_doc).toarray()

    names = [ ]
    nbs = [ ]
    docs = [ ]

    for notebook in args.notebooks:
        names.append(notebook)
        with open(notebook) as nbf:
            nb = nbformat.read(nbf, 4)
            nbs.append(nb)
        doc = nb_to_doc(nb)
        docs.append(doc)

    vecs = TfidfVectorizer().fit_transform(docs + [t_doc]).toarray()
    print(vecs)
    t_vec = vecs[-1]
    vecs = vecs[:-1]

        #print(nb)

    #results = pycode_similar.detect([t_doc, *docs], diff_method=pycode_similar.UnifiedDiff, keep_prints=False, module_level=False)
    #print(results)

    print()
    print("Compare to template")
    for i in range(len(names)):
        s = cosine_similarity([t_vec, vecs[i]])[0][1]
        print(f"{names[i][-20:]:20}   {s:0.02}")
        #print(s)
        #print(names[i][-20:].rjust(20), s)


    print()
    print("Compare all students")
    sims = [ ]
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            s = cosine_similarity([vecs[i], vecs[j]])[0][1]
        sims.append((i, j, s))

    sims.sort(key=lambda x: x[2], reverse=True)
    for i, j, s in sims:
        print(f"{names[i][-20:]:20}   {names[j][-20:]:20}   {s:0.02}")
        #print(s)
        #print(names[i][-20:].rjust(20), s)
