"""D426 course pack content: sample databases, concepts, blueprint,
and all question generators. Self-contained (no core imports needed)."""
import datetime as _dt
import random

# ---------------------------------------------------------------------------
# Sample databases — schemas mirror the course's own lab and example tables.
# All scripts are written in MySQL dialect and run through the compat layer.
# ---------------------------------------------------------------------------

SAMPLE_DBS = {}

SAMPLE_DBS["stable"] = """
-- The riding-stable database from the chapter 2 labs
-- (Horse: 2.13-2.16, Student: 2.17, LessonSchedule: 2.18, joins: 3.11-3.12)
CREATE TABLE Horse (
  ID INT AUTO_INCREMENT,
  RegisteredName VARCHAR(50),
  Breed VARCHAR(20) CHECK (Breed IN ('Egyptian Arab','Holsteiner','Quarter Horse','Paint','Saddlebred')),
  Height DECIMAL(3,1) CHECK (Height BETWEEN 10.0 AND 20.0),
  BirthDate DATE CHECK (BirthDate >= '2015-01-01'),
  PRIMARY KEY (ID)
);
CREATE TABLE Student (
  ID INT AUTO_INCREMENT,
  FirstName VARCHAR(30),
  LastName VARCHAR(30),
  PRIMARY KEY (ID)
);
CREATE TABLE LessonSchedule (
  HorseID SMALLINT UNSIGNED NOT NULL,
  StudentID SMALLINT UNSIGNED,
  LessonDateTime DATETIME NOT NULL,
  PRIMARY KEY (HorseID, LessonDateTime),
  FOREIGN KEY (HorseID) REFERENCES Horse(ID) ON DELETE CASCADE,
  FOREIGN KEY (StudentID) REFERENCES Student(ID) ON DELETE SET NULL
);
INSERT INTO Horse (RegisteredName, Breed, Height, BirthDate) VALUES
  ('Babe', 'Quarter Horse', 15.3, '2015-02-10'),
  ('Independence', 'Holsteiner', 16.0, '2017-03-13'),
  ('Ellipse', 'Egyptian Arab', 14.9, '2016-12-22'),
  ('Five', 'Paint', 17.0, '2018-08-25'),
  ('Rocket', 'Saddlebred', 15.8, '2019-05-01'),
  (NULL, 'Quarter Horse', 15.6, '2020-06-16'),
  ('Nutmeg', 'Paint', 14.2, '2015-09-03'),
  ('Dakota', 'Holsteiner', 16.4, '2021-01-28'),
  (NULL, 'Egyptian Arab', 13.8, '2019-10-11'),
  ('Comet', 'Quarter Horse', 15.0, '2022-04-19');
INSERT INTO Student (FirstName, LastName) VALUES
  ('Joan', 'Adams'), ('Mo', 'Woods'), ('Tessa', 'Nguyen'), ('Marcus', 'Lee'),
  ('Priya', 'Patel'), ('Sam', 'Okafor'), ('Lena', 'Fischer'), ('Diego', 'Ramos');
INSERT INTO LessonSchedule (HorseID, StudentID, LessonDateTime) VALUES
  (1, 1, '2026-02-01 09:00:00'),
  (1, 3, '2026-02-01 10:30:00'),
  (2, 2, '2026-02-01 09:00:00'),
  (3, 4, '2026-02-02 14:00:00'),
  (3, NULL, '2026-02-03 09:00:00'),
  (4, 5, '2026-02-03 10:30:00'),
  (5, 1, '2026-02-04 09:00:00'),
  (5, 6, '2026-02-05 15:00:00'),
  (7, 2, '2026-02-05 16:30:00'),
  (7, 7, '2026-02-06 09:00:00'),
  (8, 3, '2026-02-06 10:30:00'),
  (1, 5, '2026-02-07 09:00:00'),
  (2, 4, '2026-02-07 10:30:00'),
  (5, 8, '2026-02-08 11:00:00');
"""

SAMPLE_DBS["movies"] = """
-- The Movie/Streaming schema from the D426 office-hours DDL drills
CREATE TABLE Streaming (
  StreamID INT,
  ServiceName VARCHAR(20),
  MovieSales BIGINT,
  Year INT,
  PRIMARY KEY (StreamID)
);
CREATE TABLE Movie (
  MovieID INT AUTO_INCREMENT,
  Title VARCHAR(50),
  Genre VARCHAR(20),
  ReleaseDate DATE,
  StreamID INT,
  PRIMARY KEY (MovieID),
  FOREIGN KEY (StreamID) REFERENCES Streaming(StreamID)
);
INSERT INTO Streaming VALUES
  (1, 'StreamFlix', 5200000, 2024),
  (2, 'CineMax+', 3100000, 2024),
  (3, 'PopcornTV', 1450000, 2023),
  (4, 'NebulaPlay', 900000, 2025);
INSERT INTO Movie (Title, Genre, ReleaseDate, StreamID) VALUES
  ('Rogue Wave', 'Action', '2019-06-14', 1),
  ('The Quiet Orchard', 'Drama', '2016-11-02', 2),
  ('Byte Me', 'Comedy', '2021-03-26', 1),
  ('Starlight Protocol', 'Sci-Fi', '2023-07-21', 4),
  ('Cellar Door', 'Horror', '2018-10-05', 3),
  ('Second Serve', 'Comedy', '2015-04-17', 2),
  ('Iron Meridian', 'Action', '2022-05-06', 1),
  ('Paper Lanterns', 'Drama', '2020-02-14', NULL),
  ('Warp Harvest', 'Sci-Fi', '2024-08-30', 4),
  ('The Last Ledger', 'Drama', '2017-09-08', 1),
  ('Gravity Well', 'Sci-Fi', '2019-01-25', NULL),
  ('Midnight Recess', 'Horror', '2024-10-31', 3),
  ('Fast Compile', 'Action', '2025-05-23', 1),
  ('Sunday Gravy', 'Comedy', '2018-08-03', 2),
  ('Glass Harbor', 'Drama', '2023-12-01', 2),
  ('Echo Canyon', 'Action', '2016-03-11', NULL);
"""

SAMPLE_DBS["world"] = """
-- Mini version of the Country/City/CountryLanguage examples from chapter 3
CREATE TABLE Country (
  Code CHAR(3),
  Name VARCHAR(40),
  Continent VARCHAR(15),
  Population BIGINT,
  LifeExpectancy DECIMAL(3,1),
  PRIMARY KEY (Code)
);
CREATE TABLE City (
  ID INT AUTO_INCREMENT,
  Name VARCHAR(35),
  CountryCode CHAR(3),
  Population INT,
  PRIMARY KEY (ID),
  FOREIGN KEY (CountryCode) REFERENCES Country(Code)
);
CREATE TABLE CountryLanguage (
  CountryCode CHAR(3),
  Language VARCHAR(30),
  IsOfficial BOOL,
  Percentage DECIMAL(4,1),
  PRIMARY KEY (CountryCode, Language),
  FOREIGN KEY (CountryCode) REFERENCES Country(Code)
);
INSERT INTO Country VALUES
  ('USA', 'United States', 'North America', 340000000, 79.3),
  ('MEX', 'Mexico', 'North America', 129000000, 75.1),
  ('BRA', 'Brazil', 'South America', 216000000, 75.9),
  ('FRA', 'France', 'Europe', 68000000, 82.9),
  ('DEU', 'Germany', 'Europe', 84000000, 81.2),
  ('ITA', 'Italy', 'Europe', 59000000, 83.5),
  ('NGA', 'Nigeria', 'Africa', 223000000, 53.6),
  ('EGY', 'Egypt', 'Africa', 112000000, 70.2),
  ('JPN', 'Japan', 'Asia', 124000000, 84.5),
  ('IND', 'India', 'Asia', 1428000000, 67.7),
  ('AUS', 'Australia', 'Oceania', 26000000, 83.2),
  ('ISL', 'Iceland', 'Europe', 375000, 83.1);
INSERT INTO City (Name, CountryCode, Population) VALUES
  ('New York', 'USA', 8300000), ('Los Angeles', 'USA', 3900000),
  ('Chicago', 'USA', 2700000), ('Columbus', 'USA', 900000),
  ('Mexico City', 'MEX', 9200000), ('Guadalajara', 'MEX', 1500000),
  ('Sao Paulo', 'BRA', 12300000), ('Rio de Janeiro', 'BRA', 6700000),
  ('Paris', 'FRA', 2100000), ('Lyon', 'FRA', 520000),
  ('Berlin', 'DEU', 3600000), ('Munich', 'DEU', 1500000),
  ('Rome', 'ITA', 2800000), ('Milan', 'ITA', 1400000),
  ('Lagos', 'NGA', 15400000), ('Abuja', 'NGA', 3800000),
  ('Cairo', 'EGY', 10100000), ('Tokyo', 'JPN', 13900000),
  ('Osaka', 'JPN', 2700000), ('Mumbai', 'IND', 12500000),
  ('Delhi', 'IND', 16800000), ('Sydney', 'AUS', 5300000),
  ('Melbourne', 'AUS', 5100000), ('Reykjavik', 'ISL', 140000);
INSERT INTO CountryLanguage VALUES
  ('USA', 'English', 1, 86.2), ('USA', 'Spanish', 0, 13.5),
  ('MEX', 'Spanish', 1, 92.7), ('BRA', 'Portuguese', 1, 97.5),
  ('FRA', 'French', 1, 93.6), ('DEU', 'German', 1, 91.3),
  ('ITA', 'Italian', 1, 94.1), ('NGA', 'English', 1, 53.0),
  ('NGA', 'Hausa', 0, 25.0), ('EGY', 'Arabic', 1, 94.0),
  ('JPN', 'Japanese', 1, 99.1), ('IND', 'Hindi', 1, 41.0),
  ('IND', 'English', 1, 10.6), ('AUS', 'English', 1, 76.8),
  ('ISL', 'Icelandic', 1, 93.2);
"""

SAMPLE_DBS["company"] = """
-- Employee/Department tables in the style of the office-hours DML drills
-- (ManagerID makes self-joins possible, as in section 3.7)
CREATE TABLE Department (
  DeptID INT,
  DeptName VARCHAR(20),
  Building VARCHAR(20),
  PRIMARY KEY (DeptID)
);
CREATE TABLE Employee (
  ID INT AUTO_INCREMENT,
  Name VARCHAR(40),
  Salary DECIMAL(10,2),
  HireDate DATE,
  DeptID INT,
  ManagerID INT,
  PRIMARY KEY (ID),
  FOREIGN KEY (DeptID) REFERENCES Department(DeptID),
  FOREIGN KEY (ManagerID) REFERENCES Employee(ID)
);
INSERT INTO Department VALUES
  (10, 'Engineering', 'North'),
  (20, 'Sales', 'South'),
  (30, 'Marketing', 'South'),
  (40, 'Finance', 'North'),
  (50, 'Research', 'West');
INSERT INTO Employee (Name, Salary, HireDate, DeptID, ManagerID) VALUES
  ('Ava Chen', 98000, '2015-03-09', 10, NULL),
  ('Ben Ortiz', 72000, '2017-06-21', 10, 1),
  ('Cara Silva', 64000, '2019-01-14', 10, 1),
  ('Dev Kumar', 47000, '2021-08-02', 20, 5),
  ('Elle Brooks', 83000, '2016-04-27', 20, 1),
  ('Finn Walsh', 39500, '2023-02-13', 20, 5),
  ('Gia Romano', 55000, '2020-09-30', 30, 5),
  ('Hank Doyle', 46500, '2022-05-18', 30, 7),
  ('Iris Novak', 91000, '2014-11-03', 40, 1),
  ('Jae Park', 61000, '2018-07-09', 40, 9),
  ('Kim Reyes', 44000, '2024-01-22', NULL, 9),
  ('Leo Grant', 58500, '2019-10-15', 30, 7);
"""

DB_DESCRIPTIONS = {
    "stable":  "Horse / Student / LessonSchedule — the chapter 2 & 3 lab tables",
    "movies":  "Movie / Streaming — the office-hours DDL drill schema",
    "world":   "Country / City / CountryLanguage — the chapter 3 query examples",
    "company": "Employee / Department — DML drills, GROUP BY, and self-joins",
}


# ---------------------------------------------------------------------------
# Question bank
# ---------------------------------------------------------------------------
# Weighting comes from the D426 practice test's actual distribution:
# SQL (ch2+ch3) ~38%, ER modeling ~24%, normal forms ~21%, intro ~14%,
# physical design ~3%. The OA is all multiple choice and heavily
# definition-based, so definition items dominate; hands-on SQL tasks are
# there to make the definitions stick (and to warm you up for D427).

CH_WEIGHT = {1: 0.14, 2: 0.19, 3: 0.19, 4: 0.45, 5: 0.04}

CONCEPTS = {}
def _concept(cid, ch, ref, name):
    CONCEPTS[cid] = {"ch": ch, "ref": ref, "name": name}

