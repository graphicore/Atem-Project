```yaml
title: Hello World, this is Atem
summary: >
    Atem-Project now has a homepage. It's a wiki-like system build
    around GitHub and made to represent and steer the project.
```

This is an interesting anouncement for me, though, all the information is
on the site itself: http://atem.graphicore.de

Here's a short round up of how we do it and what it is supposed to be:

## Tech

I made a simple static website generator, details here:
[Atem-Webgenerator](https://github.com/graphicore/Atem-Webgenerator).

It will be used from [Travis CI](https://travis-ci.org/) to continuously
update this website whenever anyone pushes to the `master` branch of
(Atem-Project)[https://github.com/graphicore/Atem-Project]. This leaves us
with a nice wiki-like system, that is controlled in the way all the other
projects we are working on, via Pull-Request and reviews and so forth.
We got accustomed to that way of working.

We used the Wiki provided by GitHub  previously, but I was unhappy with
the way it (not) counts contributions and with the limited means to
present the contents. With this approach we can have a dignified home.

## What is it good for?

There are actually two aims.

* First: the website is a haven for everyone who happens to land here.
It explains what we do, why we do it and how we can be [supported]({{ url_for('__root__', filename='support-us.md') }})
in doing so.
* Second: the website is a core planning and documentation device for Atem,
to actually get work done—like planning, communication and delegation—and
provide up to date information about the project status.


All this is described in more detail on the site itself. What's left to say is a triple **hip hip hooray³**.
