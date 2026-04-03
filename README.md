# json

A JSON parser and serializer for Carp.

## Installation

```clojure
(load "git@github.com:carpentry-org/json@0.1.0")
```

## Usage

### Parsing

Parse a JSON string into a `JSON` value using `JSON.parse`:

```clojure
(match (JSON.parse "{\"name\": \"carp\", \"version\": 1}")
  (Result.Success j) (println* &j)
  (Result.Error e) (IO.errorln &e))
```

`JSON.parse` returns a `(Result JSON String)`. On failure, the error contains a
message describing what went wrong.

### Building JSON values

You can construct JSON values directly:

```clojure
(def j (JSON.obj [(JSON.entry @"name" (JSON.Str @"carp"))
                  (JSON.entry @"version" (JSON.Num 1.0))
                  (JSON.entry @"active" (JSON.Bool true))]))
```

### Serialization

Convert any `JSON` value back to a string with `str`:

```clojure
(JSON.str &j) ; => "{\"name\":\"carp\",\"version\":1.000000,\"active\":true}"
```

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
