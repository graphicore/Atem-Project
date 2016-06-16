```yaml
link_name: Vision
```

# Vision

This is where we are and where we are going. Have a look at our
[history]({{ url_for('content/Vision', filename='history.md') }}) to see where
we are coming from. Take this as **the bigger picture**. We will have detailed
roadmap documents published for shorter term goals.


## Where We Are

We have three Applications to demo the state of the technology.

* <a href="http://metapolator.com" target="_blank">Metapolator</a> a next generation font-family
authoring tool. It has a great vision and is in a minimal viable product state.
* The <a href="http://metapolator.com/developer-tool/" target="_blank">MOM-Developer-Tool</a>
which reveals a lot of the inner workings of Metapolator and has the potential to grow into
our generic platform base.
* The <a href="https://github.com/graphicore/Bauhaus-Emblem-Font" target="_blank">Bauhaus-Emblem-Font</a> (not online yet)
Which serves three purposes:
    1. An *editor for type on a circle* as seen on the Bauhaus-Emblem of Oskar Schlemmer,
    * a *tech-demo for Atem* and
    * an *initiation and learning tool for CPS*.

Our code-base is in a good shape for the moment. It's split up into modules
with clearly defined dependencies. We have solved some harder problems that
occur when JavaScript is used in different environments than just the browsers,
like node.js command-lines e.g. `Atem-IO`.

In presentations or in face-to-face dialogues, we get generally good to
positively excited feedback when we show what we have.

## Where we ultimately end up

The *Developer-Tool* type of applications will transform into a **polymorphic
platform**. We'll have it fully customizable and most of it working via
plugins. We may end up having—similar to Linux-distributions—specializations
of it, particularly well fitted for a specific task. E.g. **Metapolator**,
which is now "custom made", should be built on this platform.

A core feature will always be having the setup for experimentation and exploration,
without the need for polished UI and UX, to allow fast paced development.

### Font-Authoring

We'll have a **drawing tool**, that'll allow drawing fonts with our object model
from scratch. It will be a comfortable tool to work with for type designers.
This will lead to a **fully non-destructive workflow.** I.e. when a master is
changed, the changes will *ripple through the instances* that inherit from
that master. Fixes for problematic parts after interpolation will *persist*
and interpolation will happen *continuously*.

The Metapolator-Object-Model (MOM) and Cascading-Properties-Sheets (CPS)
will be used as the common base. We'll have different general directions
to explore parametric type design.

* One general approach is having **generic elements**, like our `<penstroke>`
or other generic drawing abstractions and making these work in the parametric font.
A great deal for this will be the implementation of a concept with the working
title **"meta-components"**, which will make a reuse straight forward. E.g. a serif,
that is made from a generic `<contour>` element and enhanced with custom
`CPS`-formulae can be shared across different glyphs and may still get assigned
specific overrides for each instance.
* Another general approach is using **specialized elements** that can be loaded
as plugins. E.g. one element-type that draws only serifs, one element-type
that draws only shoulders and so on.
* The third approach will be **combining all other directions**. The way CPS
works allows us to mix and match any elements in the object model and make them
work together.
* We are **open for more new ideas** on our journey.

### New Domains

It's easy to come up with *custom Object-Models* based on our Object-Model-API (OMA)
this entails having the fully functional CPS engine available. All the generic
tools that are not specific for the MOM will be available: *loading/saving*,
*history management* and the *Developer-Tool* platform with all the *CPS-Tools*
come for free.

We'll work on inspiring and supporting other people to *approach new domains*
using our tooling. The [Bauhaus-Emblem-Font](https://github.com/graphicore/Bauhaus-Emblem-Font)
is an example and it should be possible to take it further into a parametric **illustration
tool**.

We've been talking to the [Valentina Project](http://valentina-project.org/)
an *Open Source (fashion-)pattern drafting software*. It would be a blast to
come up with a **pattern drafting software** based on the OMA, i.e. packed with
`<collar>` elements and so on.

Conceptually, there's nothing in Atem technology limiting it to be used for
**non-graphical** applications like **audio** or adding a dimension and
exploring **3d modeling**. But, we will have to improve our Property-Language
to be up to the task.

## How we get there

From here, start to explore the [Project]({{ url_for('content/Sub-Projects:index') }})
and see what we make out of our plan, or consider [supporting us]({{ url_for('__root__', filename='support-us.md') }}) and
[collaboration]({{ url_for('__root__', filename='collaborate.md') }}) if you want this
vision to come true.
