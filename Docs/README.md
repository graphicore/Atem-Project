```yaml
user_menu: False
docs_menu: True
link_name: Project
```

# Documenting Expressive Models

Documentation on several levels is the single most important communication
channel.

The time that is available to produce good documentation is however limited.
Another factor is the up-to-dateness of documentation. Unless there's no **reasonably
stable state™** of a subject to be documented, it is pointless to put a lot of time into
making documentation about it.

## How this is organized

The structure of the documentation pages reflects the field of tension between
the need of documentation versus the inability to provide up-to date adequate documentation
in a rapidly changing project.

* **[Concepts]({{url_for('content/Concepts:index')}})** contains a high level documentation to give an overview about architecture,
  design ideas etc. that is actually used in the project. This is meant to help understanding
  when diving into the code. Since this is very high level the documentation in here won't change
  so fast and it is more save to put time into writing it.
* **Proposals** is our *main tool to guide progress* in the Atem-Project. These are documents that
  describe the planning of additions, enhancements or changes to the project. They are the
  base of technical discussions and later guidance for the implementation. After implementation
  they will serve as documentation for the design choices that have been made.
* **Manuals** contains step by step guides to accomplish certain tasks. These may become
  outdated sooner or later, however, they should have an audience by the time of their
  writing, that means, the demand should justify the effort. Updating of manuals will
  also happen if there is actual demand. Often, an old manual can still be a valuable source
  of knowledge.
* **API** documentation is a need that we have. This is a navigational dead end to raise
  awareness for our need of an *automated system* to generate well structured API documentation
  from our source code, where then as well the source codes will have to be changed to feed
  into that system. This item should link straight to a proposal document.



