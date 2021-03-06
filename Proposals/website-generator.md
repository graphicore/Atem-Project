```yaml
testing: True
```

# Atem Project Website Generator

The Atem website is generated by the code in this directory.
Ideally the website generator will be available as a shared project for
all other Atem subprojects as well. This is pretty similar to Jekyll, but
with much more specific site genrating capabilities.

## Tasks:

 * The website generator can extract information from a git repository and create webpages for it
 * Site generation should be totally content driven. I.e. the contents of a git repository
   can be used to build a site, the generator does not need to reside in the repository.
 * Special site content directories can be used to build generic websites.
 * Future: Markdown files found in the repository can be included as HTML-pages.
 * Future: JavaScript API documentation can be generated directly from the repository (this will be quite a task)
   would be nice to have it for all of the Atem projects.
 * Future: A page describing and linking the dependencies can be generated from the `bower.json` files
 * Future: A semi automated way to create a change-log report from git semver-tags plus git commit
    messages should be developed. I.e. if there is no change-log file for a semver-tag, it will be
    created as a simple json list (treating the contents as markdown), showing all commit messages in a list
    from that semver-tag to the semver-tag before (ignore the actual semver value, use just the order of
    appearance as the versioning itself should just appear in the right order).
    Then, manual labor could be applied to make a condensed version, or to group commits into
    top level entries. That hand crafted version would be preferred over a generated version.
    So, it must be possible to generate from a cli a starting point per semver-tag or for all
    on disk missing semver-tag files.

Since the list above mixes two different concerns AND a third concern, which is "application-deployment"
is missing we need to put names on all of this:

* Documentation
* API-Documentation
* Project website
* Application deployment/distribution

Where Documentation and Project website may appear in the same context.
Well, all should be accessible via the Website somehow, so it must be possible
to link and also the Navigation should at least on a high level reflect
that.

API-Documentation will come later. Distribution will also come later, and
not in Atem-Project at all.

There must be a directory structure to cope with the different parts of
the page:

```blub
index.html
js ?
css
assets ?
dist/
    # built applications ready to use
    v0.0.1
    v0.1.0
    ...
web/
    # This is specifically authored web content
    ...
docs/
    # docs will be authored similar to web, but may include stuff like a semver
    # directory layer
    # that also means, that to create older docs, we'd have to check out an
    # older tag ...
    # also, the last tag is almost always an old one and most of the time
    # `current` (rather HEAD) has no tag at all.
    # Checking out old versions may be problematic in a running build as
    # well. We could always build to `current` and then push a copy of
    # `current` to a tag folder if the tag === HEAD. That way, we would
    # also "freeze" that old documentation.
    v0.0.1
    ...
```

I think `dist` won't be handled by this in the beginning, but actually having
a central build tool for distribution, documentation and website (communication)
would be great

A blog with rss feed would be neat! Website entries marked as "news"


The plan:
 * The overall structure could be a per output directory/target
configuration.
 * Inputs are also directories, per input source a router could be defined
  that knows how to interpret different file-suffixes, i.e.
  .md will be put into the appropriate template and interpreted as markdown
  , result:  outputdir/path/to/file.md.html
  -> I want also a metadata enhanced file format
  -> like this: https://jekyllrb.com/docs/frontmatter/
  -> even a .md file may have this frontmatter, configurable?
        -> ducktyping: if it is separated like frontmatter and if it parses as yaml ...

 * The way frozen flask works we can either let the tool detect pages to generate
   when we generate the url using `url_for()` OR we define `url generators".
   I want a config driven url generator (or maybe more, to separate concerns)
   That walks the configured directories for a target and yields a suitable
   url for each target, i.e. `{targetname}/path/to/file.html`
   Then, the also configured handler for these paths would be invoked.
   It must be OK for a handler to discard a url (returning 404 or whatever)
   which probably shouldn't even be logged, as this is expected behavior.
   The handler must dispatch the content to a renderer etc.
 * How to do sitemap or a linklist? This would probably be the same code
   as the url generator, including the part where the handler decides whether
   to render the url or not. Thus, that decision making should be a shared
   function, and we can already run it in the url generator. This makes it
   easier to handle 404 as well (at least it will happen less).
 * the main menu will be authored by hand. Also, it shouldn't go too deep
   into directory structures ...
   If we need more than a simple directory listing link list, we should then
   come up with a plan. right now, something like the output of `$ tree` could
   be used for directory crawling outputs.






## remember setup steps for travis ...

```
# http://flask.pocoo.org/docs/0.10/installation/#installation
# Atem-Project/website/generator$ virtualenv venv
# need py >=3 anyway, so pyvenv seems better than virtualenv
# Atem-Project$ pyvenv-3.5 website/generator/venv
Atem-Project$ . website/generator/venv/bin/activate
Atem-Project$ pip install wheel
Atem-Project$ pip install Flask
Atem-Project$ pip install pyyaml
Atem-Project$ pip install misaka # markdown
Atem-Project$ pip install houdini.py # html escaping in mardow synax highlighter
Atem-Project$ pip install Pygments # syntax highlighting
Atem-Project$ pip install Frozen-Flask
```

## custom template variables

if <code>&#96;&#96;&#96;yaml</code> is the first thing in the file
and a <code>&#96;&#96;&#96;</code> is present in a subsequent line
everything in between is attempted to be parsed as yaml and if successful
used as template variables and removed before rendering the document.
Otherwise, the block remains unchanged in the document. This is cool,
because github will syntax highlight the configuration properly:

```yaml
this: will
be: configuration
```

## custom templates

I want the repository to be able to define it's own templates.
So, in the repositories config file, a template directory can be specified
and that will be used to look up templates prior to the default directory
of the generator.
This will also make it possible to inherit from generator templates, if they
are not overridden by the app.
Datatypes in the configuration can specify their own templates, and maybe
the document *custom template variables* could even override that.

# Menus

We have a list of all links available from the url generator for Frozen Flask
That is a great way to create one unified menu class, that basically can
render the whole sitemap as a nested menu, marking the currently displayed
page as the active one.
There will be a way, like selectors, to define which menus should be output,
so we can show different menus on different pages.
The menu class will not actually render the links, instead it will just provide
structure and contents. The Rendering will be done in jinja2 templates.




