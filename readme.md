# Readme for PKM-toolkit

## About Project
Bulk edit "front-matter" of markdown files easily. Since front-matter conatains meta-data of a file, being able to easily manipulate it makes file orgamization easier.

## Project Functionalities

+ List selectively your markdown notes meta-data contained in front-matter
+ Easily modify all or some notes' front-matter
+ Globbing support
+ SQL like query syntax.
+ Command line interface

## Technologies Used
`Python`, `Lark Parser`

## Demo
...

## Usage

### Select statement
Syntax
```
SELECT <properties> FROM <folder-path> [ RECURSE ] [ WHERE <expression> ] [ SORT BY <property> ]
```

+ `properties` could be "*" or case-insensitive strings
+ `folder-path` could be absolute of relative path ending in ".md". 
    + Both Windows-style and Linx-style paths are supported.
    + For paths with spaces use quotes to wrap the path.
+ `expression` could be of form `A <operator> B`
    + valid operators are \['=', '!=', '<>' (same as '!='), '>', '<', '>=', '<=', 'IN', 'NOT IN', 'REGEX MATCH', 'MATCH' (same as 'REGEX MATCH'), 'FUZZY MATCH', 'REGEX NO MATCH', 'NO MATCH' (same as 'REGEX NO MATCH')\]
    + all operators are case-insensitive
    + `B` could be a string, number, or array
    + `A` could be a string

### Insert statement
```
INSERT <scalar-json-object> INTO <files-path> [ IF EXISTS ]
```
+ `scaler-json-object` refers to json-object which does not contain any nested json-object. For e.g. `{key:{ nested-key: value }}` is not allowed. 
    + It can contain an array as a key though but only flat array (one-dimensional).

### Change directory
```CHANGE <path>```
+ `path` could be absolute of relative path ending in ".md". 
    + Both Windows-style and Linx-style paths are supported.
    + For paths with spaces use quotes to wrap the path.

## Local Installation
1. `git clone ...` then `cd` into the directory 
2. `pip install -r requirements.txt
3. `python app.py`

