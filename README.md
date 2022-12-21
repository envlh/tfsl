# tfsl

tfsl (an abbreviation of "twofivesixlex") is a Python-based framework for manipulating entities on Wikibases, such as lexemes and their forms and senses.
Think of it as Pywikibot but with objects in a Wikibase coming first.

Support for manipulating items, as well as claim types other than monolingual text values, is coming soon.

## Setup

[Clone this repository](https://docs.gitlab.com/ee/gitlab-basics/start-using-git.html#clone-a-repository). (Depending on which Git host you're reading this from, the URL with which to clone might vary.) The cloned repository should now reside in some folder, which may vary depending on where you performed the clone. Let's call that folder `/path/to/tfsl` (or `C:\path\to\tfsl` on a Windows system).

Make sure the cloned repository ends up in your PYTHONPATH. The simplest way to do this below, for a Unix (Linux/Mac OS/BSD) system, where the folder path `/path/to/tfsl` must be substituted with the :

```
export PYTHONPATH=$PYTHONPATH:/path/to/tfsl
```

([On Windows this process is a bit different.](https://stackoverflow.com/q/3701646))

Install the dependencies of the repository, again substituting the path accordingly:

```
pip install -r /path/to/tfsl/requirements.txt
```

Now rename 'config.ini.example' to 'config.ini' and specify
1) where retrieved lexemes and items should be stored ('CachePath') and
2) how long (in seconds) these should be stored before regeneration ('TimeToLive').

## Use

For a quick overview of how to use this library, see the file `overview.md`.

Many facets of use are exemplified in the unit tests. (Unless otherwise stated in a comment in a unit test file, any functionality which is not exhibited in a unit test should be assumed to be unstable.)

Perhaps when this is better developed a more thorough tutorial on its use will come.

## Licensing and external credits

Except where otherwise specified below, all code in this repository is under Apache 2.0.

- The contents of "auth.py" were modified from Michael Schoenitzer's [LexData](https://github.com/Nudin/LexData/) tool, under the X11 license placed in that repository.

