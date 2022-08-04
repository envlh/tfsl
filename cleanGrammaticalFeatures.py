import tfsl
import utils


def fetch_lexemes_to_clean(replacements):
    values = []
    for feature in replacements:
        values.append('wd:{}'.format(feature))
    query = 'SELECT DISTINCT ?lexeme { ?lexeme dct:language wd:Q150 ; ontolex:lexicalForm/wikibase:grammaticalFeature ?feature . VALUES ?feature { %VALUES% } }'.replace('%VALUES%', ' '.join(values))
    return utils.sparql_query(query)


def clean_lexeme(lexeme, replacements):
    change = False
    for form in lexeme.forms:
        for feature in replacements:
            if feature in form.features:
                change = True
                form.features.remove(feature)
                form.features.update(replacements[feature])
    return change


def apply_changes(lexemes):
    account = utils.load_json_file('account.json')
    session = tfsl.WikibaseSession(account['username'], account['password'])
    for lexeme in lexemes:
        session.push(lexeme, "cleaning grammatical features", 5)
        print('Lexeme {} edited!'.format(lexeme.lexeme_id))


def main():
    replacements = utils.load_json_file('replacements.json')
    changed_lexemes = []
    lexemes = fetch_lexemes_to_clean(replacements)
    for lex in lexemes:
        lexeme_id = lex['lexeme']['value'][31:]
        lexeme = tfsl.L(lexeme_id)
        if clean_lexeme(lexeme, replacements):
            changed_lexemes.append(lexeme)
    if changed_lexemes:
        print('{} lexemes to clean...'.format(len(changed_lexemes)))
        apply_changes(changed_lexemes)
    else:
        print('No lexeme to clean!')


if __name__ == '__main__':
    main()
