# Getting started

Once you have set up tfsl, you will probably want to begin using it to do stuff with lexemes.

To start, simply

```python
import tfsl
```

## Preliminary: Languages

In tfsl there is a construct called the `Language` which pairs a language code with a Qid.
Wherever a language is needed in a tfsl script, this `Language` is used in that place.
A `Language` is selected whenever a language code (in the case of lemmata, sense glosses, form representations,
and monolingual text) or language item (in the case of lexeme languages) is encountered in a lexeme retrieved by tfsl,
and this same `Language` is likewise resolved to a language code or Qid at edit time.

A list of languages present among Wikidata labels/descriptions/aliases is provided as `tfsl.langs`,
mapping language codes (after substituting hyphens with underscores and adding a trailing underscore)
to particular items:

```python
tfsl.langs.de_ # maps "de" to "Q188"
tfsl.langs.dag_ # maps "dag" to "Q32238"
tfsl.langs.sms_ # maps "sms" to "Q13271"
```

Note that the mapping to items in this list typically prefers the language item over an item combining a language and anything else.
There are also other changes that a visit to `tfsl/languages.py' and looking for your desired code might inform you of:

```python
tfsl.langs.be_tarask_ # maps "be-tarask" to "Q9091" and NOT "Q2087886"!
tfsl.langs.ms_arab_ # maps "ms-arab" to "Q9237" and NOT "Q107526440"!
```

You can make your own `Language` objects for custom code-item pairs, and you can use them when modifying lexemes,
but in order for these to be automatically resolved the next time a lexeme is retrieved,
you must assign them to an attribute in `tfsl.langs_`:

```python
my_custom_language = tfsl.Language("gsg", "Q33282")
gsg_lexeme = tfsl.L(29237) # will error here as gsg is not part of tfsl.langs
tfsl.langs.gsg_ = my_custom_language
gsg_lexeme = tfsl.L(29237) # will not error here as gsg is now part of tfsl.langs
```

## Accessing lexemes

Retrieval of existing lexemes to modify is as simple as calling tfsl.L with the Lid:

```python
renne_lexeme = tfsl.L(351)
chien_lexeme = tfsl.L('L241')
```

## Exploring lexemes

Once you have retrieved a lexeme, you can explore each of its many parts:

### Lemmata, lexeme language, and lexeme category

To retrieve a lemma in a given language, simply index into it with that language.

```python
dog_lexeme = tfsl.L("L524153")
dog_lemma_hi = dog_lexeme[tfsl.langs.hi_]
dog_lemma_ur = dog_lexeme[tfsl.langs.ur_]
```

`dog_lemma_hi` and `dog_lemma_ur` are what are referred to as `tfsl.MonolingualText` objects
(see "Value types: MonolingualText" below):

```python
print(dog_lemma_hi.text) # should print "कुत्ता"
print(dog_lemma_hi.language) # should print something like 'Language("hi", "Q11051")'
```

If you know the text of a lemma but not its language, you can also retrieve the lemma
by providing any `MonolingualText` with the text of that lemma:

```python
dog_lemma_fr = tfsl.MonolingualText("chien", tfsl.langs.fr_)
dog_lemma_fr = "chien" @ tfsl.langs.fr_ # does the same thing as the above, with syntax reminiscent of SPARQL

dog_lexeme = tfsl.L("L313030")
dog_lemma_fro = dog_lexeme[dog_lemma_fr]
```

The lexeme language is a `Language`, and the lexeme category is just a Qid string:

```python
print(dog_lexeme.language) # should print something like 'Language("fro", "Q35222")
print(dog_lexeme.category) # should print "Q1084"
```

### Statements

To access some statements on a `Lexeme`, simply index into it with the desired Pid.
If a valid Pid is provided, then a list of `tfsl.Statement`s will be returned
(which may be empty if the property is not present on the lexeme):

```python
tour_lexeme = tfsl.L("L2330")
describers_of_tour = tour_lexeme["P1343"] # should be a list of two statements
origins_of_tour = tour_lexeme["P5191"] # should be a list with one statement
examples_of_tour = tour_lexeme["P5831"] # should be an empty list

if tour_lexeme.haswbstatement("P5831"): # syntax reminiscent of the keyword used in Wikidata searching
	print("This lexeme has a usage example!")
if tour_lexeme.haswbstatement("P1343", tfsl.ItemValue("Q1935308")):
	print("This lexeme is described by the SAOB!")
```

Each `Statement` consists of a number of parts:

```python
klimatforandring = tfsl.L("L242121")
usage_examples = klimatforandring["P5831"]
first_usage_example = usage_examples[0]