for cid, ch, ref, name in [
    ("db-basics",      1, "1.1", "Database basics"),
    ("db-system",      1, "1.2", "Database system components"),
    ("sublang",        1, "1.3", "SQL sublanguages"),
    ("design-phases",  1, "1.4", "Design phases & data independence"),
    ("mysql",          1, "1.5", "MySQL"),
    ("rel-model",      1, "1.6", "Relational model"),
    ("sql-lang",       2, "2.1", "SQL language elements"),
    ("ddl-tables",     2, "2.3", "CREATE / DROP TABLE"),
    ("data-types",     2, "2.4", "Data types"),
    ("nulls",          2, "2.5", "NULL values"),
    ("dml",            2, "2.6", "INSERT / UPDATE / DELETE"),
    ("pkeys",          2, "2.7", "Primary keys"),
    ("fkeys",          2, "2.8", "Foreign keys"),
    ("ref-integrity",  2, "2.9", "Referential integrity"),
    ("constraints",    2, "2.10", "Constraints"),
    ("alter",          2, "2.12", "ALTER TABLE (CAD)"),
    ("select-where",   3, "3.1", "SELECT & WHERE"),
    ("null-compare",   3, "3.2", "NULL arithmetic & comparisons"),
    ("operators",      3, "3.3", "BETWEEN / IN / LIKE / DISTINCT"),
    ("functions",      3, "3.4", "Simple functions"),
    ("aggregates",     3, "3.5", "Aggregates, GROUP BY, HAVING"),
    ("joins",          3, "3.6", "JOIN queries"),
    ("join-types",     3, "3.7", "Equijoins, self-joins, cross-joins"),
    ("views",          3, "3.8", "Views"),
    ("er-basics",      4, "4.1", "Entities, relationships, attributes"),
    ("rel-kinds",      4, "4.3-4.5", "Binary / unary / ternary"),
    ("cardinality",    4, "4.6", "Cardinality & modality"),
    ("weak-entities",  4, "4.7", "Strong & weak entities"),
    ("super-sub",      4, "4.8", "Supertype & subtype entities"),
    ("design-steps",   4, "4.2-4.15", "ER design steps"),
    ("impl",           4, "4.10-4.12", "Implementing entities/relationships"),
    ("dependencies",   4, "4.13", "Functional dependencies"),
    ("normal-forms",   4, "4.13-4.15", "Normal forms"),
    ("table-struct",   5, "5.1", "Table structures"),
    ("indexes",        5, "5.2", "Indexes"),
]:
    _concept(cid, ch, ref, name)

def _mcq(rng, cid, prompt, correct, wrongs, explain, kind="mcq"):
    wrongs = list(dict.fromkeys(w for w in wrongs if w != correct))
    rng.shuffle(wrongs)
    opts = [correct] + wrongs[:3]
    rng.shuffle(opts)
    return {"type": kind, "concept": cid, "prompt": prompt, "options": opts,
            "answer": opts.index(correct), "explain": explain}

def _tf(rng, cid, prompt, answer, explain):
    return {"type": "tf", "concept": cid, "prompt": prompt,
            "answer": bool(answer), "explain": explain}

# --- Definition pools (term, definition) — same-pool entries make the
# plausible distractors the OA loves.

POOLS = {
"sublang": ("sublang", [
 ("Data Definition Language (DDL)", "defines the structure of the database — the columns and structure of tables (CREATE, ALTER, DROP)"),
 ("Data Query Language (DQL)", "retrieves or selects data from the database"),
 ("Data Manipulation Language (DML)", "manipulates the rows of data stored in a database (INSERT, UPDATE, DELETE, SELECT)"),
 ("Data Control Language (DCL)", "controls database user access"),
 ("Data Transaction Language (DTL)", "manages database transactions"),
]),
"components": ("db-system", [
 ("the query processor", "interprets queries, creates a plan to modify the database or retrieve data, and performs query optimization"),
 ("the storage manager", "translates query processor instructions into low-level file-system commands, and uses indexes to quickly locate data"),
 ("the transaction manager", "ensures transactions are properly executed, prevents conflicts between concurrent transactions, and restores the database to a consistent state after a failure"),
 ("a database administrator", "secures the database system against unauthorized users and enforces procedures for user access and system availability"),
 ("a database application", "software that helps business users interact with database systems"),
]),
"phases": ("design-phases", [
 ("conceptual design (analysis)", "specifies database requirements as entities, relationships, and attributes, without regard to a specific database system"),
 ("logical design", "converts entities, relationships, and attributes into tables, keys, and columns for a specific database system"),
 ("physical design", "adds indexes and specifies how tables are organized on storage media"),
 ("data independence", "the principle that physical design affects query processing speed but never affects the query result"),
]),
"rel-model": ("rel-model", [
 ("a table", "a named object with a fixed tuple of columns and a varying set of rows"),
 ("a column", "a named element that has a data type"),
 ("a row", "an unnamed tuple of values, each corresponding to a column"),
 ("a data type", "a named set of values, from which column values are drawn"),
 ("a set", "an unordered collection of elements enclosed in braces"),
 ("a tuple", "an ordered collection of elements enclosed in parentheses"),
 ("a cell", "a single column of a single row — one data point"),
]),
"basics": ("db-basics", [
 ("a database", "a collection of data in a structured format"),
 ("a database management system (DBMS)", "software that reads and writes data in a database"),
 ("data", "raw facts, which by themselves cannot tell us much"),
 ("information", "data connected in a logical way, which can be acted on"),
 ("a NoSQL (non-relational) database", "any alternative to a relational SQL database, designed to handle large web traffic and scale easily"),
]),
"keys": ("pkeys", [
 ("a primary key", "a column, or group of columns, used to identify a row"),
 ("a composite primary key", "a primary key that consists of multiple columns"),
 ("a candidate key", "a simple or composite column that is unique and minimal"),
 ("a foreign key", "a column, or group of columns, that refers to a primary key"),
 ("a non-key column", "a column that is not contained in any candidate key"),
]),
"ri": ("ref-integrity", [
 ("RESTRICT", "rejects an insert, update, or delete that violates referential integrity"),
 ("SET NULL", "sets invalid foreign keys to NULL"),
 ("SET DEFAULT", "sets invalid foreign keys to the foreign key's default value"),
 ("CASCADE", "propagates primary key changes to the matching foreign keys"),
]),
"constraints": ("constraints", [
 ("NOT NULL", "requires a column to have a value in every row"),
 ("UNIQUE", "requires a column's (or column group's) values to differ from all other rows in the table"),
 ("CHECK", "specifies an expression that must be true for every row of the table"),
 ("DEFAULT", "specifies the value stored in a column when an insert does not supply one"),
 ("PRIMARY KEY", "identifies each row: values must be unique and cannot be NULL"),
 ("FOREIGN KEY", "requires values to match a primary key in the referenced table (or be NULL)"),
]),
"dml": ("dml", [
 ("INSERT", "adds new rows to a table"),
 ("UPDATE", "modifies existing rows, using a SET clause and an optional WHERE clause"),
 ("DELETE", "removes existing rows from a table, with an optional WHERE clause"),
 ("SELECT", "retrieves data from a table"),
 ("TRUNCATE", "deletes all rows from a table while keeping the table itself"),
 ("MERGE", "selects data from a source table and inserts it into a target table"),
]),
"sqlparts": ("sql-lang", [
 ("a literal", "an explicit value that is string, numeric, or binary — strings are surrounded by quotes"),
 ("a keyword", "a word with special meaning to SQL, such as SELECT, FROM, or WHERE"),
 ("an identifier", "the name of a database object, such as a table or column"),
 ("an expression", "a sequence of literals, identifiers, and operations that evaluates to a single value"),
 ("a comment", "text intended only for humans, ignored by the database when parsing (-- or /* */)"),
]),
"joins": ("joins", [
 ("an INNER JOIN", "selects only the left and right table rows that match"),
 ("a LEFT JOIN", "selects ALL left table rows, but only matching right table rows"),
 ("a RIGHT JOIN", "selects ALL right table rows, but only matching left table rows"),
 ("a FULL JOIN", "selects all left and right table rows, regardless of match"),
 ("an outer join", "any join that selects unmatched rows — left, right, and full joins"),
 ("a UNION", "combines the results of two SELECT statements into one table"),
]),
"join-types": ("join-types", [
 ("an equijoin", "compares columns of two tables with the = operator"),
 ("a non-equijoin", "compares columns with an operator such as <, >, !=, or <>"),
 ("a self-join", "joins a table to itself, comparing rows of the same table (each copy needs an alias)"),
 ("a cross-join", "combines two tables without comparing columns — no ON clause, all combinations of rows appear"),
]),
"views": ("views", [
 ("a view", "a virtual table whose rows come from a stored SELECT query against base tables"),
 ("a materialized view", "a view for which data is stored at all times, and which must be refreshed when base tables change"),
 ("WITH CHECK OPTION", "makes the database reject inserts and updates through a view that do not satisfy the view query's WHERE clause"),
]),
"er": ("er-basics", [
 ("an entity", "a person, place, product, concept, or activity"),
 ("a relationship", "a statement about two entities — a link between them"),
 ("an attribute", "a descriptive property of an entity"),
 ("an entity type", "a set of things, which usually becomes a table"),
 ("a relationship type", "a set of related things, which usually becomes a foreign key"),
 ("an attribute type", "a set of values, which usually becomes a column"),
 ("an entity instance", "an individual thing, such as the employee Sam Snead"),
 ("a reflexive relationship", "a relationship that relates an entity to itself"),
]),
"er2": ("weak-entities", [
 ("a weak entity", "an entity without an identifying attribute of its own, identified through a relationship to another entity"),
 ("an identifying relationship", "the relationship between a weak entity and its identifying entity — the identifying entity's cardinality is always exactly one"),
 ("a supertype entity", "an entity type that contains other entity types as subsets"),
 ("a subtype entity", "a subset of another entity type, drawn within it on an ER diagram (an IsA relationship)"),
 ("a partition", "a group of mutually exclusive subtype entities"),
 ("an associative entity", "in its most basic form, the combination of the unique identifiers of the two entities in a many-to-many relationship"),
 ("an intangible entity", "an entity documented in the data model but not tracked with data in the database"),
]),
"card": ("cardinality", [
 ("cardinality (relationship maximum)", "the GREATEST number of instances of one entity that can relate to a single instance of another entity"),
 ("modality (relationship minimum)", "the LEAST number of instances of one entity that can relate to a single instance of another entity"),
]),
"nf": ("normal-forms", [
 ("first normal form (1NF)", "the table has a primary key and every entry is atomic — no repeating groups or arrays"),
 ("second normal form (2NF)", "the table is in 1NF and no non-key column depends on only part of a composite primary key"),
 ("third normal form (3NF)", "whenever a NON-KEY column A depends on a column B, B is unique — the key, the whole key, and nothing but the key"),
 ("Boyce-Codd normal form (BCNF)", "whenever ANY column A depends on a column B, B is unique — the 3NF definition with 'non-key' removed"),
 ("normalization", "eliminating redundancy by decomposing a table into two or more tables in higher normal form"),
 ("denormalization", "intentionally introducing redundancy by merging tables"),
 ("a partial dependency", "a dependency on only part of a composite primary key"),
 ("a trivial dependency", "a dependency in which A's columns are a subset of B's columns, so A always depends on B"),
]),
"struct": ("table-struct", [
 ("a heap table", "imposes no order on rows, which optimizes inserts and bulk loads"),
 ("a sorted table", "uses a designer-chosen sort column to determine the physical row order"),
 ("a hash table", "assigns rows to buckets using a hash function, such as the modulo function"),
 ("a table cluster", "interleaves the rows of two or more tables in the same storage area"),
]),
"index": ("indexes", [
 ("a table scan", "reads table blocks directly, without accessing an index"),
 ("an index scan", "reads index blocks sequentially, in order to locate the needed table blocks"),
 ("hit ratio (filter factor / selectivity)", "the percentage of table rows selected by a query"),
 ("a dense index", "contains an entry for every table ROW"),
 ("a sparse index", "contains an entry for every table BLOCK"),
 ("a bitmap index", "a grid of bits — ones and zeros"),
 ("a hash index", "assigns index entries to buckets"),
 ("a tablespace", "a database object that maps one or more tables to a single file"),
 ("a binary search", "repeatedly splits the index in two until it finds the entry containing the search value"),
]),
}

_SPARE_DISTRACTORS = [
    ("multiplicity", "the AVERAGE number of instances of one entity that "
     "relates to another entity"),
    ("connectivity", "the total number of relationship types defined in the "
     "data model"),
    ("selectivity", "the number of attributes that an entity type contains"),
    ("referential integrity", "the requirement that every attribute have a "
     "default value"),
]

def _pool_gen(pool_key):
    cid, entries = POOLS[pool_key]
    def gen(rng, ctx):
        term, definition = rng.choice(entries)
        others = [e for e in entries if e[0] != term]
        if len(others) < 3:
            others = others + rng.sample(_SPARE_DISTRACTORS, 3 - len(others))
        ref = CONCEPTS[cid]["ref"]
        if rng.random() < 0.5:
            return _mcq(rng, cid,
                        f"Which of the following best describes {term}?",
                        definition[0].upper() + definition[1:],
                        [d[0].upper() + d[1:] for _t, d in others],
                        f"{term[0].upper() + term[1:]} {definition}. (§{ref})")
        return _mcq(rng, cid,
                    f"Which term matches this description: \u201c{definition}\u201d?",
                    term, [t for t, _d in others],
                    f"{term[0].upper() + term[1:]} {definition}. (§{ref})")
    return gen

