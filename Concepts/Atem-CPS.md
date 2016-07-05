# Atem-CPS and OMA

*This is an introduction to the concepts of CPS and OMA by comparison with
CSS and the DOM.*

OMA and CPS are conceptually influenced by the interplay of [DOM](https://en.wikipedia.org/wiki/Document_Object_Model)
(Document Object Model) and [CSS](https://en.wikipedia.org/wiki/Cascading_Style_Sheets)
(Cascading Style Sheets) by the [W3C](https://www.w3.org/).


CPS stands for **Cascading Parameters Sheets** we kept the name similar to
CSS on purpose. OMA stands for **Object Model API** and is the conceptual
counterpart to the DOM.

## Similarities to DOM and CSS

CPS and CSS are used to associate `properties` with nodes in the OMA/DOM
tree structure by attaching `selectors` to blocks of `rules`.

A `property` is made of a `name` and a `value`.

A `rule` is a collection of `properties` plus a  list of `selectors`.

[CSS-Selectors](https://www.w3.org/TR/CSS22/selector.html):

> In CSS, pattern matching [= selectors] rules determine which style rules
  apply to elements in the document tree. These patterns, called selectors,
  may range from simple element names to rich contextual patterns. If all
  conditions in the pattern are true for a certain element, the selector
  matches the element.

Selectors are a query language for selecting nodes in a DOM-tree,
they are similar to [XPath](https://en.wikipedia.org/wiki/XPath) but simpler.
If a selector of a rule matches a node in the DOM tree, the rule and
therefore its properties apply to the node.

When many rules apply to the same node the `specificity` of the respective
matching selector defines in which order the rules are applied. The **more
specific rules are applied first**. If the rule that is applied first misses
a property definition, the second/next-specific rule is applied and so on.
**This fallback mechanism is called cascading.**

## Differences to DOM and CSS

We made adjustments to the DOM concept and created a whole new kind of
computing. We believe this is particularly well suited for the next generation
of parametric design tools.

### OMA is an Abstraction

The DOM is made of element types that are *specifically* created to describe
web pages. It defines elements like `<article>`, `<h1>` to `<h5>` for
headlines or `<p>` for paragraphs.

The OMA is just an abstract API that is used as a base to define domain specific
object models. E.g. for type design applications we created the MOM, **Metapolator
Object Model** and for the *Bauhaus Emblem Font*, there is the BEOM **Bauhaus Emblem
Object Model**.

The OMA defines all of the nuts and bolts needed to create a domain
specific model that is connected to CPS and to our tooling. This way we can
act as **a catalyst to jump-start new domains of parametric tooling.** More
and better tools will help all implementors of the OMA.

### Properties are Programming and Math

In CSS property values are very specific for the domain of "styling" HTML-Documents.
I.e. setting colors, margins, positions and alignments. The available properties
are firmly defined and are limited in their expressiveness. E.g. the `background`
property can only define the the background of a DOM element, nothing else.

In CPS, in turn, `Property Values` are defined in a small programming language,
the **Atem Property Language**. This language can be used to define math formulae and
other expressions. The `Property Names` are free to choose — though, depending
on the OMA-Implementation some names are type-checked for specific element types.

A `Property` can be associated with many nodes, when the selectors of its
rule match many nodes. A formulae is always executed in the context of the
node to which it is applied. This means, it will yield different values,
depending on the state of the node. But, it is side-effect free. That means
a `Property` **can't** change the state of its node, it can only define its
own value. It also is `idempotent`, meaning that given the same state when
calculating the property, it will always result in the same value.

*Most importantly*, the code of a `Property Value` can **reference all the
properties of any other node in the document tree.** This opens the doors
to many powerful ways of working. We're still figuring out new ways on how
to use this and whether this was a great idea or a terrible one ;-).

### For Collaboration

One way to use this is to implement easy to use, higher level properties,
sometimes called *"parameters"* via more sophisticated, lower level properties.
In this scenario, the lower level formula would reference a to-be-defined
property — like a simple numeric value called `fontWeight` — in its calculation.
This is similar to a function that requires a specific argument and — for
example — will be **a great way of collaboration between a developer and
a designer.**

The designer will only be presented the higher level user interfaces that
are defined in CPS by the developer. But, when necessary, the designer can
**easily drill down and override any property,** either for special cases
or to change fundamental parts of the CPS.

Visit the [Vision]({{ url_for('content/Vision:index') }}) page for more ideas,
like a fully *non-destructive font-family design workflow*.


