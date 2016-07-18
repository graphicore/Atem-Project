# CPS User Interfaces

<iframe width="640" height="360" src="https://www.youtube-nocookie.com/embed/drdI_I78F20?rel=0" frameborder="0" allowfullscreen></iframe>

[youtu.be/drdI_I78F20](https://youtu.be/drdI_I78F20)

This is the most important feature at the time of writing this. It will
enable the CPS author to define interfaces for a project directly within CPS.
E.g. a handle to move a control point would be defined like this:

```css
element {
    onOffset: Vector 100 100;
    /*
    similar to a List constructor, this style would allow us to define
    custom parameters for the ui Element.
    It would be relatively easy to add new UI types, the `UI` constructor
    acts just as a marker and the final semantic can be figured out on a
    much higher level, in the application UI.

    This could also make the transition to a new Property Language easier,
    the added flexibility could be very helpful to get an idea of the needed
    features in the new language.
    */
    onUI: UI Vector 123 456 onOffset;
    /*
    We should unwrap the value of onUI, a Vector, as a value for on. Thus
    there's no need for new validation/type checks in the object model.
    */
    on: onUI.value;
}
```


`onUI` would be used to define a interface that changes a vector.
That vector wold be displayed relative to `onOffset` on the canvas.
`onOffset` would be optional, but useful in many cases.

To create a absolute-coordinates from such an `UI Vector` the relative part
would be added later. `on: onUI.value + onUI.arguments[1];`. In this case
all arguments to the `UI` constructor can be accessed via it's `arguments`
property, a list.


When the `ui` property here is changed by the user interface it caused, say
the coordinate is dragged by `x = -23` and `y = 44` the definition of the
CPS above is changed to:

```css
element {
    offset: Vector 100 100;
    ui: UI (Vector 100 500) offset;
    on: onUI.value;
}
```

The important part is: `ui: UI (Vector 100 500) offset;`. the old, initial
definition of the Vector `Vector 123 456` got replaced by `(Vector 100 500)`.
Note the added parenthesis, which are giving us the confidence that we don't
change the mean of the expression further.

Of course, vectors would not be the only elements that could be defined. The
implementation is open for other types.

In this case, the user interface code would make use of the `offset` argument,
or for that matter, of all the other arguments passed to `UI`.

## Using the UI values

The user interface that is supposed to create real interfaces from these
notions would be handed an OMA-Node, walk each of the entries in its
StyleDict and if it finds one value that returns a `UI-Instance` and
nothing else and if the type of the `UI-Instance` is supported by the user
interface, it would display it accordingly.

Pseudocode:

```js
// element is the OMA node

var sd = element.getComputedStyle();
  , keys = sd.keys
  , k, val
  , uiItems = []
  ;
for(k in keys) {
    val = sd.get(k);
    if(!isUI(val))
        continue;
    // it's an UI item
    if(!isSupported(val.type))
        continue;
    uiItems.push(val);
}

// now render each UI-Item

```

## The Hairy Part

Updating the value must feed back into the property value **that created the
original UI-Element**. Thus, we'll have to be able to go back from our "stack"
to the "tokenized" `AST` version and from there to a text representation.

Why is that:

### When parsing we do:

1. take a `input string`
* tokenize the input string into something like an Abstract Syntax Tree (`AST`)
* create a `postfix stack` for interpretation.

### Currently

The `input string` is what we display in the CPS-panel or
what we output when serializing the CPS.

The `AST` is just a intermediate representation, we immediately
transform it into the `postfix stack`. It's possible that we'll need a more
sophisticated `AST` representation here.

When the `AST` is evaluated, the UI element — and all other non-primitive
elements — are created in the operation. This means for us, that we can here
store a reference to the origin of the element, i.e. the `Stack` instance,
as the container Element for the `postfix stack` is called currently.

### Then

What we will to do is to use the `AST` as a source for all CPS Property
Language representations. Because, then we can change the definition of
the *intrinsic* value of the UI element in the `AST`. And all representations
can follow. Also, the `AST` is the right place to do this, because it's
**a)** good to handle from code **b)** has still enough of the syntax
information to reproduce the language.

Note that such a change has to trigger a change-event to notify all consumers
of the `Property` element. This is something that is not yet easily possible,
because the `Property` and thus `PropertyValue` elements are considered
*immutable*. When we do this we can consider them only "shallow immutable"
or we have to replace them with new Instances. The latter may still reuse
the stack of the prior version, so this could be feasible indeed.

