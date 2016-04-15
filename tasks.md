# Tasks

This is a list of things to do in the Project. Some of the tasks are easier
to do and some require deep insights to the project. This is targeted at
everybody who wishes to become a contributor, but doesn't know where to start.

If you think you can handle one of these tasks or if you have a new addition to
the list, contact us via the issue tracker or send a mail to Lasse.

Detailed descriptions may be linked from here, to the Atem subproject, to
an issue in the issue tracker or to a file in the [Proposals](./Proposals)
directory

## Administration, Documentation and Publications

 * Write contents for the [website](http://atem.graphicore.de), that is more general information and easier to consume than in this repository. Targeted at people who just want to know what's going on. Create interest.
 * A general Atem project documentation, explain how it all plays together (Maybe sub-project wise: dependecies and depndants).
 * Find rules for contribution and improve them over time.
 * Atem sub-projects should follow the same style, so that we can deploy the same QA/build/production tools etc.
 * Inline CPS examples and documentation (Bauhaus Emblem Font, Atem-MOM-Developer-Tool).
 * "How-To" and "Getting Started" guides.
 * Spread the word and see if we can reach new contributors.
 * Do we need a FAQ?
 * Each sub project should have some more detailed tasks to get started.

## Programming

 * Build sdripts/tools for the applications.
 * Can we do reasonable well API-documentation generation from our sources?
 * A generic base for all Atem applications, that includes solutions to serve locally, export for a simple http-server, launch as a Desktop Application (e.g. using QT5 qith V8).
 * Testing infrastructure that works for all subprojects the same (AMD, Node+Web, Coverage, more as in ufoJS than in Metapolator).
 * Generate NPM packages from our AMD modules. (Could also be harmful: for the portability of new packages created with npm in mind to the browser, so maybe don't!?)
 * Quality assurance tools, like jshint checks via Travis, testing.
 * Atem-IO needs an interface that makes its flexibility available for use in application. (File and Filesystem Manager)

## Programming (Big Tasks)

 * Undo/Redo/History Management
 * Broker based multi-user editing.
 * Use Webworkers/Parallel computing
        * for faster and/or not-ui-blocking exports
        * the main application may run, like the multiuser Broker, in a different process or Webworker
 * Spec and implement Property Language 2.
 * OMA/MOM-Plugins via new element types. This is a low hanging fruit thing. It's rather easy to come up with a new element and to include it, let's say if a plugin structure is available (it's easy at the moment, but imho not a good plan to pull
everything in, for maintenance reasons). So, we could have a "Serifs" plugin, that is really just drawing serifs, reading it's arguments from CPS of course. And that way, via CPS, everything is connected. You could just use the left and right on curve points of your penstroke, to tell the serif where to start, things like that. Also, adding ui definitions to CPS would make this a blast ;-) This could relate to the parametric design stuff Tamir Hassan worked on with Roger Hersch in Lausanne ([ngtrrpf_10.pdf](http://lspwww.epfl.ch/publications/typography/ngtrrpf_10.pdf)) It could make very creative fonts possible.
 * UI-elements defined via CPS-values
 * Smarter "Essence-inheritance" to do things like: patch-structures, MOM-Patch-Masters, Metacomponents, etc. This is all things that can be done by reusing any MOM structure. Eg, this is the way to reuse a complete master, instead of copying the whole tree. But in the end really it is just copying the tree, but done in managed way that keeps change-operations in sync. The latter is very close to what we do now. A mechanism like this is part of the core.
 * Improve performance, therefore analyze current performance killers.
 * Components with interpolation axes (useful for CJK fonts)
