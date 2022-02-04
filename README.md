# tfsl

tfsl (an abbreviation of "twofivesixlex") is a Python-based framework for manipulating entities on Wikibases, such as lexemes and their forms and senses.
Think of it as Pywikibot but with objects in a Wikibase coming first.

Support for manipulating items, as well as claim types other than monolingual text values, is coming soon.

## Setup

Clone this repository. (Depending on which Git host you're reading this from, the URL might vary.)

Now make sure this ends up in your PYTHONPATH. The simplest way to do this below is for a Unix system, where the path must be substituted accordingly:

```
export PYTHONPATH=$PYTHONPATH:/path/to/tfsl
```

Now install its dependencies, again substituting the path accordingly:

```
pip install -r /path/to/tfsl/requirements.txt
```

Now rename 'config.ini.example' to 'config.ini' and specify
1) where retrieved lexemes and items should be stored ('CachePath') and
2) how long (in seconds) these should be stored before regeneration ('TimeToLive').

## Use

Most facets of use are exemplified in the unit tests. (Unless otherwise stated in a comment in a unit test file, any functionality which is not exhibited in a unit test should be assumed to be unstable.)

Perhaps when this is better developed a more thorough tutorial on its use will come.

## Licensing and external credits

Except where otherwise specified below, all code in this repository is under Apache 2.0.

- The contents of "auth.py" were modified from Michael Schoenitzer's [LexData](https://github.com/Nudin/LexData/) tool, under the X11 license placed in that repository.