print(first_usage_example.id) # should be something like "L242121$4e8b1dbe-412c-cf34-55be-964249290213"
print(first_usage_example.property) # should be "P5831"
print(first_usage_example.value) # should be a quote, returned as a MonolingualText
print(first_usage_example.rank) # should be something like "Rank.Normal"
first_usage_example_qualifiers = first_usage_example.qualifiers
first_usage_example_references = first_usage_example.references
```

#### Value types: Strings

Any property whose value is underlyingly a string type will have a string value for `tfsl.Statement.value`:

```python
saob_id = klimatforandring["P9963"][0]
print(type(saob_id.value)) # should be "str"
```

#### Value types: MonolingualText

As noted in the Preliminary on Languages above, any combination of text with a language code is represented alongside
a `Language`.
This also includes the values of `Statement`s with monolingual text datatype, which pair the string with the `Language`
in the form of a `MonolingualText`:

```python
first_usage_example_value = first_usage_example.value

print(first_usage_example_value.text) # should print a sentence in Swedish
print(first_usage_example_value.language) # should print something like 'Language("sv", "Q9027")'
```

#### Value types: ItemValue

Any property whose value is some Wikibase entity (be it an item, property, lexeme, form, or sense)
will have a `tfsl.ItemValue` as the value for `tfsl.Statement.value`:

```python
sv_noun_gender = klimatforandring["P5185"][0]
print(sv_noun_gender.id) # should be "Q1305037"
print(sv_noun_gender.type) # should be "item"
```

#### Value types: novalue and somevalue

"novalue" values are stored as the boolean `False`.

"somevalue" ("unknown value") values are stored as the boolean `True`.

#### Qualifiers

To list qualifiers to the statement, index into it with the Pid of the qualifying property.
If a valid Pid is provided, a list of `tfsl.Claim`s will be returned
(which, as with indexing into statements, may be empty if the provided property does not
qualify the statement):

```python
subject_forms_of_example = first_usage_example["P5830"] # should be a list with one Claim
subject_senses_of_example = first_usage_example["P6072"] # ditto
language_styles_of_example = first_usage_example["P6191"] # should be an empty list
```

Each `Claim`, like each `Statement`, has a property and a value
(but unlike a `Statement` lack a rank, qualifiers, or references themselves):

```python
first_subject_form = subject_forms_of_example[0]
print(first_subject_form.property) # should be "P5830"
print(first_subject_form.value) # should be something like 'ItemValue("L242121-F1")'
```

The list of references is a list of `tfsl.Reference`, each of which may be indexed into
similarly as with qualifiers, with the same behavior:

```python
usage_example_reference = first_usage_example_references[0]
stated_ins_of_reference = usage_example_reference["P248"] # should be a list with one Claim
pages_of_reference = usage_example_reference["P304"] # should be an empty list
```

### Senses

To access a Sense on an existing lexeme, index into it with its sid:

```python
first_sense = klimatforandring["S1"] # should return a LexemeSense
first_sense = klimatforandring["L242121-S1"] # ditto
```

Similarly to indexing `Lexeme`s to obtain lemmata, `tfsl.LexemeSense`s may be indexed to obtain glosses:

```python
print(first_sense[tfsl.langs.en_])
print(first_sense[tfsl.langs.sv_])
```

The same statement indexing behavior that applies to `Lexeme`s also applies to `Sense`s.

### Forms

To access a Form on an existing lexeme, index into it with its Fid:

```python
nom_sing_indef = klimatforandring["F1"] # should return a LexemeForm
nom_sing_indef = klimatforandring["L242121-F1"] # ditto
```

Similarly to indexing `Lexeme`s to obtain lemmata, `tfsl.LexemeForm`s may be indexed to obtain representations:

```python
print(nom_sing_indef[tfsl.langs.sv_]) # should return a MonolingualText
print(nom_sing_indef["klimatförändring" @ langs.en_]) # should return the same thing
```

The grammatical features on a `LexemeForm` are just a set of Qids:

```python
print(nom_sing_indef.features) # should return {"Q131105", "Q110786", "Q53997857"}
```

The same statement indexing behavior that applies to `Lexeme`s also applies to `Form`s.

## Creating lexemes

To create a `Lexeme`, only the lemma, language, and lexical category are required, to be provided in that order:

```python
newlexeme = tfsl.Lexeme("hello" @ tfsl.langs.en_, tfsl.langs.en_, "Q83034")
```

If you have a list of statements, forms, or senses to add, you can also optionally add any of those after the other arguments:

```python
newlexeme = tfsl.Lexeme("hello" @ tfsl.langs.en_, tfsl.langs.en_, "Q83034",
						statements = statementlist,
						forms = formlist,
						senses = senselist)