# --- Bespoke generators ------------------------------------------------------

def g_unstructured(rng, ctx):
    unstruct = ["A video file", "An audio recording", "A photograph"]
    struct = ["A table that holds customer data", "A record representing one student",
              "A relational database of course registrations",
              "A row in an Orders table"]
    if rng.random() < 0.5:
        return _mcq(rng, "db-basics", "Which item is UNSTRUCTURED data?",
                    rng.choice(unstruct), struct,
                    "Video, audio, and images are unstructured — the fields "
                    "*describing* them would be structured. (§1.1)")
    return _mcq(rng, "db-basics", "Which item is STRUCTURED data?",
                rng.choice(struct), unstruct,
                "Tables, rows, and records are structured data; raw media files "
                "are unstructured. (§1.1)")

def g_synonyms(rng, ctx):
    sets = [("table", ["file", "relation"]), ("row", ["record", "tuple"]),
            ("column", ["field", "attribute"])]
    i = rng.randrange(3)
    term, syns = sets[i]
    correct = rng.choice(syns)
    wrongs = [w for j, (_t, ws) in enumerate(sets) if j != i for w in ws]
    return _mcq(rng, "rel-model",
                f"In relational terminology, a {term} is also called a ____.",
                correct, wrongs,
                "The synonym trios: table/file/relation, row/record/tuple, "
                "column/field/attribute. (§1.6)")

def g_record_fields(rng, ctx):
    return _mcq(rng, "rel-model", "A record consists of a ____.",
                "set of one or more fields",
                ["single character", "collection of unrelated tables",
                 "group of files", "named set of data types"],
                "Connected fields make up a row, and a complete row is a "
                "record. (§1.6)")

def g_set_tuple(rng, ctx):
    a, b, c = rng.sample(list("abcdexyz"), 3)
    if rng.random() < 0.5:
        return _tf(rng, "rel-model",
                   f"({a}, {b}, {c}) and ({c}, {b}, {a}) are the same tuple.",
                   False,
                   "Tuples are ORDERED collections in parentheses, so different "
                   "orders are different tuples. Sets (in braces) are unordered. (§1.6)")
    return _tf(rng, "rel-model",
               f"{{{a}, {b}, {c}}} and {{{c}, {b}, {a}}} are the same set.",
               True,
               "Sets are UNORDERED collections in braces, so element order "
               "doesn't matter. Tuples, in parentheses, are ordered. (§1.6)")

def g_rows_unordered(rng, ctx):
    return _tf(rng, "rel-model",
               "Since a table is a set of rows, the rows of a table have no "
               "inherent order.", True,
               "A table is a fixed tuple of columns but a SET of rows — row "
               "order is not guaranteed unless a query uses ORDER BY. (§1.6)")

def g_empty_table(rng, ctx):
    return _mcq(rng, "rel-model",
                "A table must have at least ____.",
                "one column, but may have zero rows",
                ["one row, but may have zero columns",
                 "one row and one column",
                 "one primary key value"],
                "A table needs at least one column; a table with no rows is "
                "called an empty table. (§1.6)")

def g_duis(rng, ctx):
    dml = ["DELETE", "UPDATE", "INSERT", "SELECT"]
    ddl = ["CREATE TABLE", "ALTER TABLE", "DROP TABLE", "CREATE VIEW",
           "CREATE INDEX", "DROP INDEX"]
    if rng.random() < 0.5:
        return _mcq(rng, "sublang",
                    "Which statement is NOT part of the Data Manipulation "
                    "Language (DML)?",
                    rng.choice(ddl), rng.sample(dml, 3),
                    "DML changes/chooses ROWS: DELETE, UPDATE, INSERT, SELECT "
                    "(DUIS). CREATE/ALTER/DROP change table STRUCTURE — that's "
                    "DDL. (§1.3, office hours)")
    return _mcq(rng, "sublang",
                "Which statement IS part of the Data Manipulation Language (DML)?",
                rng.choice(dml), rng.sample(ddl, 3),
                "Remember DUIS: DELETE, UPDATE, INSERT, SELECT manipulate rows "
                "of data. Structure changes are DDL. (§1.3)")

def g_mysql_fact(rng, ctx):
    return _mcq(rng, "mysql", "MySQL is best described as ____.",
                "an open-source relational database system",
                ["a commercial NoSQL database system",
                 "a spreadsheet application",
                 "a general-purpose programming language",
                 "a proprietary operating system"],
                "MySQL is a relational database system with an open-source "
                "license — anyone can inspect, copy, and modify it. (§1.5)")

def g_design_phase_pick(rng, ctx):
    items = [("entities, relationships, and attributes are identified",
              "Conceptual design (analysis)"),
             ("the ER model is converted into tables, columns, and keys",
              "Logical design"),
             ("indexes are added and table storage organization is chosen",
              "Physical design")]
    desc, phase = rng.choice(items)
    all_ = ["Conceptual design (analysis)", "Logical design", "Physical design",
            "Transaction design"]
    return _mcq(rng, "design-phases",
                f"During which database design phase {desc}?",
                phase, [a for a in all_ if a != phase],
                "Conceptual/analysis → entities, relationships, attributes; "
                "logical → tables, columns, keys; physical → indexes and "
                "storage. (§1.4)")

def g_data_independence(rng, ctx):
    return _mcq(rng, "design-phases",
                "The principle that physical design never affects query "
                "RESULTS (only speed) is called ____.",
                "data independence",
                ["referential integrity", "normalization",
                 "query optimization", "data redundancy"],
                "Data independence lets administrators reorganize storage and "
                "add indexes without changing query results. (§1.4, §5.1)")

# --- Chapter 2 ---------------------------------------------------------------

_TBL = ["Movie", "Horse", "Student", "Product", "Order", "Album"]
_COLS = ["Title", "Name", "Price", "Genre", "Breed", "Rating", "Quantity"]

def g_create_syntax(rng, ctx):
    t = rng.choice(_TBL); c1, c2 = rng.sample(_COLS, 2); n = rng.choice([20, 30, 50, 60])
    good = f"CREATE TABLE {t} ({c1} INT, {c2} VARCHAR({n}));"
    return _mcq(rng, "ddl-tables",
                f"Which statement correctly creates a table named {t} with an "
                f"integer column {c1} and a text column {c2} of up to {n} "
                "characters?",
                good,
                [f"CREATE TABLE {t} (INT {c1}, VARCHAR({n}) {c2});",
                 f"CREATE {t} TABLE ({c1} INT, {c2} VARCHAR({n}));",
                 f"CREATE TABLE {t} ADD {c1} INT, {c2} VARCHAR({n});",
                 f"INSERT TABLE {t} ({c1} INT, {c2} VARCHAR({n}));"],
                "CREATE TABLE TableName (ColumnName DataType, ...): names come "
                "before types, inside parentheses. (§2.3)")

_BYTES = [("TINYINT", 1), ("SMALLINT", 2), ("MEDIUMINT", 3), ("INT", 4), ("BIGINT", 8)]

def g_type_bytes(rng, ctx):
    name, b = rng.choice(_BYTES)
    if rng.random() < 0.5:
        return _mcq(rng, "data-types",
                    f"How many bytes of storage does the MySQL {name} data "
                    "type use?",
                    f"{b} byte{'s' if b != 1 else ''}",
                    [f"{x} byte{'s' if x != 1 else ''}" for _n, x in _BYTES if x != b],
                    "TINYINT=1, SMALLINT=2, MEDIUMINT=3, INT=4, BIGINT=8 "
                    "bytes. (§2.4)")
    return _mcq(rng, "data-types",
                f"Which integer data type is implemented with {b} "
                f"byte{'s' if b != 1 else ''} of storage?",
                name, [n2 for n2, x in _BYTES if x != b],
                "TINYINT=1, SMALLINT=2, MEDIUMINT=3, INT=4, BIGINT=8 bytes. (§2.4)")

def g_type_range(rng, ctx):
    ranges = [("TINYINT", "-128 to 127", "0 to 255"),
              ("SMALLINT", "-32,768 to 32,767", "0 to 65,535")]
    name, signed, unsigned = rng.choice(ranges)
    if rng.random() < 0.5:
        return _mcq(rng, "data-types",
                    f"What is the SIGNED range of the {name} data type?",
                    signed,
                    [unsigned, "-1,024 to 1,023", "-2,147,483,648 to 2,147,483,647",
                     "0 to 16,777,215"],
                    f"{name} signed: {signed}; unsigned: {unsigned}. UNSIGNED "
                    "shifts the whole range positive. (§2.4)")
    return _mcq(rng, "data-types",
                f"What is the UNSIGNED range of the {name} data type?",
                unsigned,
                [signed, "-255 to 255", "0 to 4,294,967,295", "1 to 100"],
                f"{name} unsigned: {unsigned} (same number of values as the "
                f"signed range {signed}, all non-negative). (§2.4)")

def g_type_pick(rng, ctx):
    n = rng.choice([20, 40, 50])
    m, d = rng.choice([(6, 2), (10, 2), (5, 1)])
    items = [
        (f"textual values of 0 to {n} characters", f"VARCHAR({n})",
         ["CHAR", "TEXTFIELD", "STRING", "INT"]),
        ("fractional numeric values, such as prices", "DECIMAL",
         ["INT", "VARCHAR", "DATE", "BOOLEAN"]),
        ("a year, month, and day", "DATE",
         ["DATETIME(Y,M,D)", "VARCHAR(8)", "INT", "TIMEONLY"]),
        (f"numeric values with {m} total digits, {d} of them after the "
         "decimal point", f"DECIMAL({m},{d})",
         [f"DECIMAL({d},{m})", f"FLOAT({m})", f"INT({m},{d})", f"NUMBER({d})"]),
    ]
    desc, correct, wrongs = rng.choice(items)
    return _mcq(rng, "data-types", f"Which data type stores {desc}?",
                correct, wrongs,
                "INT = integers, DECIMAL(M,D) = M total digits with D after "
                "the decimal point, VARCHAR(N) = 0..N characters, DATE = "
                "year-month-day. (§2.4)")

def g_char_varchar(rng, ctx):
    return _mcq(rng, "data-types",
                "What is the difference between CHAR(10) and VARCHAR(10)?",
                "CHAR stores a fixed length of 10; VARCHAR stores a variable "
                "length of up to 10 characters",
                ["VARCHAR stores a fixed length; CHAR is variable",
                 "CHAR stores numbers; VARCHAR stores text",
                 "There is no difference in MySQL",
                 "CHAR allows NULL; VARCHAR does not"],
                "CHAR(N) is fixed-length, VARCHAR(N) is variable-length up to "
                "N characters. (§2.4)")

def g_quotes(rng, ctx):
    t = rng.choice(["a string value", "a DATE value like 2024-05-01"])
    return _mcq(rng, "dml",
                f"When inserting {t} into a table, the value must be ____.",
                "surrounded by quotes",
                ["written without quotes", "surrounded by parentheses",
                 "prefixed with the # symbol", "converted to an integer"],
                "Strings and dates take quotes in INSERT statements; numeric "
                "values do not. (§2.4, §2.6)")

def g_null_meaning(rng, ctx):
    return _mcq(rng, "nulls", "In SQL, NULL represents ____.",
                "an unknown or missing value",
                ["the number zero", "an empty string",
                 "the boolean value FALSE", "a deleted row"],
                "NULL means unknown/missing — it is NOT 0 and NOT an empty "
                "string. (§2.5)")

def g_insert_syntax(rng, ctx):
    name = rng.choice(["'Bergamot'", "'Kestrel'", "'Alder'"])
    price = rng.choice([12, 30, 45])
    good = f"INSERT INTO Product (Name, Price) VALUES ({name}, {price});"
    return _mcq(rng, "dml",
                "The Product table has columns Name (VARCHAR) and Price (INT). "
                f"Which statement correctly inserts a product named {name} "
                f"priced at {price}?",
                good,
                [f"INSERT INTO Product (Name, Price) VALUES ({name[1:-1]}, {price});",
                 f"INSERT Product VALUES (Name = {name}, Price = {price});",
                 f"INSERT INTO Product (Name, Price) ({name}, {price});",
                 f"ADD INTO Product (Name, Price) VALUES ({name}, '{price}');"],
                "INSERT INTO Table (Col1, Col2) VALUES (v1, v2); — strings "
                "quoted, numbers not, VALUES keyword required. (§2.6)")

