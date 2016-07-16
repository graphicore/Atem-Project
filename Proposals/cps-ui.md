# CPS User Interfaces

<iframe width="640" height="360" src="https://www.youtube-nocookie.com/embed/drdI_I78F20?rel=0" frameborder="0" allowfullscreen></iframe>

[youtu.be/drdI_I78F20](https://youtu.be/drdI_I78F20)

This is the most important feature at the time of writing this. It will
enable the CPS author to define interfaces for a project directly within CPS.
E.g. a handle to move a control point would be defined like this:

```css
element {
    onOffset: Vector 123 456;
    onUI: UIVector 100 100 onOffset;
    /*
    We should unwrap the value of onUI, a Vector, as a value for on. Thus
    there's no need for new validation/type checks in the object model.
    */
    on: onUI.value;
}
```

`onUI` would be used to define a interface that changes a vector.
That vector wold be displayed relative to `onOffset` on the canvas.

Of course, vectors would not be the only elements that could be defined. The
implementation is open for other types.

Another possibly more powerful way could be to mark any value as ui element
via a special wrapper:

```css
element {
    onOffset: Vector 123 456;
    /*
    similar like a List constructor, this style would allow us to define
    custom parameters for the ui Element. The onOffset could be optional.
    It would be much easier to add new UI types.

    This could also make the transition to a new Property Language easier,
    the added flexibility could be very helpful to get an idea of the needed
    features in the new language.
    */
    on: (UI Vector 100 100 onOffset).value;
}
```

I'll start with the first approach and then work my way up the second one.

The user interface that is supposed to create real interfaces from these
notions would be handed an OMA-Node, walk each of the entries in its
StyleDict and if it finds one value that returns a UI-Element and nothing else and
if the type of the UI-Element is supported by the user interface,
it would display it accordingly.

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
    if(!uiAPI.isUI(val))
        continue;
    // it's an UI item
    if(!isSupported(val.type))
        continue;
    uiItems.push(val);
}

// now render each UI-Item

// then, call val.update(newValue) on changes.

// The UI-Item should ideally update its position when the model updates
// but that's only good if the roundtrip time is fast enough.
// That means, the ui will only send changes, the position will then update
// on answer. Which is a bit unintuitive for ui programming, however, it
// ensures that always the correct data is visualized and it automatically
// syncs all the other instances where the uiElement is used.
// For the sake of more immediate feedback, the actually dragged ui item
// could change directly on drag (and thus be out of sync with the model)
// however, that's just a workaround, and it would need a final, explicit,
// manual step of syncing, when editing is finished.

```

A UI-Element would have a simple `update(value)` method. How value is
interpreted exactly is dependent on the type.

## The Hairy Part

Updating the value must feed back into the property value that created the
original UI-Element. Thus, we'll have to be able to go back from our "stack"
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

UI elements will only have the power to change their own `AST`, where they
have been defined, and there ideally only their `intrinsic value`.

Therefore we'll have to do some more advanced analysis, to know which part
of the `AST` has to be replaced when the UI Value is updated.

If each element in the `AST` would have it's original `AST`-index and an
element that consumed some original or created elements would have a range
from first to last consumed elements accumulated, ideally the range
works out to know which part of the `AST` have to be replace. There shouldn't
be any difficulties caused by the tokens getting reordered in the postfix
stack, check this when implementing! Comments in between might get lost
though! I don't care in this iteration, we can be smart about this later.
For the example of the UI-Vector, the vector that makes up the initial
intrinsic value may have three `Vector 10 20` or one `anotherVector` or
any number of items `Vector (10 * 3 + 4 / anotherNumber) 0` in its range.
We must also take care that we don't mix up ranges from different stacks,
when pulling in references, but that's obvious.