#### Intrinsic Value

The `intrinsic value` of the UI-Element can be initiated also with a
name token that references the initial value from somewhere else. But, the
UI-Element will not change the definition of a referenced element. It will
instead replace the the name token with it's own definition of an intrinsic
value. Changing referenced values would cause confusion and unnecessary
complexity e.g. when two UI-elements reference the same value or when a
reference is defined via other references or some construct like the above
mentioned `onUI.value`.

UI elements will only have change their own `AST`/`astOperation`, where they
have been defined.

Therefore we'll have to do some more advanced analysis, to know which part
of the `AST` has to be replaced when the UI Value is updated.

## Tracking down the Source

*You can [skip](#the-hack) this paragraph if you are not interested in red herrings.*

We'll need to track back the `ASTOperation` that created the UI-Element.
Here are some early approaches and why they don't work out.

My first idea was to inject some tracking information into the postfix stack,
so when we evaluate the postfix stack, we'll be able know which operation
created the result. However, the problem lies a bit deeper than this,
because an operation that returns a `UI instance` is not necessarily the
creator of it; the creator could be another property of another rule.
At this point our tracking would have to track back the source of the
`UI instance` which could mean the traversal of several other properties
and despite that, serious changes to `StyleDict`, to make such a back
tracking possible.

Properties can be reused, we need to know the exact `PropertyDict` and
index. Otherwise, we may end up changing the wrong place! The tracking out
of the blue is hard to do with just the last node. I.e. if we are in the
right style dict and if we have the right property, we could get the
`property.value.value.ast` and walk it down until we find the right
`ASTOperation`. *However,* if the property that emitted the
UI-Element is just a getter into something else, we can't follow that.

One way could be to add all the relevant `ASTOperation` to a path array,
to record the way the property took. This would create some overhead,
though. For one, we need to create a new array for each station, copying
the current one and appending to the copy. Also, we don't really want that
kind of tracking information!

I removed a lengthy brainstorming paragraph here, what we ended up with
is [The Hack](#the-hack).

## <a name="the-hack">The Hack</a>

Believe me, I'm not very proud of this, but a series of small changes in
different modules of Atem made it possible to inject the original `astOperation`
of `UI instances` (this are instances of the `Atem-Property-Language/UI`
class) into their `UI` constructor. We want this badly because the actual
user interface code must know exactly where in the model change needs to
happen. With less information we may have to either search — this slow — or
index — needs syncing — the right place and may still face ambiguity.

### Not exactly proud.

The [solution](#interplay) that happened to turn up is very implicit.
It took a couple of small changes in several Atem submodules that don't
make much sense by themselves, just the combination of all these changes
do what I need. This means it is hard to document and easy to mess up by
an uninitiated developer. I'm writing this section to link to from all of
these not obvious situations. And maybe we can formalize the behavior in a
future iteration.

### Data Flow

What we want to achieve is constructing a `UI-instance`, like this:

```js
    return new UI(rule, property, astOperation, args);
```

This instance will be returned by a call to `styleDict.get('someName');`
and then be used to display user interfaces that change the value of the
`UI-instance`. Here, it is important to mention that we don't make any
further assumption about whether or how the `UI-instance` is used, what
type or value it represents and what its arguments are. All this is subject
to the actual user interface code. Also, here we don't really care if
is actually an instance of `UI`, it could be anything. We just use the `UI`
class to get started with something. If there are more diverse needs in the
future, similar elements can be crated using the same mechanics.

A second, even more important observation is that the property that returns
the `UI-instance` is not necessarily the property that created it, **it can
be referenced from anywhere**, and that the property that actually created
the `UI-instance` may not have done so exclusively. It could be nested into
some kind of `List` constructor, be debugged using the `_print` operator
or — in a future version of Property Language — be created in some kind of
conditional `if-else` statement.

So, what do those arguments mean:

* `rule` is the CPS rule instance that contains the `property`.
* `property` is the `PropertyName`/`PropertyValue` pair that **created** the
  `UI-Instance`. To be more precise that executed the `OperatorToken` which
  created the `UI-Instance`. The `PropertyValue` contains the Property Language
  `Expression` and that in turn is home of the `ast` *Abstract Syntax Tree*
  that we want to manipulate eventually.
* `astOperation` is the exact node in the `ast` that holds the aforementioned
  `OperatorToken`.

We need the `rule` because this is the thing that we are actually going to
change, its `PropertyDict` at `rule.properties` to be precise.
The `property` is treated as immutable and can't be changed, it can
only be replaced. We use it to find the right slot in the `rule` to change.
So this could as well be just the `propertyName` as a `key` in the `rule`
and we'd then ask the `rule` directly for the `property`.

Both, the using the `key` *and* using the `property` are subject to a race
condition. It could be that at the time when the rule is about to be changed
via a user interface, the rule has already changed and at the `key` is another
`property`. Then we say the `UI-instance` has **lost it's mandate** to change
the rule. By using just a `key` in the `UI` constructor instead of the
`property` we wouldn't be able to detect if there's another `property` for
the `key` in the `rule` now. By using the `property` we can simply check the
identity of the active `property` and if it does not match, dismiss the operation.

At this point,

1. `astToken` will be assured to be a node in `property.value.value.ast`
And we can use it to
* find the exact place in the `ast` that needs to be changed
when creating a new manipulated version of the `ast`.
* Then create a new `Expression`,
* put it in a new `PropertyValue`,
* put that in a new `Property` with the same `PropertyName` of course
* and then *finally* change the `rule` by overriding the old `property` with the new one.

Subscribers will be informed and the model will start updating.

### <a name="interplay">Interplay</a>


As mentioned, the call to `new UI` is made within an instance of `OperatorToken`
and in the within the concrete implementation of the `OperatorToken` we
need to get our hands on all three of `rule`, `property`, `astOperation`.


#### Changes to `Atem-CPS/CPS/StyleDict`

The first two arguments, `rule` and `property`, are known on execution
time by the `styleDict` that actually runs the `evaluate` method of the
`PropertyValues` instance of `Expression`. We have always had a way to
ask the `styleDict` directly for data: the `getAPI`, which is given as an
argument to  `expression.evaluate` by `styleDict`, has exactly that purpose.
All I had to do was adding a method `getAPI.getCurrentPropertyAndRule()`
to return both items in question.

What's left to do is to get our hands on the `astOperation` that is
responsible for the creation of the `UI-instance`.

#### Changes to `Atem-Property-Language/parsing/OperatorToken`

At the lowest level the `OperatorToken` now accepts a new flag, `*optional*`,
which injects the third argument the the call to `execute` into the
concrete implementation. Hence `operatorToken.execute(getAPI, _args, optional)`
has now a third  argument, literally called `optional`.
There was the flag `*getApi*` before which would make `OperatorToken` inject
the `getAPI` as first argument into the call to the concrete operator
implementation. if `*getApi*` is set `optional` will be injected as second
argument, otherwise as first, followed by the regular arguments.
The name `optional` is vague on purpose, because I don't want it to be
pinned down to a too specific use case by a mere naming decision.


#### Changes to `Atem-Property-Language/parsing/Parser`

In order to get the `astOperation` to the `execute` call of the `OperatorToken`
we have to keep it around until the call to `execute` is made. The first
part of this is achieved by adding a flag `keepASTOperations` to
`parser.astToPostfix (node, keepASTOperations)`. Without the flag being
set, `astToPostfix` unwraps the `operatorToken` from the `astOperation`
and pushes it onto the resulting, flat *postfix stack*. With the flag,
this "unwrapping" is not performed and the `astOperation` ends where
previously the `operatorToken` would have been.


#### Changes to `Atem-Property-Language/parsing/ASTOperation`

Fortunately the evaluation of the *postfix stack* is straight forward and
not particularly complex. As such, for the `ASTOperation` to behave like
the `operatorToken` that it replaces was a pretty simple application of duck
typing. Two properties `ejects` and `consumes` where implemented as getters
and read directly from the original `operatorToken`. The method
`astOperation.execute(getAPI, args)` however does not simply forward the
call to the `operatorToken`, instead, it augments the call to inject
itself: `return this.operator.execute(getAPI, args, this);`.

This was the last in the series of small changes, needed in order to
know all of `rule`, `property` and `astOperation` at the time of constructing
the `UI-instance`. Eventually this enables the CPS-UI feature and probably
more direct interaction with the CPS Property Language in the future.