def g_autoinc(rng, ctx):
    v = rng.randrange(3)
    if v == 0:
        return _mcq(rng, "pkeys",
                    "When inserting a row into a table whose primary key is an "
                    "AUTO_INCREMENT column, you should ____.",
                    "omit the primary key value and let the database assign it",
                    ["always supply the next available value yourself",
                     "insert NULL into every other column",
                     "supply the value 0 so MySQL rejects duplicates",
                     "drop the primary key first"],
                    "MySQL allows inserting a specific value into an "
                    "auto-increment column, but overriding it is usually a "
                    "mistake — omit it and the database assigns the next "
                    "value. (§2.7)")
    if v == 1:
        return _mcq(rng, "pkeys", "An auto-increment column is ____.",
                    "a numeric column assigned an automatically incrementing "
                    "value when a new row is inserted",
                    ["a text column that stores sequential labels",
                     "a column that automatically deletes old rows",
                     "a foreign key that updates itself",
                     "a column recomputed every time the table is queried"],
                    "Auto-increment columns get the next number automatically "
                    "on INSERT — commonly used for primary keys. (§2.7)")
    return _mcq(rng, "pkeys",
                "Which of these is a common ERROR when inserting primary keys?",
                "Supplying a value for an auto-increment primary key",
                ["Omitting values for an auto-increment primary key",
                 "Letting the database assign auto-increment values",
                 "Inserting a unique value for a non-auto-increment primary key"],
                "The two classic mistakes: supplying values for AUTO_INCREMENT "
                "keys, and OMITTING values for keys that are NOT "
                "auto-increment. (§2.7)")

def g_where_omitted(rng, ctx):
    stmt = rng.choice(["UPDATE", "DELETE"])
    effect = "updated" if stmt == "UPDATE" else "deleted"
    return _mcq(rng, "dml",
                f"What happens when a {stmt} statement omits the WHERE clause?",
                f"ALL rows in the table are {effect}",
                [f"No rows are {effect}",
                 "The statement fails with a syntax error",
                 f"Only the first row is {effect}",
                 "The table itself is dropped"],
                f"WHERE is optional in {stmt} — and omitting it applies the "
                f"change to every row. A classic (and dangerous) trap. (§2.6)")

def g_vict(rng, ctx):
    t = rng.randrange(4)
    if t == 0:
        return _mcq(rng, "alter",
                    "You need to delete the VIEW named StreamView from the "
                    "database. Which statement does this?",
                    "DROP VIEW StreamView;",
                    ["DELETE VIEW StreamView;",
                     "DELETE FROM StreamView;",
                     "ALTER TABLE StreamView DROP VIEW;",
                     "REMOVE VIEW StreamView;"],
                    "The question says 'delete' but a View, Index, Column, or "
                    "Table (VICT) is structure — you DROP it. DELETE removes "
                    "rows. (office hours, §2.3)")
    if t == 1:
        return _mcq(rng, "alter",
                    "You need to delete the INDEX named IdxReleaseDate. Which "
                    "statement does this?",
                    "DROP INDEX IdxReleaseDate;",
                    ["DELETE INDEX IdxReleaseDate;",
                     "DELETE FROM IdxReleaseDate;",
                     "ALTER INDEX IdxReleaseDate DROP;",
                     "TRUNCATE INDEX IdxReleaseDate;"],
                    "DROP a VICT: View, Index, Column, Table. DELETE is for "
                    "rows of data only. (office hours, §5.2)")
    if t == 2:
        col = rng.choice(["MovieTitle", "Genre", "Rating"])
        return _mcq(rng, "alter",
                    f"You need to delete the COLUMN {col} from the Movie "
                    "table. Which statement does this?",
                    f"ALTER TABLE Movie DROP {col};",
                    [f"DELETE {col} FROM Movie;",
                     f"DROP COLUMN {col} FROM Movie;",
                     f"UPDATE Movie DROP {col};",
                     f"ALTER TABLE Movie DELETE {col};"],
                    "Columns are structure, so it's ALTER TABLE ... DROP. "
                    "DELETE FROM removes rows. (office hours, §2.12)")
    return _mcq(rng, "ddl-tables",
                "You need to delete the entire Movie table (structure and "
                "all rows). Which statement does this?",
                "DROP TABLE Movie;",
                ["DELETE TABLE Movie;",
                 "DELETE FROM Movie;",
                 "TRUNCATE TABLE Movie;",
                 "ALTER TABLE Movie DROP;"],
                "DROP TABLE removes the table itself. DELETE FROM and "
                "TRUNCATE remove rows but keep the table. (§2.3)")

def g_truncate(rng, ctx):
    return _mcq(rng, "dml",
                "How does TRUNCATE TABLE Movie differ from DROP TABLE Movie?",
                "TRUNCATE deletes all rows but keeps the table; DROP deletes "
                "the table itself",
                ["TRUNCATE deletes the table; DROP deletes only the rows",
                 "They are identical in every database system",
                 "TRUNCATE only deletes rows that violate constraints",
                 "DROP keeps the table structure for reuse"],
                "TRUNCATE ≈ DELETE with no WHERE clause (all rows gone, table "
                "remains); DROP TABLE removes the table entirely. (§2.6)")

def g_pk_rules(rng, ctx):
    v = rng.randrange(4)
    if v == 0:
        return _tf(rng, "pkeys",
                   "A table may have several candidate keys, and the database "
                   "designer designates one of them as the primary key.",
                   True,
                   "Candidate keys are unique AND minimal; the designer picks "
                   "one to be the primary key. (§2.7)")
    if v == 1:
        return _mcq(rng, "pkeys",
                    "In the definition of a candidate key, 'minimal' means ____.",
                    "all columns of the key are necessary for uniqueness",
                    ["the key uses the smallest data type available",
                     "the key contains exactly one column",
                     "the key has the fewest characters",
                     "the key's values are the smallest in the table"],
                    "Minimal = drop any column and the key is no longer "
                    "unique. A candidate key is unique and minimal. (§2.7)")
    if v == 2:
        return _tf(rng, "pkeys",
                   "The primary key is usually the table's first column, and "
                   "this position is significant to the database.",
                   False,
                   "The PK usually appears first in diagrams, but its position "
                   "is NOT significant to the database. (§2.7)")
    return _tf(rng, "pkeys",
               "A primary key column may contain NULL values as long as they "
               "are unique.", False,
               "Primary key values must be unique AND non-NULL — NULL means "
               "unknown, which can't identify a row. (§2.7)")

def g_fk_rules(rng, ctx):
    v = rng.randrange(3)
    if v == 0:
        return _mcq(rng, "fkeys",
                    "For a foreign key and the primary key it references, "
                    "which must be the SAME?",
                    "The data types",
                    ["The column names", "The table names",
                     "The number of rows", "The default values"],
                    "FK and PK data types must match; the NAMES may "
                    "differ. (§2.8)")
    if v == 1:
        return _tf(rng, "fkeys",
                   "Foreign key values may be NULL and may repeat across rows.",
                   True,
                   "Unlike primary keys, foreign keys can be NULL (no parent "
                   "yet) and non-unique (many children per parent). (§2.8)")
    return _mcq(rng, "fkeys",
                "Which keywords add a foreign key constraint in a CREATE "
                "TABLE statement?",
                "FOREIGN KEY and REFERENCES",
                ["FOREIGN KEY and JOINS", "LINK and REFERENCES",
                 "KEY and PARENT", "CONSTRAINT and CASCADE"],
                "FOREIGN KEY (Col) REFERENCES ParentTable(ParentCol) — the "
                "database then rejects statements that violate referential "
                "integrity. (§2.8)")

def g_ri_scenario(rng, ctx):
    action, outcome, wrongs = rng.choice([
        ("ON DELETE CASCADE", "The customer's orders are automatically deleted too",
         ["The delete is rejected", "The orders' CustomerID is set to NULL",
          "The orders are moved to a default customer"]),
        ("ON DELETE SET NULL", "The orders' CustomerID values are set to NULL",
         ["The orders are deleted too", "The delete is rejected",
          "The orders keep the old CustomerID value"]),
        ("ON DELETE RESTRICT", "The delete is rejected because orders still "
         "reference the customer",
         ["The orders are deleted too", "The orders' CustomerID is set to NULL",
          "The customer is archived instead of deleted"]),
    ])
    return _mcq(rng, "ref-integrity",
                "Orders.CustomerID is a foreign key to Customer(ID), declared "
                f"with {action}. A customer row that has orders is deleted. "
                "What happens?",
                outcome, wrongs,
                "RESTRICT rejects, SET NULL nulls the FKs, SET DEFAULT uses "
                "the default value, CASCADE propagates the change. (§2.9)")

def g_constraint_pick(rng, ctx):
    desc, correct = rng.choice([
        ("every row must have a value in the Email column", "NOT NULL"),
        ("no two rows may have the same Email value", "UNIQUE"),
        ("Price must always be greater than 0", "CHECK"),
        ("new rows get 'pending' in Status when no value is supplied", "DEFAULT"),
    ])
    return _mcq(rng, "constraints",
                f"Which constraint ensures that {desc}?",
                correct,
                [c for c in ["NOT NULL", "UNIQUE", "CHECK", "DEFAULT",
                             "FOREIGN KEY"] if c != correct],
                "NOT NULL = must have a value; UNIQUE = no duplicates; CHECK = "
                "expression must be true; DEFAULT = fill-in value. The "
                "database rejects statements that violate a constraint. (§2.10)")

def g_alter_cad(rng, ctx):
    v = rng.randrange(4)
    if v == 0:
        n = rng.choice([75, 100, 125])
        return _mcq(rng, "alter",
                    "Rename the Movie table's Title column to MovieTitle and "
                    f"allow up to {n} characters. Which statement?",
                    f"ALTER TABLE Movie CHANGE Title MovieTitle VARCHAR({n});",
                    [f"ALTER TABLE Movie MODIFY Title MovieTitle VARCHAR({n});",
                     f"ALTER TABLE Movie RENAME Title MovieTitle VARCHAR({n});",
                     f"UPDATE Movie SET Title = MovieTitle VARCHAR({n});",
                     f"ALTER TABLE Movie CHANGE MovieTitle Title VARCHAR({n});"],
                    "ALTER TABLE ... CHANGE OldName NewName NewType — CHANGE "
                    "renames AND retypes; old name comes first. (office hours, "
                    "§2.12)")
    if v == 1:
        n = rng.choice([100, 125])
        return _mcq(rng, "alter",
                    f"Update the Movie table's Title column to allow {n} "
                    "characters, keeping the name Title. Which statement?",
                    f"ALTER TABLE Movie CHANGE Title Title VARCHAR({n});",
                    [f"ALTER TABLE Movie CHANGE Title VARCHAR({n});",
                     f"UPDATE Movie SET Title = VARCHAR({n});",
                     f"ALTER TABLE Movie ADD Title VARCHAR({n});",
                     f"ALTER COLUMN Movie.Title VARCHAR({n});"],
                    "With CHANGE you repeat the name when only the type "
                    "changes: CHANGE Title Title VARCHAR(n). (office hours)")
    if v == 2:
        n = rng.choice([50, 75])
        return _mcq(rng, "alter",
                    f"Add a new column MovieTitle (up to {n} characters) to "
                    "the Movie table. Which statement?",
                    f"ALTER TABLE Movie ADD MovieTitle VARCHAR({n});",
                    [f"ALTER TABLE Movie INSERT MovieTitle VARCHAR({n});",
                     f"UPDATE Movie ADD MovieTitle VARCHAR({n});",
                     f"INSERT INTO Movie (MovieTitle) VARCHAR({n});",
                     f"CREATE COLUMN MovieTitle VARCHAR({n}) ON Movie;"],
                    "The ALTER TABLE verbs are CHANGE, ADD, DROP (CAD). ADD "
                    "appends a new column. (office hours, §2.12)")
    return _mcq(rng, "alter",
                "Make Movie.StreamID a foreign key to Streaming.StreamID. "
                "Which statement?",
                "ALTER TABLE Movie ADD FOREIGN KEY (StreamID) REFERENCES "
                "Streaming(StreamID);",
                ["ALTER TABLE Movie ADD FOREIGN KEY Streaming(StreamID);",
                 "ALTER TABLE Streaming ADD FOREIGN KEY (StreamID) REFERENCES "
                 "Movie(StreamID);",
                 "UPDATE Movie SET StreamID = FOREIGN KEY Streaming(StreamID);",
                 "ALTER TABLE Movie REFERENCES Streaming(StreamID);"],
                "ADD FOREIGN KEY (child column) REFERENCES Parent(column) — "
                "and it goes on the CHILD table (Movie). (office hours, §2.8)")

def g_comment(rng, ctx):
    return _mcq(rng, "sql-lang",
                "Which of the following is a valid SQL comment?",
                rng.choice(["-- update this later", "/* checked by DBA */"]),
                ["// update this later", "<!-- update this later -->",
                 "** update this later **", "%% update this later"],
                "SQL comments: -- for single-line, /* */ for multi-line. "
                "Comments are ignored by the database. (§2.1)")

# --- Chapter 3 ---------------------------------------------------------------

_WORDS = ["Lt", "Lot", "Lit", "Lift", "Loot", "Lol cat", "Let", "Bat", "Cot",
          "Slot", "List", "Lint", "Latch", "Melt", "Bolt", "Lofty"]

