# Atem Shell

*This is a stub*

Initially posted [here](https://plus.google.com/+LasseFister/posts/heZ4SL6u5q7).

This needs to be fleshed out:

> I'm trying to figure out some architectural direction for the Atem-{CPS/MOM/*}-Developer-Tool family of applications.
>
>Since the CPS-Panel tool is a bit slow loading (I blame AngularJS for this, creating all these directives and scopes etc.) I think a nice move would be to try: ngReact https://github.com/ngReact/ngReact which brings reactJS into Angular.
>
>Angular can still be used whenever sufficient. I think using https://angular-ui.github.io/ui-layout/ could be nice tool to make a grid layout happen. I'd like to see drag and drop restructuring and adding/removing of available widgets within the ui-layout in the future. Probably some user enabled wiring to listen on signals from different sources.
>
>Probably adding something like https://github.com/postaljs/postal.js into the mix.
>
>The applications would be highly customizable to the task at hand.
>
>Is anyone interested in helping planning this?﻿

Also, in [Vision]({{ url_for('content/Vision:index') }}) it says:

> ## Where we ultimately end up
>
>The *Developer-Tool* type of applications will transform into a **polymorphic
platform**. We'll have it fully customizable and most of it working via
plugins. We may end up having—similar to Linux-distributions—specializations
of it, particularly well fitted for a specific task. E.g. **Metapolator**,
which is now "custom made", should be built on this platform.
>
>A core feature will always be having the setup for experimentation and exploration,
without the need for polished UI and UX, to allow fast paced development.

Which this proposal should support.


