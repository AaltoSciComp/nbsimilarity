# nbsimilarity: compare similarity in ipynb notebook files

Notebooks are just files on disk.  If you want to detect similarity
between them (for example, for plagiarism detection), in principle this
is easy: extract the code from the notebooks, and compare them.  This
package does that in the simplest way possible: it doesn't currently
cache data or anything, you give it a glob of files and it compares
it.  Thus, it is suitable for a single assignment, but not some
persistent record of everything turned in.

It was designed for use with nbgrader, but there isn't really anything
nbgrader-specific here at all (by design - that's a different
abstraction layer and can be kept separate).  If you want to do your
own thing, the [nbformat
package](https://nbformat.readthedocs.io/en/latest/) provides an API
and the [nbconvert tool](https://nbconvert.readthedocs.io/en/latest/)
does it for you.



## Installation

This is a normal Python package.  It isn't currently distributed on repositories, so
either one of:

```
pip install .
pip install https://github.com/AaltoSciComp/nbsimilarity/archive/master.zip
```



## Basic usage

The basic principle is that you enter all files on command line to
run.  It will then print a report of what is most similar.  There
isn't a very good user interface yet, it just prints things to the
console.

For example, to run on all files of one assignment.  The `*` glob is
the student username:

```
nbsimilarity submitted/*/01_mlp/11_logreg.ipynb
```

There is support for specifying a template file, which all students
are assumed to have used.  By subtracting the template out, you can
get a more accurate comparison of similarity of the students work:

```
nbsimilarity --template source/01_mlp/11_logreg.ipynb submitted/*/01_mlp/11_logreg.ipynb
```

Example output.  The usernames and similarity (number 0-1) are
printed, and for the between-student comparison a `nbdiff` command is
printed which will show the similarities on the console:

```
Compare to template
usernam1         0.52
ttekkar1         0.51
tudents1         0.5
tekkart1         0.3
...
...

Compare all students
usernam1           ttekkar1           0.9      nbdiff -OD submitted/usernam1/01_mlp/11_logreg.ipynb submitted/ttekkar1/01_mlp/11_logreg.ipynb | less -R
usernam1           tudents1           0.95     nbdiff -OD submitted/usernam1/01_mlp/11_logreg.ipynb submitted/tudents1/01_mlp/11_logreg.ipynb | less -R
tudents1           tekkart1           0.5      nbdiff -OD submitted/usernam1/01_mlp/11_logreg.ipynb submitted/ttekkar1/01_mlp/11_logreg.ipynb | less -R
...
..

```



## Reference

(empty)



## Insides

This is *very much* under development (only a few hours of work so
far), so everything you read below should be improved later.

* Output prints to the console, and prints `nbdiff`-command lines that
  you can copy and paste to another terminal to look at the actual
  diff and use your judgement about what to do.
* Right now it prints all 
* Comparison functions should be pluggable, and selectable with
  `--compare`. Right now comparers are:
  * `Tfidf`: Some tf-idf tool based on word tokens (not code) 
  * `PycodeSimilar`: Something using
    [pycode-similar](https://pypi.org/project/pycode-similar/)
* There is a filtering layer.



## Other notes

Some considerations in design:

* Jupyter uses IPython as the kernel, not raw Python.  Various IPython
  magic functions need to be handled (for now, we strip them all out).

* All comparison is re-calculated on every run, there is no caching.
  With modern computing power, this isn't a problem yet but could be
  improved later.  If you go beyond this level, maybe you want to use
  some service-based tool.



## Status and maintenance

Still under development, don't count on it working without author
support.

Anyone who can provide similarity-detection code should file an issue
and we can give you help adding it.

Contact: Richard Darst
