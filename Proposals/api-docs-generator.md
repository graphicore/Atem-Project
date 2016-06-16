# Proposal: API Documentation Generator

**This is not the API documentation you are looking for.**

Documentation is a need that we have. *This is a navigational dead end* to raise
awareness for our need of an **automated system to generate well structured API documentation**
from our original source code, where then as well the source codes will have to be changed to feed
into that system.

## Why

Atem is a young project with still fast and often changing code. Well made
hand-written documentation is a luxury we can't afford yet, it'd be outdated
in the moment we stop writing docs and switch to write code again.

## What

We want to have good readable and ideally hyper-linked documentation
generated from our original source files. In the best case synced via github
hooks and travis on update or on new tag releases.

Python has Sphinx, which is good but, as it seems, not very well with JavaScript.
We also have very uniformly organized repositories, code in a modular fashion
and a relatively well defined coding style. It should be possible to take
some advantage from that.

Generating the docs has a higher priority than automatic updating, in fact,
the latter could be impractical(when?).

Maybe we can make or reuse something in the spirit of literate programming.
It would be nice to still have the source-code accessible where the generated
documentation is displayed.

We will have to augment our source code with doc-strings accordingly. This
is something that can grow over time.