```

More on the contents of `statementlist`, `formlist`, and `senselist` below.

### Creating statements

Given a Pid and an appropriate property value, a statement may be created as follows:

```python
newstatement = tfsl.Statement("P1343", ItemValue("Q464886"))
newstatement2 = tfsl.Statement("P5187", "hello" @ tfsl.langs.en_)
```

If you want to create a lexeme with those two statements, then they can be
added to a Python list and provided at lexeme creation time with the `statements` argument to `Lexeme`:

```python
statementlist = [newstatement, newstatement2]
newlexeme = tfsl.Lexeme("hello" @ tfsl.langs.en_, tfsl.langs.en_, "Q83034",
						statements = statementlist)
```

Alternatively, these statements may be added directly to the newly created lexeme as follows:

```python
newlexeme = newlexeme + newstatement
newlexeme = newlexeme + newstatement2
```

### Creating forms

Given a form representation, a new `LexemeForm` may be created as follows:

```python
newform_representation = "hello" @ tfsl.langs.en_
newform = tfsl.LexemeForm([newform_representation])
```

(The representation is in a list because there may be multiple form representations on a single `LexemeForm`.)

To add a new form representation to a lexeme form, it is as simple as

```python
another_newform_rep = "hallo" @ tfsl.langs.en_gb_
newform = newform + another_newform_rep
```

(Note that if there were already a British English form representation on `newform`, that representation would be overwritten.)

If features are desired to be added, they can be added to a Python list and provided as the `features` argument to `LexemeForm`:

```python
newform_features = ["Q2339337", "Q77768943"]
newform = tfsl.LexemeForm(newform_representation, features=newform_features2)
```

To add a new feature to a lexeme form proceeds similarly to adding a representation:

```python
newform = newform + "Q901711"
```

Much of the content of "Creating statements" above also applies here; `LexemeForm` also takes a `statements=` argument.

If you want to create a lexeme with this form, then it can be
added to a Python list and provided at lexeme creation time with the `forms` argument to `Lexeme`:

```python
formlist = [newform]
newlexeme = tfsl.Lexeme("hello" @ tfsl.langs.en_, tfsl.langs.en_, "Q83034",
						forms = formlist)
```

Alternatively, to add the new form to the new lexeme is as simple as

```python
newlexeme = newlexeme + newform
```

### Creating senses

Given a sense gloss, a new `LexemeSense` may be created as follows:

```python
newsense_gloss = "greeting" @ tfsl.langs.en_
newsense = tfsl.LexemeSense([newsense_gloss])
```

(The gloss is in a list because there may be multiple sense glosses on a single `LexemeSense`.)

To add a new sense gloss to a lexeme sense, it is as simple as

```python
another_newsense_gloss = "hälsning" @ tfsl.langs.sv_
newsense = newsense + another_newsense_gloss
```

(Note that if there were already a Swedish sense gloss on `newsense`, that gloss would be overwritten.)

Much of the content of "Creating statements" above also applies here; `LexemeSense` also takes a `statements=` argument.

If you want to create a lexeme with this sense, then it can be
added to a Python list and provided at lexeme creation time with the `senses` argument to `Lexeme`:

```python
senselist = [newsense]
newlexeme = tfsl.Lexeme("hello" @ tfsl.langs.en_, tfsl.langs.en_, "Q83034",
						senses = senselist)
```

Alternatively, to add the new sense to the new lexeme is as simple as

```python
newlexeme = newlexeme + newsense
```

## Submitting lexeme edits

If you want to edit lexemes, you must first ensure that you are logged in:

```python
my_username = 'Mahirtwofivesix'
current_session = tfsl.WikibaseSession(my_username)
```

This will prompt you for a password when it is run.
You may optionally provide this password as the second argument to WikibaseSession:

```python
my_username = 'Mahirtwofivesix'
my_password = '' # your password here
current_session = tfsl.WikibaseSession(my_username, my_password)
```

To submit edits to a particular lexeme,
or to create an entirely new one,
one can use `WikibaseSession.push` and provide
the `Lexeme` in question and an optional edit summary:

```python
current_session.push(tour_lexeme)
current_session.push(renne_lexeme, "lexème modifiée")
current_session.push(newlexeme, "nouveau lexème")
```