def g_like(rng, ctx):
    pattern = rng.choice(["L_t", "L%t", "L_t%", "%ot", "_o%", "L__t"])
    def matches(w):
        h, r = ctx.q(None, f"SELECT '{w}' LIKE '{pattern}'")
        return bool(r[0][0])
    yes = [w for w in _WORDS if matches(w)]
    no = [w for w in _WORDS if not matches(w)]
    if len(yes) >= 1 and len(no) >= 3 and rng.random() < 0.6:
        return _mcq(rng, "operators",
                    f"Which value MATCHES the pattern LIKE '{pattern}'?",
                    f"'{rng.choice(yes)}'",
                    [f"'{w}'" for w in rng.sample(no, 3)],
                    "% matches any number of characters (including zero); _ "
                    "matches exactly one character. (§3.3)")
    if len(no) >= 1 and len(yes) >= 3:
        return _mcq(rng, "operators",
                    f"Which value does NOT match the pattern LIKE '{pattern}'?",
                    f"'{rng.choice(no)}'",
                    [f"'{w}'" for w in rng.sample(yes, 3)],
                    "% matches any number of characters (including zero); _ "
                    "matches exactly one character. (§3.3)")
    return g_wildcards(rng, ctx)

def g_wildcards(rng, ctx):
    if rng.random() < 0.5:
        return _mcq(rng, "operators",
                    "In a LIKE pattern, the % wildcard matches ____.",
                    "any number of characters, including zero",
                    ["exactly one character", "exactly one digit",
                     "only spaces", "the literal percent sign only"],
                    "% = any number of characters (even none); _ = exactly "
                    "one character. (§3.3)")
    return _mcq(rng, "operators",
                "In a LIKE pattern, the _ wildcard matches ____.",
                "exactly one character",
                ["any number of characters", "one or more characters",
                 "only underscores", "exactly one word"],
                "_ = exactly one character; % = any number of characters. "
                "So 'L_t' matches 'Lot' but not 'Lt' or 'Loot'. (§3.3)")

def g_between(rng, ctx):
    a = rng.randrange(10, 40); b = a + rng.randrange(10, 40)
    col = rng.choice(["Price", "Age", "Height", "Quantity"])
    if rng.random() < 0.6:
        return _mcq(rng, "operators",
                    f"{col} BETWEEN {a} AND {b} is equivalent to ____.",
                    f"{col} >= {a} AND {col} <= {b}",
                    [f"{col} > {a} AND {col} < {b}",
                     f"{col} >= {a} OR {col} <= {b}",
                     f"{col} > {a} OR {col} < {b}",
                     f"{col} = {a} AND {col} = {b}"],
                    "BETWEEN is INCLUSIVE of both endpoints: >= min AND <= "
                    "max. (§3.3)")
    return _tf(rng, "operators",
               f"The value {a} satisfies the condition {col} BETWEEN {a} AND {b}.",
               True,
               "BETWEEN includes both endpoints — it means >= min AND <= "
               "max. (§3.3)")

def g_null_compare(rng, ctx):
    v = rng.randrange(3)
    if v == 0:
        n = rng.choice([25, 100, 7])
        return _mcq(rng, "null-compare",
                    f"What does the expression {n} + NULL evaluate to?",
                    "NULL",
                    [str(n), "0", "an error", f"{n + 1}"],
                    "Arithmetic with NULL yields NULL — the unknown value "
                    "propagates. (§3.2)")
    if v == 1:
        return _mcq(rng, "null-compare",
                    "Which WHERE clause correctly selects rows where "
                    "MiddleName has no value?",
                    "WHERE MiddleName IS NULL",
                    ["WHERE MiddleName = NULL", "WHERE MiddleName == NULL",
                     "WHERE MiddleName IS EMPTY", "WHERE MiddleName = ''"],
                    "Comparisons like = NULL evaluate to unknown and select "
                    "nothing; use IS NULL / IS NOT NULL. (§3.2)")
    return _tf(rng, "null-compare",
               "The condition Salary = NULL selects all rows where Salary "
               "is NULL.", False,
               "= NULL never matches — a comparison with NULL is unknown. "
               "Use Salary IS NULL. (§3.2)")

def g_func_output(rng, ctx):
    n = rng.randrange(3, 99)
    word = rng.choice(["MySQL", "Boomerang", "Database", "Disengage"])
    t = rng.choice(["14:22:45", "22:11:45", "08:05:30"])
    items = [
        (f"ABS(-{n})", str(n), [f"-{n}", "0", f"{n+1}"]),
        (f"LOWER('{word}')", f"'{word.lower()}'",
         [f"'{word.upper()}'", f"'{word}'", f"'{word.capitalize()}'"]),
        (f"UPPER('{word.lower()}')", f"'{word.upper()}'",
         [f"'{word.lower()}'", f"'{word.capitalize()}'", f"'{word[::-1].upper()}'"]),
        ("TRIM('  test  ')", "'test'",
         ["'  test  '", "'test  '", "'  test'"]),
        ("REPLACE('This and that', 'and', 'or')", "'This or that'",
         ["'This and that'", "'Thor and that'", "'or'"]),
        ("SUBSTRING('Boomerang', 1, 4)", "'Boom'",
         ["'oome'", "'Boome'", "'rang'"]),
        ("SUBSTRING('Boomerang', 5, 4)", "'eran'",
         ["'meran'", "'rang'", "'omer'"]),
        ("CONCAT('Dis', 'en', 'gage')", "'Disengage'",
         ["'Dis en gage'", "'Disen'", "an error"]),
        (f"HOUR('{t}')", t.split(":")[0].lstrip("0") or "0",
         [t.split(":")[1], t.split(":")[2], "12"]),
        (f"MINUTE('{t}')", t.split(":")[1].lstrip("0") or "0",
         [t.split(":")[0].lstrip("0") or "0", t.split(":")[2], "60"]),
    ]
    expr, correct, wrongs = rng.choice(items)
    return _mcq(rng, "functions", f"What does SELECT {expr}; return?",
                correct, wrongs,
                f"SELECT {expr} returns {correct}. String positions in "
                "SUBSTRING start at 1. (§3.4)")

