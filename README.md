<img src="/docs/images/tf-small.png" align="left"/>

# Pilot

This repo pilots the study of correspondences between patristic texts and the Greek New Testament.

## Source Data

In the *sources* directory there are partristic (*pt*) and New Testament texts (*nt*).

They are in XML-TEI.

Currently: only the book of John.

(provenance to be written)

## Converted data

The sources have been converted to
[Text-Fabric](https://github.com/Dans-labs/text-fabric) format,
the resulting feature files are in
the *tf* directory.

The information we want to draw from the source files are incoded in
[features](docs/features.md).

## Conversion 

The conversion itself is coded in
[tfFromNt](https://nbviewer.jupyter.org/github/pthu/pilot/blob/master/programs/tfFromNt.ipynb),
a Jupyter notebook.

## Tutorial

A brief example of how to work with this TF data set is the
[tutorial notebook](https://nbviewer.jupyter.org/github/pthu/pilot/blob/master/tutorial/start.ipynb).

## Authors

Joint work by

* [Ernst Boogert](https://www.pthu.nl/Over_PThU/Organisatie/Medewerkers/e.boogert/), 
  [PThU](https://www.pthu.nl/en/)
* [Dirk Roorda](http://knaw.academia.edu/DirkRoorda)
  [DANS](https://dans.knaw.nl/en/front-page?set_language=en)
