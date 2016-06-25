# Developer Mindset

An attempt to get you into a good mood for development in the Atem-Project.

*Never finished. Additions welcome.*

## Be Autonomous

Learn how things are done in Atem by reading code and documentatin and
by understanding it for yourself. If you have trouble understanding the
JavaScript of Atem, go to [MDN](https://developer.mozilla.org/en-US/)
(nowhere else) and learn the syntax and API. *Don't let us find the
documentation for you.* It doubles the time wasted for the task and you
learn less.

If there's no documentation and you have a hard time understanding something,
try to **formulate a most informed question.** If that did not help you
already we'll be glad answering you.

If you just had a fundamental breakthrough in understanding something in
Atem, **be a hero and write a short article** to share in the
[Concepts]({{url_for('content/Concepts:index')}}) or
[Manuals]({{url_for('content/Manuals:index')}}) section.

## Look at Atem-Project in its entirety

Always consider the whole Atem-Project, not just your specific problem at
hand. Many solutions may be better/leaner if applied in a lower level of
the project. Before you start to hack a fix around some bad behavior of a
dependency, **consider fixing the dependency.**

This is important, because of the subproject-structure of Atem it is likely
that you think fixing the hindrance is "to much effort" or whatever. But
in fact it will in the most cases **improve the project and make it more
complete.** Also, you will learn more about the project structure and
eventually start taking part in forming the lower level structures of the
project.

A good starting point to fix lower level code could be to make a
clean sub-class of the module in question, within your project, and implement
the changes needed there (or do monkey-patching if there's no better way).
That way, discussing the upstreaming of the changes will be easy and
straight forward and you can keep on going without a pull request, maybe
file an issue and point to the changes needed.

For the project, **the most valuable thing you can give is a pull request.**
But this kind of contribution can slow things down; because there is peer
review involved: people reading the code, discussions, requests for changes
etc. If, for whatever reason you lack the time for a proper pull request
process, it is OK to do it as described above. Important is that you don't
take the foundation you build upon as given and work around weaknesses,
instead, **improve the foundation**.


## Write code for other people to read

When writing code try to be short and precise but not cryptic. The most
important function of your code is to be read by other developers, **write
code as if you want to explain something to a human being.**

## Break Stuff

To make things better you got to break things. [Don't be afraid to break stuff](https://blog.codinghorror.com/dont-be-afraid-to-break-stuff/),
it's an opportunity for you to learn and it's probably the right way to
achieve your goal.

We use the concept of "private" properties/functions/methods—marked with
an `_` underscore as the prefix of a name—_that's **invaluable** when refactoring
code._ Be reckless when changing private APIs, be careful when changing public
APIs. Use `grep`, consider all users of a public APIs, see how the public APIs
are used. **By default, add private APIs**, only add public APIs when they are
really needed in the very moment. *Don't presumably add new public APIs,*
unless it's really core to how your module is to be used.


After breaking things you should still try to make a Pull Request that does
not break things "too much", or at least inform us about things you broke
in your PR. The point is that **your result will be better if you did break
stuff in the process.**

<a
    href="https://xkcd.com/1428/"
    ><img
        src="//imgs.xkcd.com/comics/move_fast_and_break_things.png"
        title="I was almost fired from a job driving the hearse in funeral processions, but then the funeral home realized how much business I was creating for them."
        alt="Move Fast and Break Things"
        /></a>

