# tfsl

tfsl (an abbreviation of "twofivesixlex") is a Python-based framework for manipulating entities on Wikibases, such as lexemes and their forms and senses.
Think of it as Pywikibot but with objects in a Wikibase coming first.

Support for manipulating items, as well as claim types other than monolingual text values, is coming soon.

## Setup

This was developed using Python 3.8.5 on a Unix system.
All you need besides that or some other similarly recent version of Python is the 'requests' library ('pip install requests' or something similar).

## Use

Most facets of use are exemplified in the unit tests.
Perhaps when this is better developed a more thorough tutorial on its use will come.

## Licensing and external credits

Except where otherwise specified below, all code in this repository is under Apache 2.0.

- The contents of "auth.py" were modified from Michael Schoenitzer's [LexData](https://github.com/Nudin/LexData/) tool, under the X11 license placed in that repository.

