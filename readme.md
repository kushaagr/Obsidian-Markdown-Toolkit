## About Project
Bulk edit "front-matter" of markdown files easily. Since front-matter contains metadata of a file, being able to easily manipulate it makes file organization easier.

## Project Functionalities

+ List selectively your markdown notes metadata contained in front-matter
+ Easily modify all or some notes' front-matter
+ Globbing support
+ SQL like query syntax.
+ Command line interface

## Technologies Used
`Python`, `Lark Parser`

## Demo
https://github.com/kushaagr/PKM-Toolkit/assets/68564934/84062977-306b-4443-bcd7-48618ae401b7

## Usage

### Select statement
Syntax

```sql
SELECT <properties> FROM <folder-path> [ RECURSE ] [ WHERE <expression> ] [ SORT BY <property> ] [;]
```

+ `properties` could be "*" or case-insensitive strings
+ `folder-path` could be absolute of relative path ending in ".md". 
    + Both Windows-style and Linux-style paths are supported.
    + For paths, with spaces use quotes to wrap the path.
+ `expression` could be of form `A <operator> B`
    + Valid operators are \['=', '!=', '<>' (same as '!='), '>', '<', '>=', '<=', 'IN', 'NOT IN', 'REGEX MATCH', 'MATCH' (same as 'REGEX MATCH'), 'FUZZY MATCH', 'REGEX NO MATCH', 'NO MATCH' (same as 'REGEX NO MATCH')\]
    + All operators are case-insensitive
    + `B` could be a string, number, or array
    + `A` could be a string
+ `RECURSE` flag traverses the `folder-path` recursively if a glob operator is specified in `folder-path` (like "./Notes/*.md")
    
#### Example
```sql
SELECT Author, tags FROM './Notes/Find Factor Algorithm.md' WHERE Author = kushaagr;
```

### Insert statement
```sql
INSERT <scalar-json-object> INTO <files-path> [ IF EXISTS ] [WHERE <expression>] [;]
```
+ `scalar-json-object` refers to json-object which does not contain any nested json-object. For example `{key:{ nested-key: value }}` is not allowed. 
    + It can contain an array as a key though but only flat array (one-dimensional).
+ `files-path` could be absolute of relative path ending in ".md". 
    + Both Windows-style and Linux-style paths are supported.
    + For paths with spaces use quotes to wrap the path.
+ `IF EXISTS` (only applicable where no globbing operator ('*') is specified) flag ensures that file exists when inserting value, by default `INSERT` command would create a new file if specified file (from `files-path`) is not found.

#### Example
```sql
INSERT {created: "2024-01-01", updated: "2024-06-01"} INTO "./Notes/*.md" WHERE datec = "2024";
```

### Change directory
```sql
CHANGE <path> [;]
```
+ `path` could be absolute of relative path ending in ".md". 
    + Both Windows-style and Linux-style paths are supported.
    + For paths with spaces, use quotes to wrap the path.

## Local Installation
1. ```bash
	git clone https://github.com/kushaagr/PKM-Toolkit.git
	``` 
	then `cd` into the directory 
2. ```sh
	pip install -r requirements.txt
	```
3. Run ```python app.py```