def g_agg_nulls(rng, ctx):
    vals = rng.sample([3, 5, 7, 9, 11, 4, 8], 3)
    total = sum(vals)
    while total % 3 != 0:
        vals = rng.sample([3, 5, 7, 9, 11, 4, 8, 6], 3)
        total = sum(vals)
    listed = f"{vals[0]}, NULL, {vals[1]}, NULL, {vals[2]}"
    fn = rng.choice(["COUNT(Bonus)", "COUNT(*)", "SUM(Bonus)", "AVG(Bonus)"])
    ans = {"COUNT(Bonus)": "3", "COUNT(*)": "5", "SUM(Bonus)": str(total),
           "AVG(Bonus)": str(total // 3)}[fn]
    wrongs = {"3", "5", str(total), str(total // 3), str(total // 5), "NULL"} - {ans}
    return _mcq(rng, "aggregates",
                f"A table has 5 rows; the Bonus column holds: {listed}. "
                f"What does SELECT {fn} FROM the table return?",
                ans, sorted(wrongs),
                "Aggregate functions ignore NULLs — COUNT(column) counts "
                "non-NULL values, while COUNT(*) counts all rows. AVG divides "
                "by the non-NULL count. (§3.5)")

def g_agg_pick(rng, ctx):
    desc, fn = rng.choice([
        ("computes the arithmetic mean of the values", "AVG()"),
        ("finds the largest value in the set", "MAX()"),
        ("finds the smallest value in the set", "MIN()"),
        ("adds up all the values in the set", "SUM()"),
        ("counts the number of rows in the set", "COUNT()"),
    ])
    return _mcq(rng, "aggregates",
                f"Which aggregate function {desc}?",
                fn, [f for f in ["AVG()", "MAX()", "MIN()", "SUM()", "COUNT()"]
                     if f != fn],
                "COUNT, MIN, MAX, SUM, AVG process a set of rows and return "
                "one summary value. (§3.5)")

def g_having(rng, ctx):
    v = rng.randrange(3)
    if v == 0:
        return _mcq(rng, "aggregates",
                    "Which clause filters GROUPS produced by GROUP BY?",
                    "HAVING", ["WHERE", "ORDER BY", "FILTER", "LIMIT"],
                    "WHERE filters rows BEFORE grouping; HAVING filters the "
                    "groups afterward. (§3.5)")
    if v == 1:
        return _mcq(rng, "aggregates",
                    "In a SELECT statement, the HAVING clause appears ____.",
                    "after GROUP BY and before ORDER BY",
                    ["before GROUP BY", "after ORDER BY",
                     "immediately after SELECT", "inside the WHERE clause"],
                    "Clause order: SELECT ... FROM ... WHERE ... GROUP BY ... "
                    "HAVING ... ORDER BY. (§3.5)")
    return _mcq(rng, "aggregates",
                "A question asks for the average salary 'in EACH department'. "
                "Which clause does that phrasing signal?",
                "GROUP BY",
                ["ORDER BY", "DISTINCT", "UNION", "LIMIT"],
                "'By / per / in each category' means group the rows: GROUP BY "
                "the category column, then aggregate. (office hours, §3.5)")

def g_orderby(rng, ctx):
    if rng.random() < 0.5:
        return _mcq(rng, "select-where",
                    "By default, ORDER BY sorts rows in ____ order.",
                    "ascending",
                    ["descending", "insertion", "random", "primary key"],
                    "ORDER BY defaults to ascending; add DESC for greatest to "
                    "least. (§3.3)")
    return _mcq(rng, "select-where",
                "Which query lists salaries from GREATEST to LEAST?",
                "SELECT Name, Salary FROM Employee ORDER BY Salary DESC;",
                ["SELECT Name, Salary FROM Employee ORDER BY Salary ASC;",
                 "SELECT Name, Salary FROM Employee ORDER BY Salary;",
                 "SELECT Name, Salary FROM Employee GROUP BY Salary DESC;",
                 "SELECT Name, Salary FROM Employee SORT BY Salary;"],
                "DESC gives descending (greatest first). Plain ORDER BY is "
                "ascending. (office hours, §3.3)")

def g_join_count(rng, ctx):
    # Build two tiny tables with controlled overlap and compute real counts.
    l_only = rng.randrange(1, 3); r_only = rng.randrange(1, 3)
    both = rng.randrange(1, 4)
    l_vals = list(range(1, both + 1)) + [100 + i for i in range(l_only)]
    r_vals = list(range(1, both + 1)) + [200 + i for i in range(r_only)]
    setup = ["CREATE TABLE L (K INT)", "CREATE TABLE R (K INT)"]
    setup += [f"INSERT INTO L VALUES ({v})" for v in l_vals]
    setup += [f"INSERT INTO R VALUES ({v})" for v in r_vals]
    jt, sql = rng.choice([
        ("INNER JOIN", "SELECT * FROM L INNER JOIN R ON L.K = R.K"),
        ("LEFT JOIN", "SELECT * FROM L LEFT JOIN R ON L.K = R.K"),
        ("RIGHT JOIN", "SELECT * FROM L RIGHT JOIN R ON L.K = R.K"),
        ("FULL JOIN", "SELECT * FROM L FULL JOIN R ON L.K = R.K"),
        ("CROSS JOIN", "SELECT * FROM L CROSS JOIN R"),
    ])
    _h, rows = ctx.q(None, sql, setup=setup)
    ans = len(rows)
    l_n, r_n = len(l_vals), len(r_vals)
    prompt = (f"Table L has {l_n} rows and table R has {r_n} rows; their K "
              f"values match on exactly {both} row pair"
              f"{'s' if both != 1 else ''} (one match each). How many rows "
              f"does SELECT * FROM L {jt} R "
              f"{'ON L.K = R.K ' if jt != 'CROSS JOIN' else ''}return?")
    wrongs = {str(x) for x in [both, l_n, r_n, l_n + r_n, l_n + r_n - both,
                               l_n * r_n, ans + 1, ans - 1] if x >= 0} - {str(ans)}
    return _mcq(rng, "joins", prompt, str(ans), sorted(wrongs)[:4],
                f"INNER = matches only ({both}); LEFT = all left rows ({l_n}); "
                f"RIGHT = all right rows ({r_n}); FULL = everything "
                f"({l_n + r_n - both}); CROSS = all combinations "
                f"({l_n}×{r_n}={l_n * r_n}). (§3.6-3.7)")

def g_unmatched_null(rng, ctx):
    side, other = rng.choice([("LEFT", "right"), ("RIGHT", "left")])
    return _mcq(rng, "joins",
                f"In a {side} JOIN result, what appears in the {other}-table "
                f"columns for an unmatched {side.lower()}-table row?",
                "NULL values",
                ["Zeros", "Empty strings", "The row is silently dropped",
                 "The previous row's values"],
                f"A {side} JOIN keeps every {side.lower()}-table row; where no "
                f"{other}-table row matches, those columns show NULL. (§3.6)")

def g_full_join_mysql(rng, ctx):
    if rng.random() < 0.5:
        return _mcq(rng, "joins",
                    "Which JOIN clause is NOT supported by MySQL?",
                    "FULL JOIN",
                    ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "CROSS JOIN"],
                    "MySQL lacks FULL JOIN — you emulate it by UNIONing a "
                    "LEFT JOIN with a RIGHT JOIN. (§3.6)")
    return _mcq(rng, "joins",
                "How is a FULL JOIN emulated in MySQL?",
                "A LEFT JOIN combined with a RIGHT JOIN using UNION",
                ["An INNER JOIN with a WHERE clause",
                 "Two CROSS JOINs on the same key",
                 "A self-join with aliases",
                 "It cannot be emulated"],
                "LEFT JOIN ... UNION ... RIGHT JOIN produces all matched and "
                "unmatched rows from both tables. (§3.6)")

def g_nonequi(rng, ctx):
    return _mcq(rng, "join-types",
                "Which join clauses can be used in a NON-equijoin query?",
                "All join clauses",
                ["INNER JOIN and FULL JOIN only",
                 "LEFT JOIN and RIGHT JOIN only",
                 "CROSS JOIN only", "None — non-equijoins are invalid"],
                "Any join clause works; what makes it a non-equijoin is the "
                "comparison operator (<, >, !=, <>) in ON. (§3.7)")

def g_selfjoin_alias(rng, ctx):
    if rng.random() < 0.5:
        return _tf(rng, "join-types",
                   "In a self-join, each copy of the table must be given an "
                   "alias.", True,
                   "Both copies have the same name, so aliases (e.g., "
                   "Employee E, Employee M) are required to tell them "
                   "apart. (§3.7)")
    return _mcq(rng, "join-types",
                "Which query correctly lists each employee with their "
                "manager's name using a self-join?",
                "SELECT E.Name, M.Name FROM Employee E INNER JOIN Employee M "
                "ON E.ManagerID = M.ID;",
                ["SELECT Name, Name FROM Employee INNER JOIN Employee ON "
                 "ManagerID = ID;",
                 "SELECT E.Name, M.Name FROM Employee CROSS JOIN Employee;",
                 "SELECT Name FROM Employee WHERE ManagerID = ID;"],
                "A self-join needs two aliases and an ON clause relating them "
                "— here the employee's ManagerID to the manager's ID. (§3.7)")

def g_cross_rows(rng, ctx):
    m = rng.randrange(3, 7); n = rng.randrange(3, 7)
    return _mcq(rng, "join-types",
                f"Table A has {m} rows and table B has {n} rows. How many "
                "rows does SELECT * FROM A CROSS JOIN B; return?",
                str(m * n),
                [str(m + n), str(max(m, n)), str(m * n - 1), str(m + n - 1)],
                "A cross-join has no ON clause, so ALL combinations appear: "
                f"{m} × {n} = {m * n} rows. (§3.7)")

def g_subquery(rng, ctx):
    if rng.random() < 0.5:
        return _mcq(rng, "aggregates",
                    "A query nested inside another SQL query is called a ____.",
                    "subquery (nested or inner query)",
                    ["view", "self-join", "stored procedure", "transaction"],
                    "A subquery — also called a nested or inner query — is "
                    "often used with aggregates in a WHERE clause. (§3.5)")
    return _mcq(rng, "aggregates",
                "Which query correctly finds employees earning more than the "
                "average salary?",
                "SELECT Name FROM Employee WHERE Salary > (SELECT AVG(Salary) "
                "FROM Employee);",
                ["SELECT Name FROM Employee WHERE Salary > AVG(Salary);",
                 "SELECT Name FROM Employee HAVING Salary > AVG(Salary);",
                 "SELECT Name, AVG(Salary) FROM Employee WHERE Salary > AVG;"],
                "Aggregates can't sit directly in WHERE — compute the average "
                "in a subquery and compare against it. (§3.5)")

def g_alias(rng, ctx):
    return _mcq(rng, "select-where",
                "Which keyword assigns a temporary name (alias) to a column "
                "or table?",
                "AS", ["ALIAS", "NAME", "REF", "LIKE"],
                "The AS keyword creates an alias — and the keyword itself is "
                "optional (Employee E works too). (§3.6)")

def g_view_qs(rng, ctx):
    v = rng.randrange(3)
    if v == 0:
        return _mcq(rng, "views",
                    "Create a view named MyMovies containing Title and Genre "
                    "from Movie. Which statement?",
                    "CREATE VIEW MyMovies AS SELECT Title, Genre FROM Movie;",
                    ["CREATE VIEW MyMovies (SELECT Title, Genre FROM Movie);",
                     "CREATE TABLE MyMovies AS VIEW Title, Genre FROM Movie;",
                     "CREATE VIEW MyMovies SELECT Title, Genre FROM Movie;",
                     "ALTER VIEW MyMovies ADD Title, Genre FROM Movie;"],
                    "CREATE VIEW ViewName AS SELECT ... — the AS is "
                    "required. (office hours, §3.8)")
    if v == 1:
        return _tf(rng, "views",
                   "MySQL and many other databases do not support "
                   "materialized views.", True,
                   "Materialized views store data at all times and must be "
                   "refreshed; MySQL doesn't support them (regular views are "
                   "virtual). (§3.8)")
    return _mcq(rng, "views",
                "A view created WITH CHECK OPTION will ____.",
                "reject inserts and updates that do not satisfy the view "
                "query's WHERE clause",
                ["refresh automatically whenever base tables change",
                 "store its data permanently on disk",
                 "prevent the view from ever being dropped",
                 "check for duplicate rows in the base table"],
                "WITH CHECK OPTION makes the database generate an error for "
                "changes that violate the view's WHERE clause. (§3.8)")

def g_distinct(rng, ctx):
    return _mcq(rng, "operators",
                "Which keyword removes duplicate values from a SELECT result?",
                "DISTINCT", ["UNIQUE", "DEDUPE", "SINGLE", "ONLY"],
                "SELECT DISTINCT Column returns each value once. (§3.3)")

# --- Chapter 4 ---------------------------------------------------------------

_SCENARIOS = [
 ("A pet owner can have many pets; a specific pet is linked to exactly one "
  "pet owner.", "One-to-many binary",
  "One owner ↔ many pets, two entity types: binary 1:M."),
 ("Employees receive paychecks; each paycheck belongs to one employee, and "
  "an employee receives many paychecks over time.", "One-to-many binary",
  "Employee:Paycheck is the classic 1:M — many paychecks per employee, one "
  "employee per paycheck."),
 ("Many employees are assigned to one office building, and each employee is "
  "assigned to exactly one building.", "Many-to-one binary",
  "Many employees → one building (M:1). Nobody works from several "
  "buildings, so it's not M:N."),
 ("Each employee is assigned exactly one desk, and each desk is assigned to "
  "exactly one employee.", "One-to-one binary",
  "1:1 relationships come from a constraint against sharing — one desk per "
  "employee, one employee per desk."),
 ("Students enroll in classes; a student takes several classes and a class "
  "has many students.", "Many-to-many binary",
  "Many on both sides: M:N binary — implemented later with a junction "
  "table."),
 ("Patients see doctors; a patient may see several doctors and a doctor "
  "treats many patients.", "Many-to-many binary",
  "Many on both sides between two entity types: M:N binary."),
 ("Products appear on orders; an order lists many products and a product "
  "appears on many orders.", "Many-to-many binary",
  "Product:Order is M:N — most real-world business relationships are."),
 ("Each agent at the firm is assigned as a mentor to exactly one other "
  "agent, and each agent has exactly one mentor.", "One-to-one unary",
  "The relationship relates Agent to Agent — one entity type, so UNARY — "
  "with a one-mentor-one-mentee constraint: unary 1:1."),
 ("An employee manages other employees; each employee has one manager, and "
  "a manager manages many employees.", "One-to-many unary",
  "Employee relates to Employee (one entity type = unary), one manager to "
  "many reports: unary 1:M."),
 ("A part can contain many other parts, and a part can be a component of "
  "many other parts.", "Many-to-many unary",
  "Part relates to Part — unary — with many on both sides: unary M:N."),
 ("A doctor prescribes a drug to a patient; the relationship links Doctor, "
  "Drug, and Patient together.", "Ternary",
  "Three entity types participate in one relationship: ternary."),
]

_REL_KINDS = ["One-to-one binary", "One-to-many binary", "Many-to-one binary",
              "Many-to-many binary", "One-to-one unary", "One-to-many unary",
              "Many-to-many unary", "Ternary"]

def g_rel_scenario(rng, ctx):
    desc, correct, why = rng.choice(_SCENARIOS)
    wrongs = [k for k in _REL_KINDS if k != correct]
    return _mcq(rng, "cardinality",
                f"Scenario: {desc} What kind of relationship is this?",
                correct, rng.sample(wrongs, 4),
                why + " Think in tables: how many of each side can attach to "
                "ONE of the other? (§4.3-4.6, office hours)")

def g_bin_una_ter(rng, ctx):
    n, name = rng.choice([(1, "unary"), (2, "binary"), (3, "ternary")])
    if rng.random() < 0.5:
        return _mcq(rng, "rel-kinds",
                    f"A relationship among {n} entity type"
                    f"{'s' if n != 1 else ''} is called ____.",
                    name, [x for x in ["unary", "binary", "ternary"] if x != name]
                    + ["reflexive-composite"],
                    "Unary = 1 entity type (a table related to itself, like a "
                    "unicycle), binary = 2, ternary = 3. (§4.3-4.5)")
    return _mcq(rng, "rel-kinds",
                f"A {name} relationship involves how many entity types?",
                str(n), [str(x) for x in (1, 2, 3, 4) if x != n],
                "Unary = 1, binary = 2 (like a bicycle's two wheels), "
                "ternary = 3. (§4.3-4.5)")

def g_card_max_min(rng, ctx):
    which, ans, other = rng.choice([
        ("cardinality (the relationship maximum)", "the GREATEST number",
         "the LEAST number"),
        ("modality (the relationship minimum)", "the LEAST number",
         "the GREATEST number")])
    return _mcq(rng, "cardinality",
                f"In ER modeling, {which} is ____ of instances of one entity "
                "that can relate to a single instance of another entity.",
                ans, [other, "the average number", "the total number",
                      "the required number of attributes"],
                "Cardinality = maximum; modality = minimum. Exam questions "
                "love swapping these. (§4.6)")

def g_crows_foot(rng, ctx):
    sym, mean = rng.choice([("a circle", "zero"), ("a short line", "one"),
                            ("three short lines (the 'crow's foot')", "many")])
    return _mcq(rng, "cardinality",
                f"In crow's foot notation, {sym} depicts a cardinality of ____.",
                mean, [m for m in ["zero", "one", "many"] if m != mean]
                + ["exactly two"],
                "Crow's foot: circle = zero, short line = one, three short "
                "lines = many. (§4.9)")

def g_weak_entity(rng, ctx):
    v = rng.randrange(3)
    if v == 0:
        return _mcq(rng, "weak-entities",
                    "A weak entity is an entity that ____.",
                    "lacks an identifying attribute of its own and is "
                    "identified through a relationship to another entity",
                    ["has more than one candidate key",
                     "contains fewer than three attributes",
                     "cannot participate in any relationship",
                     "is documented but never stored"],
                    "Weak entities have no identifying attribute; an "
                    "identifying relationship to an identifying entity "
                    "supplies identity. (§4.7)")
    if v == 1:
        return _mcq(rng, "weak-entities",
                    "In an identifying relationship, the cardinality of the "
                    "IDENTIFYING entity is always ____.",
                    "exactly one (1(1))",
                    ["zero or one", "one or many", "zero or many", "exactly two"],
                    "Each weak-entity instance is identified by exactly one "
                    "identifying-entity instance; a diamond replaces that "
                    "cardinality symbol. (§4.7)")
    return _tf(rng, "weak-entities",
               "On an ER diagram, an identifying relationship is marked with "
               "a diamond next to the identifying entity.", True,
               "The diamond replaces the cardinality symbol, since the "
               "identifying entity's cardinality is always exactly one. (§4.7)")

def g_super_sub(rng, ctx):
    v = rng.randrange(3)
    if v == 0:
        sup, sub = rng.choice([("Employee", "Manager"), ("Vehicle", "Truck"),
                               ("Account", "SavingsAccount")])
        return _mcq(rng, "super-sub",
                    f"Every {sub} is a {sup}, so {sub} is a ____ of the "
                    f"{sup} entity.",
                    "subtype", ["supertype", "partition", "weak entity",
                                "candidate key"],
                    f"{sub} is a subset of {sup} — a subtype drawn inside its "
                    "supertype; the identifying relationship is called IsA. (§4.8)")
    if v == 1:
        return _mcq(rng, "super-sub",
                    "A group of MUTUALLY EXCLUSIVE subtype entities is "
                    "called a ____.",
                    "partition", ["cluster", "candidate group", "cascade",
                                  "junction"],
                    "A partition means an instance belongs to at most one of "
                    "the subtypes. (§4.8)")
    return _mcq(rng, "super-sub",
                "The relationship between a subtype entity and its supertype "
                "is called ____.",
                "an IsA relationship",
                ["a HasA relationship", "an identifying relationship",
                 "a reflexive relationship", "a cascading relationship"],
                "Subtype IsA supertype: a Manager IsA Employee. (§4.8)")

_STEPS8 = ["Discover entities, relationships, and attributes",
           "Determine cardinality",
           "Distinguish strong and weak entities",
           "Create supertype and subtype entities",
           "Implement entities",
           "Implement relationships",
           "Implement attributes",
           "Apply normal form"]

def g_steps(rng, ctx):
    if rng.random() < 0.3:
        return _tf(rng, "design-steps",
                   "Creating supertype and subtype entities is the LAST of "
                   "the four analysis steps.", True,
                   "Analysis order: discover E/R/A → cardinality → "
                   "strong/weak → supertype/subtype. Then logical design "
                   "implements and normalizes. (§4.8)")
    i = rng.randrange(len(_STEPS8) - 1)
    correct = _STEPS8[i + 1]
    wrongs = [s for j, s in enumerate(_STEPS8) if j != i + 1 and j != i]
    return _mcq(rng, "design-steps",
                f"In the ER design process, which step comes immediately "
                f"AFTER '{_STEPS8[i]}'?",
                correct, rng.sample(wrongs, 4),
                "The eight steps: discover E/R/A → cardinality → strong/weak "
                "→ super/subtypes → implement entities → relationships → "
                "attributes → apply normal form. (§4.2-4.15)")

def g_impl_rel(rng, ctx):
    v = rng.randrange(3)
    if v == 0:
        a, b = rng.choice([("Department", "Employee"), ("Country", "City"),
                           ("Customer", "Order")])
        return _mcq(rng, "impl",
                    f"One {a} relates to many {b}s. How is this 1:M "
                    "relationship implemented in tables?",
                    f"Add a foreign key to the {b} table (the 'many' side) "
                    f"referencing {a}'s primary key",
                    [f"Add a foreign key to the {a} table referencing {b}",
                     "Create a new junction table with both primary keys",
                     f"Merge {a} and {b} into a single table",
                     "Add a UNIQUE constraint to both tables"],
                    "A 1:M relationship becomes a foreign key on the MANY "
                    "side, pointing at the one side's primary key. (§4.11)")
    if v == 1:
        a, b = rng.choice([("Student", "Class"), ("Product", "Order"),
                           ("Actor", "Film")])
        return _mcq(rng, "impl",
                    f"{a}s and {b}s have a many-to-many relationship. How is "
                    "it implemented?",
                    f"Create a new table whose composite primary key is the "
                    f"two foreign keys referencing {a} and {b}",
                    [f"Add a foreign key to the {a} table only",
                     f"Add a foreign key to the {b} table only",
                     "Add matching UNIQUE columns to both tables",
                     "Many-to-many relationships cannot be implemented"],
                    "M:N needs a junction (associative) table holding both "
                    "keys — its composite PK is the pair of FKs. (§4.11)")
    return _mcq(rng, "impl",
                "How is a ONE-TO-ONE relationship between tables A and B "
                "typically implemented?",
                "Add a foreign key to either table, constrained to be unique",
                ["Create a junction table with a composite primary key",
                 "Add foreign keys to both tables pointing at each other",
                 "It requires a ternary relationship",
                 "Duplicate every column in both tables"],
                "1:1 = a foreign key on either side; making it UNIQUE "
                "enforces the 'one'. (§4.11)")

def g_impl_map(rng, ctx):
    src, dst = rng.choice([("entity type", "a table"),
                           ("attribute type", "a column"),
                           ("relationship type", "a foreign key")])
    all_dst = ["a table", "a column", "a foreign key", "an index"]
    return _mcq(rng, "impl",
                f"During logical design, an {src} usually becomes ____.",
                dst, [d for d in all_dst if d != dst],
                "Entity types → tables, attribute types → columns, "
                "relationship types → foreign keys. (§4.1, §4.10-4.12)")

def g_fd(rng, ctx):
    if rng.random() < 0.5:
        return _mcq(rng, "dependencies",
                    "Column A is functionally dependent on column B when ____.",
                    "each B value is associated with exactly one A value",
                    ["each A value is unique in the table",
                     "A and B have the same data type",
                     "B is a foreign key referencing A",
                     "A and B are both primary keys"],
                    "B determines A: knowing B tells you A. Written B → A "
                    "('A depends on B'). (§4.13)")
    return _mcq(rng, "dependencies",
                "FareClass depends on (FlightCode, FareClass). This "
                "dependency is called ____.",
                "trivial",
                ["partial", "transitive", "composite", "reflexive"],
                "When A's columns are a SUBSET of B's columns, A always "
                "depends on B — a trivial dependency. (§4.14)")

_PD_THEMES = [
 ("ORDER_ITEM", ("OrderNum", "ItemNum"),
  {"OrderDate": "OrderNum", "ItemDesc": "ItemNum", "Quantity": None}),
 ("EMP_PROJ", ("ProjNum", "EmpNum"),
  {"ProjName": "ProjNum", "EmpName": "EmpNum", "Hours": None}),
 ("ENROLLMENT", ("StudentID", "CourseID"),
  {"StudentName": "StudentID", "CourseTitle": "CourseID", "Grade": None}),
]

def g_partial_dep(rng, ctx):
    tname, pk, deps = rng.choice(_PD_THEMES)
    cols = list(pk) + list(deps)
    partials = [(k, v) for k, v in deps.items() if v]
    col, part = rng.choice(partials)
    full = [k for k, v in deps.items() if v is None][0]
    other_part = [p for p in pk if p != part][0]
    correct = f"{part} → {col}"
    wrongs = [f"({pk[0]}, {pk[1]}) → {full}",
              f"({pk[0]}, {pk[1]}) → {col}",
              f"{col} → {full}",
              f"{full} → {other_part}"]
    return _mcq(rng, "dependencies",
                f"Table {tname}({', '.join(cols)}) has the composite primary "
                f"key ({pk[0]}, {pk[1]}). Which of the following is a "
                "PARTIAL dependency?",
                correct, wrongs,
                f"{col} depends on {part} alone — only PART of the composite "
                "key. Dependencies on the whole key are full, not "
                "partial. (§4.13)")

def g_nf_identify(rng, ctx):
    tname = rng.choice(["ORDER_ITEM", "REGISTRATION", "SHIPMENT"])
    v = rng.randrange(4)
    opts = ["Unnormalized (not 1NF)", "1NF", "2NF", "3NF"]
    if v == 0:
        prompt = (f"A {tname} table has a primary key, but its PhoneNumbers "
                  "column stores several phone numbers in one cell. What is "
                  "the highest normal form this table satisfies?")
        correct = "Unnormalized (not 1NF)"
        why = ("1NF requires every entry to be atomic — repeating groups or "
               "multi-valued cells violate it.")
    elif v == 1:
        prompt = (f"{tname} has composite primary key (A, B); non-key column "
                  "C depends on A alone, and D depends on the whole key. "
                  "Entries are atomic. What is the highest normal form?")
        correct = "1NF"
        why = ("C depending on part of the composite key is a PARTIAL "
               "dependency, which blocks 2NF. Atomic entries + PK = 1NF.")
    elif v == 2:
        prompt = (f"{tname} has simple primary key K; non-key column City "
                  "depends on non-key column ZipCode, which depends on K. "
                  "Entries are atomic. What is the highest normal form?")
        correct = "2NF"
        why = ("A simple primary key rules out partial dependencies, so it's "
               "automatically 2NF — but the non-key→non-key (transitive) "
               "dependency ZipCode → City blocks 3NF.")
    else:
        prompt = (f"{tname} has simple primary key K, atomic entries, and "
                  "every non-key column depends directly on K and nothing "
                  "else. What is the highest normal form shown?")
        correct = "3NF"
        why = ("The key, the whole key, and nothing but the key — no partial "
               "or transitive dependencies, so 3NF.")
    return _mcq(rng, "normal-forms", prompt, correct,
                [o for o in opts if o != correct], why + " (§4.13)")

def g_nf_facts(rng, ctx):
    v = rng.randrange(4)
    if v == 0:
        return _tf(rng, "normal-forms",
                   "A table with a simple (single-column) primary key is "
                   "automatically in second normal form.", True,
                   "Partial dependencies require a COMPOSITE key to be "
                   "partial about — a simple key makes 2NF automatic (given "
                   "1NF). (§4.13)")
    if v == 1:
        return _mcq(rng, "normal-forms",
                    "Boyce-Codd normal form is ideal for tables with ____.",
                    "frequent inserts, updates, and deletes",
                    ["mostly read-only reporting queries",
                     "very few rows", "no primary key",
                     "many duplicate rows"],
                    "BCNF — the 'gold standard' — minimizes redundancy, which "
                    "is what makes heavy insert/update/delete traffic "
                    "safe. (§4.14)")
    if v == 2:
        return _mcq(rng, "normal-forms",
                    "Normalization works through a series of normal ____.",
                    "forms", ["schemas", "entities", "databases", "indexes"],
                    "Normal FORMS: 1NF, 2NF, 3NF, BCNF — each removes a kind "
                    "of redundancy. (§4.13)")
    return _mcq(rng, "normal-forms",
                "How does BCNF's definition differ from 3NF's?",
                "It is the 3NF definition with the term 'non-key' removed — "
                "ANY dependent column's determinant must be unique",
                ["It only applies to tables with simple primary keys",
                 "It allows partial dependencies that 3NF forbids",
                 "It requires every column to be a candidate key",
                 "There is no difference"],
                "3NF: whenever a NON-KEY column depends on B, B is unique. "
                "BCNF drops 'non-key': whenever ANY column depends on B, B "
                "is unique. (§4.14)")

# --- Chapter 5 ---------------------------------------------------------------

def g_index_syntax(rng, ctx):
    col = rng.choice(["ReleaseDate", "LastName", "Price"])
    tbl = rng.choice(["Movie", "Customer", "Product"])
    return _mcq(rng, "indexes",
                f"Create an index named Idx{col} on the {col} column of the "
                f"{tbl} table. Which statement?",
                f"CREATE INDEX Idx{col} ON {tbl}({col});",
                [f"CREATE INDEX Idx{col} FROM {tbl}({col});",
                 f"ALTER TABLE {tbl} CREATE INDEX Idx{col} ({col});",
                 f"CREATE Idx{col} INDEX ON {tbl}.{col};",
                 f"INSERT INDEX Idx{col} INTO {tbl}({col});"],
                "CREATE INDEX IndexName ON TableName (Column, ...); (§5.2, "
                "office hours)")

def g_why_index(rng, ctx):
    return _mcq(rng, "indexes",
                "Why would a database designer create an index?",
                "To speed up slow queries on large tables by letting the "
                "database locate data efficiently",
                ["To change the results that queries return",
                 "To enforce referential integrity",
                 "To reduce the number of columns in a table",
                 "To convert a heap table into a view"],
                "Indexes speed up query processing; by data independence "
                "they never change query RESULTS. (§5.2, §1.4)")

def g_heap_fact(rng, ctx):
    return _mcq(rng, "table-struct",
                "Which table structure is particularly fast for BULK LOADING "
                "many rows?",
                "A heap table, since rows are simply stored in load order",
                ["A sorted table, since rows arrive pre-sorted",
                 "A hash table, since buckets never overflow",
                 "A table cluster, since tables share storage"],
                "Heap tables impose no order and track free space in a "
                "linked list — inserts and bulk loads are their "
                "strength. (§5.1)")

# --- SQL hands-on tasks ------------------------------------------------------
# Each runs on a FRESH copy of the sample database, so playground experiments
# never break the grading. Reference solutions double as the reveal.

def _sqltask(cid, db, prompt, reference, kind="select", order=False,
             verify=None, hint=None, ddl_check=None):
    return {"type": "sql", "concept": cid, "db": db, "prompt": prompt,
            "reference": reference, "kind": kind, "order_matters": order,
            "verify": verify, "hint": hint, "ddl_check": ddl_check}

def s_horse_where(rng, ctx):
    breed, h = rng.choice([("Quarter Horse", 15.0), ("Quarter Horse", 14.5),
                           ("Holsteiner", 15.5), ("Paint", 14.0),
                           ("Egyptian Arab", 13.5)])
    return _sqltask("select-where", "stable",
        f"List the RegisteredName and Height of every horse whose Breed is "
        f"'{breed}' AND whose Height is greater than {h}.\n"
        f"(Columns: RegisteredName, Height — in that order.)",
        f"SELECT RegisteredName, Height FROM Horse WHERE Breed = '{breed}' "
        f"AND Height > {h}",
        hint="SELECT col1, col2 FROM Horse WHERE ... AND ... ;  Strings take "
             "single quotes; numbers don't.")

def s_horse_insert(rng, ctx):
    nm = rng.choice(["Sunset Glory", "Copper Sky", "Sable Trail"])
    br = rng.choice(["Saddlebred", "Paint", "Holsteiner"])
    ht = rng.choice([14.6, 15.1, 16.2])
    bd = rng.choice(["2020-03-15", "2021-07-04", "2019-11-30"])
    return _sqltask("dml", "stable",
        f"Insert a new horse: RegisteredName '{nm}', Breed '{br}', Height "
        f"{ht}, BirthDate '{bd}'. The ID column is AUTO_INCREMENT — do not "
        "supply it.",
        f"INSERT INTO Horse (RegisteredName, Breed, Height, BirthDate) "
        f"VALUES ('{nm}', '{br}', {ht}, '{bd}')",
        kind="dml",
        verify="SELECT RegisteredName, Breed, Height, BirthDate FROM Horse",
        hint="INSERT INTO Horse (col, col, ...) VALUES (...); — name the "
             "columns so the auto-increment ID assigns itself.")

def s_horse_update(rng, ctx):
    hid = rng.choice([6, 9])
    nm = rng.choice(["Beacon", "Onyx", "Juniper"])
    return _sqltask("dml", "stable",
        f"The horse with ID {hid} has no RegisteredName. Update that row so "
        f"RegisteredName is '{nm}'.",
        f"UPDATE Horse SET RegisteredName = '{nm}' WHERE ID = {hid}",
        kind="dml",
        verify="SELECT ID, RegisteredName FROM Horse",
        hint="UPDATE Horse SET column = value WHERE ...; — without the "
             "WHERE, EVERY horse gets renamed.")

def s_horse_delete(rng, ctx):
    d = rng.choice(["2021-12-31", "2020-12-31"])
    return _sqltask("dml", "stable",
        f"Delete every horse whose BirthDate is after '{d}'.",
        f"DELETE FROM Horse WHERE BirthDate > '{d}'",
        kind="dml",
        verify="SELECT ID, RegisteredName FROM Horse",
        hint="DELETE FROM Horse WHERE ...; — dates compare with > and quotes.")

def s_lessons_inner(rng, ctx):
    return _sqltask("joins", "stable",
        "For every scheduled lesson with a student assigned, list the "
        "student's FirstName, LastName, and the LessonDateTime, using an "
        "INNER JOIN between Student and LessonSchedule.\n"
        "(Columns: FirstName, LastName, LessonDateTime.)",
        "SELECT FirstName, LastName, LessonDateTime FROM Student "
        "INNER JOIN LessonSchedule ON Student.ID = LessonSchedule.StudentID",
        hint="... FROM Student INNER JOIN LessonSchedule ON Student.ID = "
             "LessonSchedule.StudentID")

def s_lessons_triple(rng, ctx):
    return _sqltask("joins", "stable",
        "List each lesson's horse RegisteredName, student LastName, and "
        "LessonDateTime by joining LessonSchedule to Horse AND to Student "
        "with INNER JOINs.\n(Columns: RegisteredName, LastName, "
        "LessonDateTime.)",
        "SELECT RegisteredName, LastName, LessonDateTime FROM LessonSchedule "
        "INNER JOIN Horse ON LessonSchedule.HorseID = Horse.ID "
        "INNER JOIN Student ON LessonSchedule.StudentID = Student.ID",
        hint="Chain two INNER JOINs: LessonSchedule → Horse ON HorseID = "
             "Horse.ID, then → Student ON StudentID = Student.ID.")

def s_left_join_movies(rng, ctx):
    return _sqltask("joins", "movies",
        "List EVERY movie's Title with its streaming ServiceName, including "
        "movies not on any service (their ServiceName should show as NULL). "
        "Use a LEFT JOIN from Movie to Streaming.\n"
        "(Columns: Title, ServiceName.)",
        "SELECT Title, ServiceName FROM Movie "
        "LEFT JOIN Streaming ON Movie.StreamID = Streaming.StreamID",
        hint="LEFT JOIN keeps all left-table (Movie) rows: FROM Movie LEFT "
             "JOIN Streaming ON Movie.StreamID = Streaming.StreamID")

def s_group_genre(rng, ctx):
    return _sqltask("aggregates", "movies",
        "For each Genre, count how many movies there are.\n"
        "(Columns: Genre, then the count.)",
        "SELECT Genre, COUNT(*) FROM Movie GROUP BY Genre",
        hint="'For each Genre' signals GROUP BY Genre; COUNT(*) counts the "
             "rows in each group.")

def s_year_between(rng, ctx):
    a = rng.choice([2016, 2018, 2019]); b = a + rng.choice([3, 4])
    return _sqltask("operators", "movies",
        f"List the Titles of movies released between {a} and {b} "
        "(inclusive), in alphabetical order. Use the YEAR() function on "
        "ReleaseDate.\n(Column: Title.)",
        f"SELECT Title FROM Movie WHERE YEAR(ReleaseDate) BETWEEN {a} AND {b} "
        "ORDER BY Title",
        order=True,
        hint=f"WHERE YEAR(ReleaseDate) BETWEEN {a} AND {b} ORDER BY Title")

def s_like_titles(rng, ctx):
    pat, desc = rng.choice([("The %", "start with 'The '"),
                            ("%er%", "contain 'er' anywhere"),
                            ("S%", "start with the letter S")])
    return _sqltask("operators", "movies",
        f"List the Titles of movies whose Title values {desc}. Use LIKE.\n"
        "(Column: Title.)",
        f"SELECT Title FROM Movie WHERE Title LIKE '{pat}'",
        hint=f"WHERE Title LIKE '{pat}' — % matches any number of characters.")

def s_view_create(rng, ctx):
    g = rng.choice(["Comedy", "Drama", "Action"])
    return _sqltask("views", "movies",
        f"Create a view named {g}View containing the Title and ReleaseDate "
        f"of every {g} movie. (You will be graded by querying the view.)",
        f"CREATE VIEW {g}View AS SELECT Title, ReleaseDate FROM Movie "
        f"WHERE Genre = '{g}'",
        kind="dml",
        verify=f"SELECT * FROM {g}View",
        hint="CREATE VIEW name AS SELECT ... FROM ... WHERE ...;")

def s_alter_add(rng, ctx):
    return _sqltask("alter", "movies",
        "Add a new column Rating to the Movie table that stores numeric "
        "values with 2 total digits, 1 after the decimal point.",
        "ALTER TABLE Movie ADD Rating DECIMAL(2,1)",
        kind="ddl",
        ddl_check={"table": "Movie", "has_columns": [("Rating", "DECIMAL")]},
        hint="ALTER TABLE Movie ADD ColumnName TYPE; — DECIMAL(M,D) is M "
             "total digits, D after the point.")

def s_create_table(rng, ctx):
    return _sqltask("ddl-tables", "stable",
        "Create a table named RidingLesson2 with columns:\n"
        "  - HorseID, integer, NOT NULL\n"
        "  - StudentID, integer\n"
        "  - LessonDateTime, DATETIME, NOT NULL\n"
        "with (HorseID, LessonDateTime) as a composite PRIMARY KEY, a "
        "FOREIGN KEY from HorseID to Horse(ID), and a FOREIGN KEY from "
        "StudentID to Student(ID).",
        "CREATE TABLE RidingLesson2 ("
        "HorseID INT NOT NULL, StudentID INT, LessonDateTime DATETIME NOT NULL, "
        "PRIMARY KEY (HorseID, LessonDateTime), "
        "FOREIGN KEY (HorseID) REFERENCES Horse(ID), "
        "FOREIGN KEY (StudentID) REFERENCES Student(ID))",
        kind="ddl",
        ddl_check={"table": "RidingLesson2",
                   "has_columns": [("HorseID", "INT"), ("StudentID", "INT"),
                                    ("LessonDateTime", "DATETIME")],
                   "pk": ["HorseID", "LessonDateTime"],
                   "fks": [("HorseID", "Horse"), ("StudentID", "Student")]},
        hint="Composite PK goes on its own line: PRIMARY KEY (colA, colB). "
             "Each FK: FOREIGN KEY (col) REFERENCES Parent(col).")

def s_raise_update(rng, ctx):
    amt = rng.choice([1000, 1500, 2000]); cap = rng.choice([50000, 48000])
    return _sqltask("dml", "company",
        f"Give a ${amt} raise to every employee making less than ${cap} — "
        "add it to their current Salary.",
        f"UPDATE Employee SET Salary = Salary + {amt} WHERE Salary < {cap}",
        kind="dml",
        verify="SELECT ID, Salary FROM Employee",
        hint="SET Salary = Salary + amount — the column can reference "
             "itself. Don't forget the WHERE. (This is the office-hours "
             "drill.)")

def s_salary_order(rng, ctx):
    cap = rng.choice([60000, 65000, 70000])
    return _sqltask("select-where", "company",
        f"Display the Name and Salary of every employee making less than "
        f"${cap}, from GREATEST to LEAST salary.\n(Columns: Name, Salary.)",
        f"SELECT Name, Salary FROM Employee WHERE Salary < {cap} "
        "ORDER BY Salary DESC",
        order=True,
        hint="Greatest-to-least means ORDER BY Salary DESC. No GROUP BY — "
             "nothing is being put into categories.")

def s_having_avg(rng, ctx):
    t = rng.choice([55000, 60000])
    return _sqltask("aggregates", "company",
        f"For each DeptID, show the DeptID and average Salary — but only "
        f"for departments whose average salary exceeds ${t}.\n"
        "(Columns: DeptID, then the average.)",
        f"SELECT DeptID, AVG(Salary) FROM Employee GROUP BY DeptID "
        f"HAVING AVG(Salary) > {t}",
        hint="Filter GROUPS with HAVING (after GROUP BY), not WHERE.")

def s_self_join(rng, ctx):
    return _sqltask("join-types", "company",
        "Using a self-join on Employee, list each employee's Name and their "
        "manager's Name. Alias the copies E and M, and join E.ManagerID to "
        "M.ID.\n(Columns: employee name, manager name.)",
        "SELECT E.Name, M.Name FROM Employee E "
        "INNER JOIN Employee M ON E.ManagerID = M.ID",
        hint="FROM Employee E INNER JOIN Employee M ON E.ManagerID = M.ID — "
             "aliases are required in a self-join.")

def s_subquery_avg(rng, ctx):
    return _sqltask("aggregates", "company",
        "List the Name of every employee whose Salary is above the company "
        "average. Use a subquery.\n(Column: Name.)",
        "SELECT Name FROM Employee WHERE Salary > "
        "(SELECT AVG(Salary) FROM Employee)",
        hint="Aggregates can't sit in WHERE directly — compare against "
             "(SELECT AVG(Salary) FROM Employee).")

def s_delete_emp(rng, ctx):
    victim = rng.choice([("Finn Walsh", 6), ("Hank Doyle", 8),
                         ("Kim Reyes", 11), ("Leo Grant", 12)])
    return _sqltask("dml", "company",
        f"{victim[0]} (ID {victim[1]}) has left the company. Delete that "
        "employee's row.",
        f"DELETE FROM Employee WHERE ID = {victim[1]}",
        kind="dml",
        verify="SELECT ID, Name FROM Employee",
        hint="DELETE FROM Employee WHERE ID = ...; — DELETE removes rows; "
             "DROP would remove the whole table.")

def s_country_in(rng, ctx):
    c1, c2 = rng.sample(["Europe", "Asia", "Africa", "North America"], 2)
    return _sqltask("operators", "world",
        f"List the Name of every country whose Continent is '{c1}' or "
        f"'{c2}' using the IN operator, alphabetically.\n(Column: Name.)",
        f"SELECT Name FROM Country WHERE Continent IN ('{c1}', '{c2}') "
        "ORDER BY Name",
        order=True,
        hint=f"WHERE Continent IN ('{c1}', '{c2}') — IN is shorthand for "
             "chained ORs.")

def s_continent_sum(rng, ctx):
    return _sqltask("aggregates", "world",
        "For each Continent, show the Continent and the SUM of its "
        "countries' Population.\n(Columns: Continent, then the sum.)",
        "SELECT Continent, SUM(Population) FROM Country GROUP BY Continent",
        hint="'For each Continent' → GROUP BY Continent, then SUM(Population).")

def s_city_join(rng, ctx):
    p = rng.choice([3000000, 5000000])
    return _sqltask("joins", "world",
        f"List each city Name with its country's Name for cities whose "
        f"Population exceeds {p:,}. Use an INNER JOIN.\n"
        "(Columns: city name, country name.)",
        f"SELECT City.Name, Country.Name FROM City INNER JOIN Country "
        f"ON City.CountryCode = Country.Code WHERE City.Population > {p}",
        hint="Qualify the ambiguous Name columns: City.Name, Country.Name. "
             "Join ON City.CountryCode = Country.Code.")

MCQ_GENERATORS = ([_pool_gen(k) for k in POOLS] + [
    g_unstructured, g_synonyms, g_record_fields, g_set_tuple,
    g_rows_unordered, g_empty_table, g_duis, g_mysql_fact,
    g_design_phase_pick, g_data_independence,
    g_create_syntax, g_type_bytes, g_type_range, g_type_pick, g_char_varchar,
    g_quotes, g_null_meaning, g_insert_syntax, g_autoinc, g_where_omitted,
    g_vict, g_truncate, g_pk_rules, g_fk_rules, g_ri_scenario,
    g_constraint_pick, g_alter_cad, g_comment,
    g_like, g_wildcards, g_between, g_null_compare, g_func_output,
    g_agg_nulls, g_agg_pick, g_having, g_orderby, g_join_count,
    g_unmatched_null, g_full_join_mysql, g_nonequi, g_selfjoin_alias,
    g_cross_rows, g_subquery, g_alias, g_view_qs, g_distinct,
    g_rel_scenario, g_bin_una_ter, g_card_max_min, g_crows_foot,
    g_weak_entity, g_super_sub, g_steps, g_impl_rel, g_impl_map, g_fd,
    g_partial_dep, g_nf_identify, g_nf_facts,
    g_index_syntax, g_why_index, g_heap_fact,
])

SQL_GENERATORS = [
    s_horse_where, s_horse_insert, s_horse_update, s_horse_delete,
    s_lessons_inner, s_lessons_triple, s_left_join_movies, s_group_genre,
    s_year_between, s_like_titles, s_view_create, s_alter_add,
    s_create_table, s_raise_update, s_salary_order, s_having_avg,
    s_self_join, s_subquery_avg, s_delete_emp, s_country_in,
    s_continent_sum, s_city_join,
]

