# json

A JSON parser and serializer for Carp.

## Installation

```clojure
(load "git@github.com:carpentry-org/json@0.5.0")
```

## Usage

### Parsing

Parse a JSON string into a `JSON` value using `JSON.parse`:

```clojure
(match (JSON.parse "{\"name\": \"carp\", \"version\": 1}")
  (Result.Success j) (println* &j)
  (Result.Error e) (IO.errorln &(JSON.parse-error-str &e)))
```

`JSON.parse` returns a `(Result JSON ParseError)`. The error carries both
a `ParseErrorKind` (one of 16 variants describing what went wrong) and a
byte position. Use `JSON.parse-error-str` to format it for display, or
`match-ref` on the kind to react programmatically.

### Building JSON values

You can construct JSON values directly:

```clojure
(def j (JSON.obj [(JSON.entry @"name" (JSON.Str @"carp"))
                  (JSON.entry @"version" (JSON.Num 1.0))
                  (JSON.entry @"active" (JSON.Bool true))]))
```

Or convert native Carp values via the `to-json` interface, which is
implemented for `Bool`, `Int`, `Long`, `Float`, `Double`, `String`, and
`Array`:

```clojure
(to-json @"hello")    ; => (JSON.Str "hello")
(to-json [1 2 3])     ; => (JSON.Arr [...])
(to-json [@"a" @"b"]) ; => (JSON.Arr [(JSON.Str "a") (JSON.Str "b")])
```

### Serialization

Convert any `JSON` value back to a string with `str`:

```clojure
(match (JSON.str &j)
  (Result.Success s) (println &s)
  (Result.Error e) (IO.errorln &(JSON.serialize-error-str &e)))
```

`JSON.str` returns a `(Result String SerializeError)`. It only fails when
a `JSON.Num` contains NaN or infinity, neither of which is representable
in JSON.

### Accessing values

```clojure
; Look up a key in an object
(JSON.get &j "name")             ; => (Maybe.Just (JSON.Str "carp"))

; Index into an array
(JSON.nth &arr 0)                ; => (Maybe.Just ...)

; Nested key lookup
(JSON.get-in &j &[@"data" @"users"])

; Extract typed values
(JSON.as-str &(JSON.Str @"hi"))  ; => (Maybe.Just "hi")
(JSON.as-num &(JSON.Num 3.14))   ; => (Maybe.Just 3.14)
(JSON.as-bool &(JSON.Bool true))  ; => (Maybe.Just true)

; Compare structurally: arrays by order, objects independent of member order
(= &(JSON.Num 1.0) &(JSON.Num 1.0))  ; => true
```

### JSON Pointer

`JSON.Pointer` implements [RFC 6901](https://www.rfc-editor.org/rfc/rfc6901),
which addresses a value inside a document with a string like `/foo/0/bar`:

```clojure
(JSON.Pointer.get &doc "/foo/0")  ; => (Maybe.Just ...)
(JSON.Pointer.get &doc "")        ; => the whole document
(JSON.Pointer.get &doc "/a~1b")   ; => the value under the key "a/b"
```

Array tokens must be `0` or a positive integer without a leading zero; the
`-` end-of-array token, out-of-range indices, and invalid pointers all return
`Nothing`. Use `escape`/`unescape` to build or decode a single reference token
(`~` becomes `~0`, `/` becomes `~1`):

```clojure
(JSON.Pointer.escape "a/b")     ; => "a~1b"
(JSON.Pointer.unescape "m~0n")  ; => "m~n"
```

### JSON Patch

`JSON.Patch` implements [RFC 6902](https://www.rfc-editor.org/rfc/rfc6902),
which expresses a change to a document as a JSON array of operation objects
addressed by JSON Pointer:

```clojure
(def patch
  (Result.unsafe-from-success
    (JSON.parse "[{\"op\": \"add\", \"path\": \"/tags/-\", \"value\": \"lisp\"},
                  {\"op\": \"replace\", \"path\": \"/version\", \"value\": 2},
                  {\"op\": \"move\", \"from\": \"/old\", \"path\": \"/new\"}]")))

(match (JSON.Patch.apply &doc &patch)
  (Result.Success patched) (println* &patched)
  (Result.Error e) (IO.errorln &(JSON.patch-error-str &e)))
```

All six operations are supported. `add` inserts into an array (shifting the
rest right, with `-` appending) and inserts or replaces an object member;
`remove` and `replace` require the location to exist; `move` may not move a
location into one of its own children; `test` compares the addressed value
with `JSON.=`. The empty pointer `""` addresses the whole document.

Patches are atomic: if any operation fails, the returned `PatchError` names
the index of the failing operation and the input document is left untouched.

Two limits bound the work a patch can ask for, since `copy` duplicates a
subtree and a short patch could otherwise build a very large document. An
operation that would nest the document deeper than `JSON.parse` accepts is
rejected with `DepthLimitExceeded`, and a patch may insert at most
`json-max-patch-nodes` nodes beyond the combined size of the document and the
patch before `SizeLimitExceeded`. Neither binds on a hand-written patch.

### JSON Merge Patch

`JSON.merge-patch` implements [RFC 7386](https://www.rfc-editor.org/rfc/rfc7386),
which is what an HTTP API almost always means by `application/merge-patch+json`.
The patch is a document shaped like the target, and merging it replaces the
members it mentions:

```clojure
(def doc (Result.unsafe-from-success (JSON.parse "{\"a\":1,\"b\":{\"c\":2}}")))
(def patch (Result.unsafe-from-success (JSON.parse "{\"b\":{\"c\":3},\"d\":4}")))

(JSON.merge-patch @&doc &patch)  ; => {"a":1,"b":{"c":3},"d":4}
```

A patch that is not an object replaces the target outright, a `null` member
deletes that key, and a target that is not an object is treated as an empty
one. Arrays are replaced whole, never merged element by element.

`JSON.merge-diff` builds the smallest patch taking one document to another,
emitting `null` for dropped members and omitting unchanged ones:

```clojure
(JSON.merge-diff &doc &other)      ; => {"b":{"c":3},"d":4}
(JSON.merge-patch @&doc &(JSON.merge-diff &doc &other))  ; => other
```

Two things the format cannot express: setting a member to `null`, since that
spelling already means delete, and reaching inside an array. So a `merge-diff`
whose target introduces a `null` member does not survive the round trip, and
an array edit costs the whole array. Reach for `JSON.Patch` when you need
either.

### Type predicates

```clojure
(JSON.null? &(JSON.Null))  ; => true
(JSON.bool? &(JSON.Null))  ; => false
(JSON.num? &(JSON.Num 1.0)) ; => true
(JSON.str? &(JSON.Str @"")) ; => true
(JSON.arr? &(JSON.Arr []))  ; => true
(JSON.obj? &(JSON.Obj {}))  ; => true
```

## The JSON type

`JSON` is a sum type with six variants:

```clojure
(deftype JSON
  (Null [])
  (Bool [Bool])
  (Num [Double])
  (Str [String])
  (Arr [(Array (Box JSON))])
  (Obj [(Map String (Box JSON))]))
```

Arrays and objects contain `Box`ed values because the type is recursive.

## Testing

```
carp -x test/json.carp
```

## Benchmarking

```
carp -x bench/json_bench.carp
```

<hr/>

Have fun!
