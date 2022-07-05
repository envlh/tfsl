""" Intended to make certain commonly used derived types which depend only on tfsl itself easier to use.
    That no other file imports this one, not even __init__.py, is intentional.
"""

from typing import List, Union

import tfsl.languages

language_or_list_of_languages = Union[tfsl.languages.Language, List[tfsl.languages.Language]]
