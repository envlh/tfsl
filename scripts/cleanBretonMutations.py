import tfsl
import utils
import time
import re


def fetch_lexemes_to_clean():
    query = 'SELECT DISTINCT ?lexeme { ?lexeme dct:language wd:Q12107 ; ontolex:lexicalForm ?f . ?f wikibase:grammaticalFeature wd:Q56648701 ; ontolex:representation ?form . FILTER (!REGEX(?form,"^[fzcFZC]")) }'
    return utils.sparql_query(query)


def clean_lexeme(lexeme):
    change = False
    for form in lexeme.forms:
        if 'Q56648701' in form.features and not re.search('^[fzcFZC]', form.representations.texts.pop().text):
            change = True
            form.features.remove('Q56648701')
            form.features.add('Q97130345')
    return change


def apply_changes(lexemes):
    account = utils.load_json_file('account.json')
    session = tfsl.WikibaseSession(account['username'], account['password'])
    for lexeme in lexemes:
        time.sleep(5)
        session.push(lexeme, "cleaning grammatical features", 5, True)
        print('Lexeme {} edited!'.format(lexeme.id))


def main():
    changed_lexemes = []
    lexemes = fetch_lexemes_to_clean()
    for lex in lexemes:
        lexeme_id = lex['lexeme']['value'][31:]
        if lexeme_id not in ('L630016', 'L628789'):
            lexeme = tfsl.L(lexeme_id)
            if clean_lexeme(lexeme):
                changed_lexemes.append(lexeme)
    if changed_lexemes:
        print('{} lexemes to clean...'.format(len(changed_lexemes)))
        apply_changes(changed_lexemes)
    else:
        print('No lexeme to clean!')


if __name__ == '__main__':
    main()
