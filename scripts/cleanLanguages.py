import tfsl
import utils
import time


def fetch_lexemes_to_clean():
    query = 'SELECT DISTINCT ?lexeme { ?lexeme dct:language wd:Q732317 }'
    return utils.sparql_query(query)


def clean_lexeme(lexeme):
    change = False
    if lexeme.language == 'Q732317':
        lexeme.language = tfsl.langs.ee_
        change = True
    return change


def apply_changes(lexemes):
    account = utils.load_json_file('account.json')
    session = tfsl.WikibaseSession(account['username'], account['password'])
    for lexeme in lexemes:
        time.sleep(5)
        session.push(lexeme, "cleaning language", 5, True)
        print('Lexeme {} edited!'.format(lexeme.id))


def main():
    changed_lexemes = []
    lexemes = fetch_lexemes_to_clean()
    for lex in lexemes:
        lexeme_id = lex['lexeme']['value'][31:]
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
