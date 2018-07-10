# Feature documentation

The data source is a set of nodes.

*Node features* are mappings from nodes to strings or numbers.

*Edge features* are mappings from pairs of nodes to strings or numbers.

The first *n* nodes represent the words of the corpus, in the natural order.
We call them *slots*.
Think of slots as textual positions, without the stuff that occupies those positions.

Higher nodes correspond to other textual types, such as `verse`, `chapter`, and `book`.

For each node we need to be able to determine to what kind of object it corresponds:
we have a node feature *otype* for that.

For each non-slot node we need to be able to determine to which slot nodes it is linked:
we have an edge feature *oslots* for that.

*otype* and *otype* represent the abstract structure of the text.

All the concrete material is added onto them in the form of additional node features and edge features.



name | nodeType | example values | explanation
--- | --- | --- | ---
**otype** | all | `word` `verse` `chapter` `book` | the type of a node
**oslots** | all non-slot types | {`1`, `2`, `3`} | per non-slot node it is the sets of slots linked to it
**otext** | none | none | configuration file: definition of text-formats and sections
**book** | `book` | `John` | the name of a book 
**book@en** | `book` | `John` | the name of a book in English (currently identical to **book**
**chapter** | `chapter` | `3` | the number of a chapter 
**verse** | `verse` | `16` | the number of a verse 
**post** | `word` | `?̔` | post-word material: non letter characters at the end of a word, including punctiation and white space
**orig** | `word` | `λόγος,` | the word as encoded in the source file, after splitting on white space
**pre** | `word` | `?̔` | pre-word material: non letter characters at the start of a word
**main** | `word` | `λόγος` | the word, after splitting on white space and punctuation
**plain** | `word` | `ΛΟΓΟΣ` | the word, stripped of accents, capitalized, after splitting on white space and punctuation
**page** | `word` | `191` | number of the new page that starts right before the present word
**para** | `word` | `+` | indicates that a new paragraph starts right before the present word




