# CitExt
Citation extractor from text, finds sentences with citations and the enclosing sentences.
It then provides a sentiment analysis, along with NLI indicating whether the citation section (part of text mentioning and discussing the citation) is positive negative or neutral finally these are represented in a graph, where the colour red indicates a negative reference, the colour green indicates a positive one. Otherwise it is neutral

## Needed information

Save your text in .txt format and save them in a `texts` folder.
Provide a .txt with the same base name of the file abve followed by `-bibliography.txt`:
```
texts
 |
 -- KentEtAl2023.txt
 -- KentEtAl2023-bibliography.txt:
```

Contents KentEtAl2023-bibliography.txt:
```
Clark Kent and Bruce Wayne. 2023. Example of a reference in bibliography
M. Morales, P. Parker, Dr O. Octavius. 2023. Second Line of example
... 
```


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
