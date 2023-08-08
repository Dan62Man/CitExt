# CitExt
Citation extractor from text, finds sentences with citations and the enclosing sentences.

## Needed information

Save your text in .txt files and save them in a `texts` folder.


## Output

A folder with a json file for each txt file will be created and the json files will contains lists of a collection of sentences: 

```
"sentences": {
    0: {
        "previous_sentence": "This sentence does not contain a citaion."
        "citation_sentence": "This is the sentence that does contain a citation (Surname, 2023)."
        "next_sentence": "This also does not contain a citation in the sentence."
    }
}
```
