# json

A JSON parser and serializer for Carp.

## Installation

```clojure
(load "git@github.com:carpentry-org/json@0.2.1")
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
a `ParseErrorKind` (one of 15 variants describing what went wrong) and a
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
```

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
