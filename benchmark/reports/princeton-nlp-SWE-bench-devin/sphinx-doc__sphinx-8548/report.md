# sphinx-doc__sphinx-8548

| **sphinx-doc/sphinx** | `dd1615c59dc6fff633e27dbb3861f2d27e1fb976` |
| ---- | ---- |
| **No of patches** | 2 |
| **All found context length** | 4696 |
| **Any found context length** | 4696 |
| **Avg pos** | 105.5 |
| **Min pos** | 7 |
| **Max pos** | 62 |
| **Top file pos** | 1 |
| **Missing snippets** | 4 |
| **Missing patch files** | 0 |


## Expected patch

```diff
diff --git a/sphinx/ext/autodoc/__init__.py b/sphinx/ext/autodoc/__init__.py
--- a/sphinx/ext/autodoc/__init__.py
+++ b/sphinx/ext/autodoc/__init__.py
@@ -1584,7 +1584,7 @@ def add_directive_header(self, sig: str) -> None:
                 self.add_line('   ' + _('Bases: %s') % ', '.join(bases), sourcename)
 
     def get_object_members(self, want_all: bool) -> Tuple[bool, ObjectMembers]:
-        members = get_class_members(self.object, self.objpath, self.get_attr, self.analyzer)
+        members = get_class_members(self.object, self.objpath, self.get_attr)
         if not want_all:
             if not self.options.members:
                 return False, []  # type: ignore
diff --git a/sphinx/ext/autodoc/importer.py b/sphinx/ext/autodoc/importer.py
--- a/sphinx/ext/autodoc/importer.py
+++ b/sphinx/ext/autodoc/importer.py
@@ -14,7 +14,7 @@
 from typing import Any, Callable, Dict, List, Mapping, NamedTuple, Optional, Tuple
 
 from sphinx.deprecation import RemovedInSphinx40Warning, deprecated_alias
-from sphinx.pycode import ModuleAnalyzer
+from sphinx.pycode import ModuleAnalyzer, PycodeError
 from sphinx.util import logging
 from sphinx.util.inspect import (getannotations, getmro, getslots, isclass, isenumclass,
                                  safe_getattr)
@@ -251,8 +251,8 @@ def __init__(self, cls: Any, name: str, value: Any, docstring: Optional[str] = N
         self.docstring = docstring
 
 
-def get_class_members(subject: Any, objpath: List[str], attrgetter: Callable,
-                      analyzer: ModuleAnalyzer = None) -> Dict[str, ClassAttribute]:
+def get_class_members(subject: Any, objpath: List[str], attrgetter: Callable
+                      ) -> Dict[str, ClassAttribute]:
     """Get members and attributes of target class."""
     from sphinx.ext.autodoc import INSTANCEATTR
 
@@ -297,23 +297,31 @@ def get_class_members(subject: Any, objpath: List[str], attrgetter: Callable,
         except AttributeError:
             continue
 
-    # annotation only member (ex. attr: int)
-    for cls in getmro(subject):
-        try:
-            for name in getannotations(cls):
-                name = unmangle(cls, name)
-                if name and name not in members:
-                    members[name] = ClassAttribute(cls, name, INSTANCEATTR)
-        except AttributeError:
-            pass
-
-    if analyzer:
-        # append instance attributes (cf. self.attr1) if analyzer knows
-        namespace = '.'.join(objpath)
-        for (ns, name), docstring in analyzer.attr_docs.items():
-            if namespace == ns and name not in members:
-                members[name] = ClassAttribute(subject, name, INSTANCEATTR,
-                                               '\n'.join(docstring))
+    try:
+        for cls in getmro(subject):
+            # annotation only member (ex. attr: int)
+            try:
+                for name in getannotations(cls):
+                    name = unmangle(cls, name)
+                    if name and name not in members:
+                        members[name] = ClassAttribute(cls, name, INSTANCEATTR)
+            except AttributeError:
+                pass
+
+            # append instance attributes (cf. self.attr1) if analyzer knows
+            try:
+                modname = safe_getattr(cls, '__module__')
+                qualname = safe_getattr(cls, '__qualname__')
+                analyzer = ModuleAnalyzer.for_module(modname)
+                analyzer.analyze()
+                for (ns, name), docstring in analyzer.attr_docs.items():
+                    if ns == qualname and name not in members:
+                        members[name] = ClassAttribute(cls, name, INSTANCEATTR,
+                                                       '\n'.join(docstring))
+            except (AttributeError, PycodeError):
+                pass
+    except AttributeError:
+        pass
 
     return members
 

```

## Expected file changes

| File | Start line | End line | Found on position | Found file position | Context length |
| ---- | ---------- | -------- | ----------------- | ------------------- | -------------- |
| sphinx/ext/autodoc/__init__.py | 1587 | 1587 | 62 | 1 | 20079
| sphinx/ext/autodoc/importer.py | 17 | 17 | 58 | 3 | 18929
| sphinx/ext/autodoc/importer.py | 254 | 255 | 42 | 3 | 14233
| sphinx/ext/autodoc/importer.py | 300 | 316 | 42 | 3 | 14233


## Problem Statement

```
autodoc inherited-members won't work for inherited attributes (data members).
autodoc searches for a cached docstring using (namespace, attrname) as search-key, but doesn't check for baseclass-namespace.

---
- Bitbucket: https://bitbucket.org/birkenfeld/sphinx/issue/741
- Originally reported by: Anonymous
- Originally created at: 2011-08-02T17:05:58.754


```

## Retrieved code snippets

| Position | File | Start line | End line | Tokens | Sum tokens | File tokens |
| -------- | ---- | ---------- | -------- | ------ | ---------- | ----------- |
| 1 | **1 sphinx/ext/autodoc/__init__.py** | 693 | 799| 868 | 868 | 21215 | 
| 2 | **1 sphinx/ext/autodoc/__init__.py** | 2312 | 2335| 216 | 1084 | 21215 | 
| 3 | **1 sphinx/ext/autodoc/__init__.py** | 1035 | 1063| 232 | 1316 | 21215 | 
| 4 | **1 sphinx/ext/autodoc/__init__.py** | 1900 | 1913| 145 | 1461 | 21215 | 
| 5 | **1 sphinx/ext/autodoc/__init__.py** | 2361 | 2380| 260 | 1721 | 21215 | 
| 6 | **1 sphinx/ext/autodoc/__init__.py** | 2217 | 2234| 177 | 1898 | 21215 | 
| **-> 7 <-** | **1 sphinx/ext/autodoc/__init__.py** | 1386 | 1681| 2798 | 4696 | 21215 | 
| 8 | **1 sphinx/ext/autodoc/__init__.py** | 573 | 585| 133 | 4829 | 21215 | 
| 9 | **1 sphinx/ext/autodoc/__init__.py** | 2237 | 2271| 284 | 5113 | 21215 | 
| 10 | **1 sphinx/ext/autodoc/__init__.py** | 2273 | 2290| 197 | 5310 | 21215 | 
| 11 | 2 sphinx/ext/autodoc/deprecated.py | 78 | 93| 139 | 5449 | 22175 | 
| 12 | **2 sphinx/ext/autodoc/__init__.py** | 2337 | 2359| 276 | 5725 | 22175 | 
| 13 | **2 sphinx/ext/autodoc/__init__.py** | 2462 | 2500| 445 | 6170 | 22175 | 
| 14 | **2 sphinx/ext/autodoc/__init__.py** | 2134 | 2148| 163 | 6333 | 22175 | 
| 15 | **2 sphinx/ext/autodoc/__init__.py** | 2432 | 2462| 365 | 6698 | 22175 | 
| 16 | **2 sphinx/ext/autodoc/__init__.py** | 2151 | 2181| 217 | 6915 | 22175 | 
| 17 | **3 sphinx/ext/autodoc/importer.py** | 163 | 177| 125 | 7040 | 24774 | 
| 18 | **3 sphinx/ext/autodoc/__init__.py** | 2183 | 2215| 273 | 7313 | 24774 | 
| 19 | 3 sphinx/ext/autodoc/deprecated.py | 32 | 47| 140 | 7453 | 24774 | 
| 20 | **3 sphinx/ext/autodoc/__init__.py** | 289 | 363| 784 | 8237 | 24774 | 
| 21 | **3 sphinx/ext/autodoc/__init__.py** | 1004 | 1020| 172 | 8409 | 24774 | 
| 22 | 3 sphinx/ext/autodoc/deprecated.py | 96 | 111| 133 | 8542 | 24774 | 
| 23 | 4 sphinx/ext/autodoc/mock.py | 71 | 93| 200 | 8742 | 25881 | 
| 24 | **4 sphinx/ext/autodoc/__init__.py** | 1065 | 1082| 177 | 8919 | 25881 | 
| 25 | **4 sphinx/ext/autodoc/__init__.py** | 2082 | 2101| 181 | 9100 | 25881 | 
| 26 | **4 sphinx/ext/autodoc/__init__.py** | 1876 | 1898| 245 | 9345 | 25881 | 
| 27 | **4 sphinx/ext/autodoc/__init__.py** | 13 | 116| 790 | 10135 | 25881 | 
| 28 | **4 sphinx/ext/autodoc/__init__.py** | 1106 | 1136| 287 | 10422 | 25881 | 
| 29 | **4 sphinx/ext/autodoc/importer.py** | 74 | 137| 597 | 11019 | 25881 | 
| 30 | 5 sphinx/ext/autosummary/generate.py | 269 | 282| 202 | 11221 | 31130 | 
| 31 | **5 sphinx/ext/autodoc/__init__.py** | 119 | 152| 207 | 11428 | 31130 | 
| 32 | **5 sphinx/ext/autodoc/__init__.py** | 1085 | 1103| 179 | 11607 | 31130 | 
| 33 | **5 sphinx/ext/autodoc/importer.py** | 321 | 340| 180 | 11787 | 31130 | 
| 34 | **5 sphinx/ext/autodoc/__init__.py** | 1022 | 1033| 126 | 11913 | 31130 | 
| 35 | **5 sphinx/ext/autodoc/__init__.py** | 2292 | 2310| 201 | 12114 | 31130 | 
| 36 | **5 sphinx/ext/autodoc/__init__.py** | 801 | 844| 453 | 12567 | 31130 | 
| 37 | **5 sphinx/ext/autodoc/__init__.py** | 1839 | 1874| 285 | 12852 | 31130 | 
| 38 | **5 sphinx/ext/autodoc/__init__.py** | 2104 | 2132| 209 | 13061 | 31130 | 
| 39 | **5 sphinx/ext/autodoc/__init__.py** | 1211 | 1231| 241 | 13302 | 31130 | 
| 40 | **5 sphinx/ext/autodoc/__init__.py** | 1800 | 1836| 290 | 13592 | 31130 | 
| 41 | **5 sphinx/ext/autodoc/__init__.py** | 2414 | 2429| 126 | 13718 | 31130 | 
| **-> 42 <-** | **5 sphinx/ext/autodoc/importer.py** | 254 | 318| 515 | 14233 | 31130 | 
| 43 | 5 sphinx/ext/autosummary/generate.py | 225 | 240| 184 | 14417 | 31130 | 
| 44 | **5 sphinx/ext/autodoc/__init__.py** | 1684 | 1719| 262 | 14679 | 31130 | 
| 45 | 5 sphinx/ext/autodoc/deprecated.py | 114 | 127| 114 | 14793 | 31130 | 
| 46 | **5 sphinx/ext/autodoc/__init__.py** | 250 | 286| 297 | 15090 | 31130 | 
| 47 | 6 sphinx/application.py | 1056 | 1077| 265 | 15355 | 42420 | 
| 48 | **6 sphinx/ext/autodoc/__init__.py** | 376 | 411| 315 | 15670 | 42420 | 
| 49 | **6 sphinx/ext/autodoc/__init__.py** | 654 | 692| 304 | 15974 | 42420 | 
| 50 | **6 sphinx/ext/autodoc/importer.py** | 180 | 251| 539 | 16513 | 42420 | 
| 51 | **6 sphinx/ext/autodoc/__init__.py** | 1722 | 1738| 135 | 16648 | 42420 | 
| 52 | **6 sphinx/ext/autodoc/__init__.py** | 365 | 374| 121 | 16769 | 42420 | 
| 53 | **6 sphinx/ext/autodoc/__init__.py** | 626 | 652| 306 | 17075 | 42420 | 
| 54 | **6 sphinx/ext/autodoc/__init__.py** | 1252 | 1352| 836 | 17911 | 42420 | 
| 55 | **6 sphinx/ext/autodoc/__init__.py** | 2383 | 2411| 247 | 18158 | 42420 | 
| 56 | **6 sphinx/ext/autodoc/__init__.py** | 1784 | 1797| 136 | 18294 | 42420 | 
| 57 | 6 sphinx/ext/autodoc/mock.py | 11 | 68| 451 | 18745 | 42420 | 
| **-> 58 <-** | **6 sphinx/ext/autodoc/importer.py** | 11 | 37| 184 | 18929 | 42420 | 
| 59 | **6 sphinx/ext/autodoc/__init__.py** | 1916 | 1931| 120 | 19049 | 42420 | 
| 60 | 7 sphinx/ext/autodoc/directive.py | 109 | 159| 453 | 19502 | 43681 | 
| 61 | **7 sphinx/ext/autodoc/__init__.py** | 960 | 1002| 388 | 19890 | 43681 | 
| **-> 62 <-** | **7 sphinx/ext/autodoc/__init__.py** | 1355 | 1681| 189 | 20079 | 43681 | 
| 63 | 8 sphinx/ext/inheritance_diagram.py | 38 | 66| 233 | 20312 | 47543 | 
| 64 | 8 sphinx/application.py | 1079 | 1092| 174 | 20486 | 47543 | 
| 65 | **8 sphinx/ext/autodoc/__init__.py** | 1741 | 1757| 137 | 20623 | 47543 | 
| 66 | 8 sphinx/ext/autodoc/directive.py | 9 | 49| 298 | 20921 | 47543 | 
| 67 | **8 sphinx/ext/autodoc/__init__.py** | 1934 | 2079| 1279 | 22200 | 47543 | 
| 68 | 8 sphinx/ext/autosummary/generate.py | 172 | 191| 176 | 22376 | 47543 | 
| 69 | 9 sphinx/domains/python.py | 908 | 920| 132 | 22508 | 59448 | 
| 70 | 10 doc/usage/extensions/example_google.py | 261 | 275| 109 | 22617 | 61558 | 
| 71 | 10 sphinx/domains/python.py | 727 | 781| 530 | 23147 | 61558 | 
| 72 | 10 doc/usage/extensions/example_google.py | 277 | 296| 120 | 23267 | 61558 | 
| 73 | 10 sphinx/ext/autosummary/generate.py | 242 | 267| 298 | 23565 | 61558 | 
| 74 | 11 doc/usage/extensions/example_numpy.py | 320 | 334| 109 | 23674 | 63666 | 
| 75 | 11 doc/usage/extensions/example_numpy.py | 336 | 356| 120 | 23794 | 63666 | 
| 76 | 12 sphinx/util/__init__.py | 480 | 493| 123 | 23917 | 69968 | 
| 77 | **12 sphinx/ext/autodoc/__init__.py** | 871 | 957| 804 | 24721 | 69968 | 
| 78 | **12 sphinx/ext/autodoc/__init__.py** | 413 | 432| 182 | 24903 | 69968 | 
| 79 | 12 sphinx/ext/autosummary/generate.py | 20 | 57| 275 | 25178 | 69968 | 
| 80 | 12 sphinx/ext/autosummary/generate.py | 87 | 114| 269 | 25447 | 69968 | 
| 81 | 13 sphinx/ext/napoleon/docstring.py | 811 | 824| 153 | 25600 | 80518 | 
| 82 | 14 sphinx/ext/napoleon/__init__.py | 398 | 481| 740 | 26340 | 84476 | 
| 83 | **14 sphinx/ext/autodoc/__init__.py** | 1234 | 1249| 166 | 26506 | 84476 | 
| 84 | 14 sphinx/ext/napoleon/docstring.py | 781 | 809| 213 | 26719 | 84476 | 
| 85 | 14 sphinx/ext/autosummary/generate.py | 466 | 487| 217 | 26936 | 84476 | 
| 86 | **14 sphinx/ext/autodoc/__init__.py** | 434 | 482| 359 | 27295 | 84476 | 
| 87 | **14 sphinx/ext/autodoc/__init__.py** | 846 | 869| 246 | 27541 | 84476 | 
| 88 | 14 sphinx/ext/autodoc/deprecated.py | 11 | 29| 155 | 27696 | 84476 | 
| 89 | **14 sphinx/ext/autodoc/__init__.py** | 558 | 571| 131 | 27827 | 84476 | 
| 90 | 14 sphinx/ext/autodoc/deprecated.py | 65 | 75| 108 | 27935 | 84476 | 
| 91 | 14 sphinx/ext/napoleon/docstring.py | 284 | 292| 121 | 28056 | 84476 | 
| 92 | **14 sphinx/ext/autodoc/__init__.py** | 1139 | 1209| 528 | 28584 | 84476 | 
| 93 | **14 sphinx/ext/autodoc/importer.py** | 40 | 56| 125 | 28709 | 84476 | 
| 94 | 15 doc/conf.py | 59 | 127| 688 | 29397 | 86034 | 
| 95 | 15 sphinx/ext/autodoc/deprecated.py | 50 | 62| 113 | 29510 | 86034 | 
| 96 | **15 sphinx/ext/autodoc/__init__.py** | 587 | 624| 378 | 29888 | 86034 | 
| 97 | 15 sphinx/ext/napoleon/docstring.py | 602 | 627| 255 | 30143 | 86034 | 
| 98 | 15 sphinx/ext/autosummary/generate.py | 284 | 340| 606 | 30749 | 86034 | 
| 99 | **15 sphinx/ext/autodoc/importer.py** | 140 | 160| 147 | 30896 | 86034 | 
| 100 | **15 sphinx/ext/autodoc/__init__.py** | 541 | 556| 206 | 31102 | 86034 | 
| 101 | 16 sphinx/util/cfamily.py | 179 | 230| 341 | 31443 | 89536 | 
| 102 | 16 sphinx/util/cfamily.py | 392 | 450| 491 | 31934 | 89536 | 
| 103 | 17 sphinx/ext/doctest.py | 320 | 335| 130 | 32064 | 94624 | 
| 104 | 18 sphinx/ext/viewcode.py | 47 | 83| 313 | 32377 | 96862 | 
| 105 | 19 sphinx/util/docutils.py | 228 | 238| 163 | 32540 | 100985 | 
| 106 | 19 sphinx/ext/doctest.py | 408 | 484| 752 | 33292 | 100985 | 
| 107 | 19 sphinx/ext/autosummary/generate.py | 193 | 222| 176 | 33468 | 100985 | 
| 108 | 20 sphinx/util/inspect.py | 891 | 918| 228 | 33696 | 108011 | 
| 109 | 20 sphinx/ext/viewcode.py | 85 | 117| 340 | 34036 | 108011 | 
| 110 | 20 sphinx/ext/autosummary/generate.py | 343 | 448| 861 | 34897 | 108011 | 
| 111 | 21 sphinx/domains/javascript.py | 11 | 32| 187 | 35084 | 112058 | 
| 112 | 22 sphinx/domains/c.py | 3412 | 3836| 3706 | 38790 | 143253 | 
| 113 | 22 sphinx/ext/inheritance_diagram.py | 182 | 219| 342 | 39132 | 143253 | 
| 114 | 23 sphinx/domains/std.py | 725 | 762| 366 | 39498 | 153757 | 
| 115 | 23 sphinx/ext/napoleon/docstring.py | 699 | 719| 249 | 39747 | 153757 | 
| 116 | 24 sphinx/ext/autodoc/typehints.py | 82 | 138| 460 | 40207 | 154810 | 
| 117 | 25 sphinx/registry.py | 54 | 124| 784 | 40991 | 159451 | 
| 118 | 25 sphinx/ext/autodoc/typehints.py | 40 | 79| 324 | 41315 | 159451 | 
| 119 | 25 sphinx/ext/napoleon/docstring.py | 502 | 517| 130 | 41445 | 159451 | 
| 120 | 25 sphinx/domains/python.py | 11 | 78| 526 | 41971 | 159451 | 
| 121 | 25 sphinx/util/cfamily.py | 126 | 156| 209 | 42180 | 159451 | 
| 122 | 25 sphinx/util/docutils.py | 342 | 358| 178 | 42358 | 159451 | 
| 123 | 26 sphinx/builders/__init__.py | 536 | 544| 120 | 42478 | 164842 | 
| 124 | 26 sphinx/ext/napoleon/docstring.py | 13 | 59| 515 | 42993 | 164842 | 
| 125 | 27 sphinx/util/smartypants.py | 375 | 387| 137 | 43130 | 168953 | 
| 126 | 27 sphinx/domains/std.py | 897 | 905| 120 | 43250 | 168953 | 
| 127 | 27 sphinx/domains/std.py | 907 | 922| 192 | 43442 | 168953 | 
| 128 | 28 sphinx/builders/xml.py | 75 | 99| 249 | 43691 | 169816 | 
| 129 | 28 sphinx/ext/napoleon/docstring.py | 541 | 554| 164 | 43855 | 169816 | 
| 130 | **28 sphinx/ext/autodoc/__init__.py** | 519 | 539| 235 | 44090 | 169816 | 
| 131 | **28 sphinx/ext/autodoc/__init__.py** | 1760 | 1782| 201 | 44291 | 169816 | 
| 132 | 29 sphinx/directives/__init__.py | 267 | 321| 517 | 44808 | 172551 | 
| 133 | 30 sphinx/ext/autosectionlabel.py | 34 | 69| 339 | 45147 | 173070 | 
| 134 | 30 sphinx/domains/python.py | 266 | 284| 214 | 45361 | 173070 | 
| 135 | 30 sphinx/domains/std.py | 1087 | 1111| 280 | 45641 | 173070 | 
| 136 | 30 sphinx/domains/python.py | 1009 | 1027| 143 | 45784 | 173070 | 
| 137 | **30 sphinx/ext/autodoc/__init__.py** | 155 | 181| 236 | 46020 | 173070 | 
| 138 | 30 sphinx/ext/napoleon/docstring.py | 649 | 660| 124 | 46144 | 173070 | 


### Hint

```
_From [mitar](https://bitbucket.org/mitar) on 2012-01-07 18:21:47+00:00_

Also {{{find_attr_doc}}} seems to not find inherited attributes?

_From [mitar](https://bitbucket.org/mitar) on 2012-01-07 20:04:22+00:00_

The problem is also that parser for attributes' doc strings parses only one module. It should also parses modules of all parent classes and combine everything.

_From Jon Waltman on 2012-11-30 15:14:18+00:00_

Issue #1048 was marked as a duplicate of this issue.

I'm currently getting bit by this issue in 1.2.3.  https://github.com/sphinx-doc/sphinx/issues/2233 is preventing me from working with `1.3.x`.  Is there a workaround you might recommend?  

Is there any hope of getting this fixed, or a workaround? As mentioned in  #1048 even using autoattribute does not work. 

I'm also running into this.  For now I'm manually duplicating docstrings, but it would be nice if `:inherited-members:` worked.

I'm not familiar with the code base at all, but if anyone's willing to point me in a direction I can try to write a fix.

Any news on this feature / bugfix ?
I am also awaiting a fix for this, fwiw
I don't understand this problem. Could anyone make an example to me? I'll try to fix it if possible.
@tk0miya Here's a very simple example project: [sphinx-example.tar.gz](https://github.com/sphinx-doc/sphinx/files/2753140/sphinx-example.tar.gz).


\`\`\`python
class Base:
    """The base class."""

    #: A base attribute.
    ham = True

    def eggs(self):
        """A base method."""


class Inherited(Base):
    """The subclass."""

    #: A local attribute.
    foo = 3

    def bar(self):
        """A local method."""
\`\`\`

\`\`\`rst
.. autoclass:: example.Inherited
    :inherited-members:
\`\`\`

The `Base.ham` attribute is not present in the docs for `Inherited`. However, the `Base.eggs` inherited method is displayed.
In my case ham is an instance attribute and I want it to be auto-documented but it is not working. 

\`\`\`
class Base:
    """The base class."""

    def __init__(self):
        #: A base attribute.
        self.ham = True

    def eggs(self):
        """A base method."""
\`\`\`


I am not sure it is even technically possible for Sphinx to auto-document `self.ham`. As I understood Sphinx finds attributes by code inspection, not actually instantiating the class.  And to detect the ham instance attribute it seems to me you need to instantiate the Base class.
It seems latest Sphinx (2.0.1) is able to process inherited attributes. On the other hand, inherited-instance attributes are not supported yet (filed as #6415 now).
So I think this issue has been resolved now.

I'm closing this. Please let me know if you're still in problem.

Thanks,
@tk0miya I just tried the example I posted earlier with Sphinx 2.1.0 and this issue still occurs. https://github.com/sphinx-doc/sphinx/issues/741#issuecomment-453832459

#6415 and @Dmitrii-I's comment is different, but possibly related.
Thank you for comment. my bad. Just reopened. I might give `:undoc-members:` option on testing...

Inside autodoc, the comment based docstring is strongly coupled with its class. So autodoc considers the docstring for `Base.ham` is not related with `Inherited.ham`. As a result, `Inherited.ham` is detected undocumented variable.

I'll try to fix this again.
```

## Patch

```diff
diff --git a/sphinx/ext/autodoc/__init__.py b/sphinx/ext/autodoc/__init__.py
--- a/sphinx/ext/autodoc/__init__.py
+++ b/sphinx/ext/autodoc/__init__.py
@@ -1584,7 +1584,7 @@ def add_directive_header(self, sig: str) -> None:
                 self.add_line('   ' + _('Bases: %s') % ', '.join(bases), sourcename)
 
     def get_object_members(self, want_all: bool) -> Tuple[bool, ObjectMembers]:
-        members = get_class_members(self.object, self.objpath, self.get_attr, self.analyzer)
+        members = get_class_members(self.object, self.objpath, self.get_attr)
         if not want_all:
             if not self.options.members:
                 return False, []  # type: ignore
diff --git a/sphinx/ext/autodoc/importer.py b/sphinx/ext/autodoc/importer.py
--- a/sphinx/ext/autodoc/importer.py
+++ b/sphinx/ext/autodoc/importer.py
@@ -14,7 +14,7 @@
 from typing import Any, Callable, Dict, List, Mapping, NamedTuple, Optional, Tuple
 
 from sphinx.deprecation import RemovedInSphinx40Warning, deprecated_alias
-from sphinx.pycode import ModuleAnalyzer
+from sphinx.pycode import ModuleAnalyzer, PycodeError
 from sphinx.util import logging
 from sphinx.util.inspect import (getannotations, getmro, getslots, isclass, isenumclass,
                                  safe_getattr)
@@ -251,8 +251,8 @@ def __init__(self, cls: Any, name: str, value: Any, docstring: Optional[str] = N
         self.docstring = docstring
 
 
-def get_class_members(subject: Any, objpath: List[str], attrgetter: Callable,
-                      analyzer: ModuleAnalyzer = None) -> Dict[str, ClassAttribute]:
+def get_class_members(subject: Any, objpath: List[str], attrgetter: Callable
+                      ) -> Dict[str, ClassAttribute]:
     """Get members and attributes of target class."""
     from sphinx.ext.autodoc import INSTANCEATTR
 
@@ -297,23 +297,31 @@ def get_class_members(subject: Any, objpath: List[str], attrgetter: Callable,
         except AttributeError:
             continue
 
-    # annotation only member (ex. attr: int)
-    for cls in getmro(subject):
-        try:
-            for name in getannotations(cls):
-                name = unmangle(cls, name)
-                if name and name not in members:
-                    members[name] = ClassAttribute(cls, name, INSTANCEATTR)
-        except AttributeError:
-            pass
-
-    if analyzer:
-        # append instance attributes (cf. self.attr1) if analyzer knows
-        namespace = '.'.join(objpath)
-        for (ns, name), docstring in analyzer.attr_docs.items():
-            if namespace == ns and name not in members:
-                members[name] = ClassAttribute(subject, name, INSTANCEATTR,
-                                               '\n'.join(docstring))
+    try:
+        for cls in getmro(subject):
+            # annotation only member (ex. attr: int)
+            try:
+                for name in getannotations(cls):
+                    name = unmangle(cls, name)
+                    if name and name not in members:
+                        members[name] = ClassAttribute(cls, name, INSTANCEATTR)
+            except AttributeError:
+                pass
+
+            # append instance attributes (cf. self.attr1) if analyzer knows
+            try:
+                modname = safe_getattr(cls, '__module__')
+                qualname = safe_getattr(cls, '__qualname__')
+                analyzer = ModuleAnalyzer.for_module(modname)
+                analyzer.analyze()
+                for (ns, name), docstring in analyzer.attr_docs.items():
+                    if ns == qualname and name not in members:
+                        members[name] = ClassAttribute(cls, name, INSTANCEATTR,
+                                                       '\n'.join(docstring))
+            except (AttributeError, PycodeError):
+                pass
+    except AttributeError:
+        pass
 
     return members
 

```

## Test Patch

```diff
diff --git a/tests/roots/test-ext-autodoc/target/instance_variable.py b/tests/roots/test-ext-autodoc/target/instance_variable.py
new file mode 100644
--- /dev/null
+++ b/tests/roots/test-ext-autodoc/target/instance_variable.py
@@ -0,0 +1,10 @@
+class Foo:
+    def __init__(self):
+        self.attr1 = None  #: docstring foo
+        self.attr2 = None  #: docstring foo
+
+
+class Bar(Foo):
+    def __init__(self):
+        self.attr2 = None  #: docstring bar
+        self.attr3 = None  #: docstring bar
diff --git a/tests/test_ext_autodoc_autoclass.py b/tests/test_ext_autodoc_autoclass.py
--- a/tests/test_ext_autodoc_autoclass.py
+++ b/tests/test_ext_autodoc_autoclass.py
@@ -51,6 +51,61 @@ def test_classes(app):
     ]
 
 
+@pytest.mark.sphinx('html', testroot='ext-autodoc')
+def test_instance_variable(app):
+    options = {'members': True}
+    actual = do_autodoc(app, 'class', 'target.instance_variable.Bar', options)
+    assert list(actual) == [
+        '',
+        '.. py:class:: Bar()',
+        '   :module: target.instance_variable',
+        '',
+        '',
+        '   .. py:attribute:: Bar.attr2',
+        '      :module: target.instance_variable',
+        '',
+        '      docstring bar',
+        '',
+        '',
+        '   .. py:attribute:: Bar.attr3',
+        '      :module: target.instance_variable',
+        '',
+        '      docstring bar',
+        '',
+    ]
+
+
+@pytest.mark.sphinx('html', testroot='ext-autodoc')
+def test_inherited_instance_variable(app):
+    options = {'members': True,
+               'inherited-members': True}
+    actual = do_autodoc(app, 'class', 'target.instance_variable.Bar', options)
+    assert list(actual) == [
+        '',
+        '.. py:class:: Bar()',
+        '   :module: target.instance_variable',
+        '',
+        '',
+        '   .. py:attribute:: Bar.attr1',
+        '      :module: target.instance_variable',
+        '',
+        '      docstring foo',
+        '',
+        '',
+        '   .. py:attribute:: Bar.attr2',
+        '      :module: target.instance_variable',
+        '',
+        '      docstring bar',
+        '',
+        '',
+        '   .. py:attribute:: Bar.attr3',
+        '      :module: target.instance_variable',
+        '',
+        '      docstring bar',
+        '',
+    ]
+
+
 def test_decorators(app):
     actual = do_autodoc(app, 'class', 'target.decorator.Baz')
     assert list(actual) == [

```


## Code snippets

### 1 - sphinx/ext/autodoc/__init__.py:

Start line: 693, End line: 799

```python
class Documenter:

    def filter_members(self, members: ObjectMembers, want_all: bool
                       ) -> List[Tuple[str, Any, bool]]:
        # ... other code
        for obj in members:
            membername, member = obj
            # if isattr is True, the member is documented as an attribute
            if member is INSTANCEATTR:
                isattr = True
            else:
                isattr = False

            doc = getdoc(member, self.get_attr, self.config.autodoc_inherit_docstrings,
                         self.parent, self.object_name)
            if not isinstance(doc, str):
                # Ignore non-string __doc__
                doc = None

            # if the member __doc__ is the same as self's __doc__, it's just
            # inherited and therefore not the member's doc
            cls = self.get_attr(member, '__class__', None)
            if cls:
                cls_doc = self.get_attr(cls, '__doc__', None)
                if cls_doc == doc:
                    doc = None

            if isinstance(obj, ObjectMember) and obj.docstring:
                # hack for ClassDocumenter to inject docstring via ObjectMember
                doc = obj.docstring

            has_doc = bool(doc)

            metadata = extract_metadata(doc)
            if 'private' in metadata:
                # consider a member private if docstring has "private" metadata
                isprivate = True
            elif 'public' in metadata:
                # consider a member public if docstring has "public" metadata
                isprivate = False
            else:
                isprivate = membername.startswith('_')

            keep = False
            if safe_getattr(member, '__sphinx_mock__', None) is not None:
                # mocked module or object
                pass
            elif self.options.exclude_members and membername in self.options.exclude_members:
                # remove members given by exclude-members
                keep = False
            elif want_all and special_member_re.match(membername):
                # special __methods__
                if self.options.special_members and membername in self.options.special_members:
                    if membername == '__doc__':
                        keep = False
                    elif is_filtered_inherited_member(membername):
                        keep = False
                    else:
                        keep = has_doc or self.options.undoc_members
                else:
                    keep = False
            elif (namespace, membername) in attr_docs:
                if want_all and isprivate:
                    if self.options.private_members is None:
                        keep = False
                    else:
                        keep = membername in self.options.private_members
                else:
                    # keep documented attributes
                    keep = True
                isattr = True
            elif want_all and isprivate:
                if has_doc or self.options.undoc_members:
                    if self.options.private_members is None:
                        keep = False
                    elif is_filtered_inherited_member(membername):
                        keep = False
                    else:
                        keep = membername in self.options.private_members
                else:
                    keep = False
            else:
                if self.options.members is ALL and is_filtered_inherited_member(membername):
                    keep = False
                else:
                    # ignore undocumented members if :undoc-members: is not given
                    keep = has_doc or self.options.undoc_members

            if isinstance(obj, ObjectMember) and obj.skipped:
                # forcedly skipped member (ex. a module attribute not defined in __all__)
                keep = False

            # give the user a chance to decide whether this member
            # should be skipped
            if self.env.app:
                # let extensions preprocess docstrings
                try:
                    skip_user = self.env.app.emit_firstresult(
                        'autodoc-skip-member', self.objtype, membername, member,
                        not keep, self.options)
                    if skip_user is not None:
                        keep = not skip_user
                except Exception as exc:
                    logger.warning(__('autodoc: failed to determine %r to be documented, '
                                      'the following exception was raised:\n%s'),
                                   member, exc, type='autodoc')
                    keep = False

            if keep:
                ret.append((membername, member, isattr))

        return ret
```
### 2 - sphinx/ext/autodoc/__init__.py:

Start line: 2312, End line: 2335

```python
class AttributeDocumenter(GenericAliasMixin, NewTypeMixin, SlotsMixin,  # type: ignore
                          TypeVarMixin, UninitializedInstanceAttributeMixin,
                          NonDataDescriptorMixin, DocstringStripSignatureMixin,
                          ClassLevelDocumenter):

    def import_object(self, raiseerror: bool = False) -> bool:
        try:
            ret = super().import_object(raiseerror=True)
            if inspect.isenumattribute(self.object):
                self.object = self.object.value
        except ImportError as exc:
            if self.isinstanceattribute():
                self.object = INSTANCEATTR
                ret = True
            elif raiseerror:
                raise
            else:
                logger.warning(exc.args[0], type='autodoc', subtype='import_object')
                self.env.note_reread()
                ret = False

        if self.parent:
            self.update_annotations(self.parent)

        return ret

    def get_real_modname(self) -> str:
        return self.get_attr(self.parent or self.object, '__module__', None) \
            or self.modname
```
### 3 - sphinx/ext/autodoc/__init__.py:

Start line: 1035, End line: 1063

```python
class ModuleDocumenter(Documenter):

    def get_object_members(self, want_all: bool) -> Tuple[bool, ObjectMembers]:
        if want_all:
            members = get_module_members(self.object)
            if not self.__all__:
                # for implicit module members, check __module__ to avoid
                # documenting imported objects
                return True, members
            else:
                ret = []
                for name, value in members:
                    if name in self.__all__:
                        ret.append(ObjectMember(name, value))
                    else:
                        ret.append(ObjectMember(name, value, skipped=True))

                return False, ret
        else:
            memberlist = self.options.members or []
            ret = []
            for name in memberlist:
                try:
                    value = safe_getattr(self.object, name)
                    ret.append(ObjectMember(name, value))
                except AttributeError:
                    logger.warning(__('missing attribute mentioned in :members: option: '
                                      'module %s, attribute %s') %
                                   (safe_getattr(self.object, '__name__', '???'), name),
                                   type='autodoc')
            return False, ret
```
### 4 - sphinx/ext/autodoc/__init__.py:

Start line: 1900, End line: 1913

```python
class DataDocumenter(GenericAliasMixin, NewTypeMixin, TypeVarMixin,
                     UninitializedGlobalVariableMixin, ModuleLevelDocumenter):

    def document_members(self, all_members: bool = False) -> None:
        pass

    def get_real_modname(self) -> str:
        return self.get_attr(self.parent or self.object, '__module__', None) \
            or self.modname

    def add_content(self, more_content: Optional[StringList], no_docstring: bool = False
                    ) -> None:
        if not more_content:
            more_content = StringList()

        self.update_content(more_content)
        super().add_content(more_content, no_docstring=no_docstring)
```
### 5 - sphinx/ext/autodoc/__init__.py:

Start line: 2361, End line: 2380

```python
class AttributeDocumenter(GenericAliasMixin, NewTypeMixin, SlotsMixin,  # type: ignore
                          TypeVarMixin, UninitializedInstanceAttributeMixin,
                          NonDataDescriptorMixin, DocstringStripSignatureMixin,
                          ClassLevelDocumenter):

    def get_doc(self, encoding: str = None, ignore: int = None) -> List[List[str]]:
        if self.object is INSTANCEATTR:
            return []

        try:
            # Disable `autodoc_inherit_docstring` temporarily to avoid to obtain
            # a docstring from the value which descriptor returns unexpectedly.
            # ref: https://github.com/sphinx-doc/sphinx/issues/7805
            orig = self.config.autodoc_inherit_docstrings
            self.config.autodoc_inherit_docstrings = False  # type: ignore
            return super().get_doc(encoding, ignore)
        finally:
            self.config.autodoc_inherit_docstrings = orig  # type: ignore

    def add_content(self, more_content: Optional[StringList], no_docstring: bool = False
                    ) -> None:
        if more_content is None:
            more_content = StringList()
        self.update_content(more_content)
        super().add_content(more_content, no_docstring)
```
### 6 - sphinx/ext/autodoc/__init__.py:

Start line: 2217, End line: 2234

```python
class UninitializedInstanceAttributeMixin(DataDocumenterMixinBase):

    def should_suppress_value_header(self) -> bool:
        return (self.object is UNINITIALIZED_ATTR or
                super().should_suppress_value_header())

    def get_doc(self, encoding: str = None, ignore: int = None) -> List[List[str]]:
        if self.object is UNINITIALIZED_ATTR:
            comment = self.get_attribute_comment(self.parent)
            if comment:
                return [comment]

        return super().get_doc(encoding, ignore)  # type: ignore

    def add_content(self, more_content: Optional[StringList], no_docstring: bool = False
                    ) -> None:
        if self.object is UNINITIALIZED_ATTR:
            self.analyzer = None

        super().add_content(more_content, no_docstring=no_docstring)  # type: ignore
```
### 7 - sphinx/ext/autodoc/__init__.py:

Start line: 1386, End line: 1681

```python
class ClassDocumenter(DocstringSignatureMixin, ModuleLevelDocumenter):  # type: ignore
    """
    Specialized Documenter subclass for classes.
    """
    objtype = 'class'
    member_order = 20
    option_spec = {
        'members': members_option, 'undoc-members': bool_option,
        'noindex': bool_option, 'inherited-members': inherited_members_option,
        'show-inheritance': bool_option, 'member-order': member_order_option,
        'exclude-members': exclude_members_option,
        'private-members': members_option, 'special-members': members_option,
    }  # type: Dict[str, Callable]

    _signature_class = None  # type: Any
    _signature_method_name = None  # type: str

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        merge_members_option(self.options)

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any
                            ) -> bool:
        return isinstance(member, type)

    def import_object(self, raiseerror: bool = False) -> bool:
        ret = super().import_object(raiseerror)
        # if the class is documented under another name, document it
        # as data/attribute
        if ret:
            if hasattr(self.object, '__name__'):
                self.doc_as_attr = (self.objpath[-1] != self.object.__name__)
            else:
                self.doc_as_attr = True
        return ret

    def _get_signature(self) -> Tuple[Optional[Any], Optional[str], Optional[Signature]]:
        def get_user_defined_function_or_method(obj: Any, attr: str) -> Any:
            """ Get the `attr` function or method from `obj`, if it is user-defined. """
            if inspect.is_builtin_class_method(obj, attr):
                return None
            attr = self.get_attr(obj, attr, None)
            if not (inspect.ismethod(attr) or inspect.isfunction(attr)):
                return None
            return attr

        # This sequence is copied from inspect._signature_from_callable.
        # ValueError means that no signature could be found, so we keep going.

        # First, we check the obj has a __signature__ attribute
        if (hasattr(self.object, '__signature__') and
                isinstance(self.object.__signature__, Signature)):
            return None, None, self.object.__signature__

        # Next, let's see if it has an overloaded __call__ defined
        # in its metaclass
        call = get_user_defined_function_or_method(type(self.object), '__call__')

        if call is not None:
            if "{0.__module__}.{0.__qualname__}".format(call) in _METACLASS_CALL_BLACKLIST:
                call = None

        if call is not None:
            self.env.app.emit('autodoc-before-process-signature', call, True)
            try:
                sig = inspect.signature(call, bound_method=True,
                                        type_aliases=self.config.autodoc_type_aliases)
                return type(self.object), '__call__', sig
            except ValueError:
                pass

        # Now we check if the 'obj' class has a '__new__' method
        new = get_user_defined_function_or_method(self.object, '__new__')

        if new is not None:
            if "{0.__module__}.{0.__qualname__}".format(new) in _CLASS_NEW_BLACKLIST:
                new = None

        if new is not None:
            self.env.app.emit('autodoc-before-process-signature', new, True)
            try:
                sig = inspect.signature(new, bound_method=True,
                                        type_aliases=self.config.autodoc_type_aliases)
                return self.object, '__new__', sig
            except ValueError:
                pass

        # Finally, we should have at least __init__ implemented
        init = get_user_defined_function_or_method(self.object, '__init__')
        if init is not None:
            self.env.app.emit('autodoc-before-process-signature', init, True)
            try:
                sig = inspect.signature(init, bound_method=True,
                                        type_aliases=self.config.autodoc_type_aliases)
                return self.object, '__init__', sig
            except ValueError:
                pass

        # None of the attributes are user-defined, so fall back to let inspect
        # handle it.
        # We don't know the exact method that inspect.signature will read
        # the signature from, so just pass the object itself to our hook.
        self.env.app.emit('autodoc-before-process-signature', self.object, False)
        try:
            sig = inspect.signature(self.object, bound_method=False,
                                    type_aliases=self.config.autodoc_type_aliases)
            return None, None, sig
        except ValueError:
            pass

        # Still no signature: happens e.g. for old-style classes
        # with __init__ in C and no `__text_signature__`.
        return None, None, None

    def format_args(self, **kwargs: Any) -> str:
        if self.config.autodoc_typehints in ('none', 'description'):
            kwargs.setdefault('show_annotation', False)

        try:
            self._signature_class, self._signature_method_name, sig = self._get_signature()
        except TypeError as exc:
            # __signature__ attribute contained junk
            logger.warning(__("Failed to get a constructor signature for %s: %s"),
                           self.fullname, exc)
            return None

        if sig is None:
            return None

        return stringify_signature(sig, show_return_annotation=False, **kwargs)

    def format_signature(self, **kwargs: Any) -> str:
        if self.doc_as_attr:
            return ''

        sig = super().format_signature()
        sigs = []

        overloads = self.get_overloaded_signatures()
        if overloads and self.config.autodoc_typehints == 'signature':
            # Use signatures for overloaded methods instead of the implementation method.
            method = safe_getattr(self._signature_class, self._signature_method_name, None)
            __globals__ = safe_getattr(method, '__globals__', {})
            for overload in overloads:
                overload = evaluate_signature(overload, __globals__,
                                              self.config.autodoc_type_aliases)

                parameters = list(overload.parameters.values())
                overload = overload.replace(parameters=parameters[1:],
                                            return_annotation=Parameter.empty)
                sig = stringify_signature(overload, **kwargs)
                sigs.append(sig)
        else:
            sigs.append(sig)

        return "\n".join(sigs)

    def get_overloaded_signatures(self) -> List[Signature]:
        if self._signature_class and self._signature_method_name:
            for cls in self._signature_class.__mro__:
                try:
                    analyzer = ModuleAnalyzer.for_module(cls.__module__)
                    analyzer.analyze()
                    qualname = '.'.join([cls.__qualname__, self._signature_method_name])
                    if qualname in analyzer.overloads:
                        return analyzer.overloads.get(qualname)
                    elif qualname in analyzer.tagorder:
                        # the constructor is defined in the class, but not overrided.
                        return []
                except PycodeError:
                    pass

        return []

    def add_directive_header(self, sig: str) -> None:
        sourcename = self.get_sourcename()

        if self.doc_as_attr:
            self.directivetype = 'attribute'
        super().add_directive_header(sig)

        if self.analyzer and '.'.join(self.objpath) in self.analyzer.finals:
            self.add_line('   :final:', sourcename)

        # add inheritance info, if wanted
        if not self.doc_as_attr and self.options.show_inheritance:
            sourcename = self.get_sourcename()
            self.add_line('', sourcename)

            if hasattr(self.object, '__orig_bases__') and len(self.object.__orig_bases__):
                # A subclass of generic types
                # refs: PEP-560 <https://www.python.org/dev/peps/pep-0560/>
                bases = [restify(cls) for cls in self.object.__orig_bases__]
                self.add_line('   ' + _('Bases: %s') % ', '.join(bases), sourcename)
            elif hasattr(self.object, '__bases__') and len(self.object.__bases__):
                # A normal class
                bases = [restify(cls) for cls in self.object.__bases__]
                self.add_line('   ' + _('Bases: %s') % ', '.join(bases), sourcename)

    def get_object_members(self, want_all: bool) -> Tuple[bool, ObjectMembers]:
        members = get_class_members(self.object, self.objpath, self.get_attr, self.analyzer)
        if not want_all:
            if not self.options.members:
                return False, []  # type: ignore
            # specific members given
            selected = []
            for name in self.options.members:  # type: str
                if name in members:
                    selected.append(ObjectMember(name, members[name].value,
                                                 docstring=members[name].docstring))
                else:
                    logger.warning(__('missing attribute %s in object %s') %
                                   (name, self.fullname), type='autodoc')
            return False, selected
        elif self.options.inherited_members:
            return False, [ObjectMember(m.name, m.value, docstring=m.docstring)
                           for m in members.values()]
        else:
            return False, [ObjectMember(m.name, m.value, docstring=m.docstring)
                           for m in members.values() if m.class_ == self.object]

    def get_doc(self, encoding: str = None, ignore: int = None) -> List[List[str]]:
        if encoding is not None:
            warnings.warn("The 'encoding' argument to autodoc.%s.get_doc() is deprecated."
                          % self.__class__.__name__,
                          RemovedInSphinx40Warning, stacklevel=2)
        if self.doc_as_attr:
            # Don't show the docstring of the class when it is an alias.
            return []

        lines = getattr(self, '_new_docstrings', None)
        if lines is not None:
            return lines

        content = self.config.autoclass_content

        docstrings = []
        attrdocstring = self.get_attr(self.object, '__doc__', None)
        if attrdocstring:
            docstrings.append(attrdocstring)

        # for classes, what the "docstring" is can be controlled via a
        # config value; the default is only the class docstring
        if content in ('both', 'init'):
            __init__ = self.get_attr(self.object, '__init__', None)
            initdocstring = getdoc(__init__, self.get_attr,
                                   self.config.autodoc_inherit_docstrings,
                                   self.parent, self.object_name)
            # for new-style classes, no __init__ means default __init__
            if (initdocstring is not None and
                (initdocstring == object.__init__.__doc__ or  # for pypy
                 initdocstring.strip() == object.__init__.__doc__)):  # for !pypy
                initdocstring = None
            if not initdocstring:
                # try __new__
                __new__ = self.get_attr(self.object, '__new__', None)
                initdocstring = getdoc(__new__, self.get_attr,
                                       self.config.autodoc_inherit_docstrings,
                                       self.parent, self.object_name)
                # for new-style classes, no __new__ means default __new__
                if (initdocstring is not None and
                    (initdocstring == object.__new__.__doc__ or  # for pypy
                     initdocstring.strip() == object.__new__.__doc__)):  # for !pypy
                    initdocstring = None
            if initdocstring:
                if content == 'init':
                    docstrings = [initdocstring]
                else:
                    docstrings.append(initdocstring)

        tab_width = self.directive.state.document.settings.tab_width
        return [prepare_docstring(docstring, ignore, tab_width) for docstring in docstrings]

    def add_content(self, more_content: Optional[StringList], no_docstring: bool = False
                    ) -> None:
        if self.doc_as_attr:
            more_content = StringList([_('alias of %s') % restify(self.object)], source='')

        super().add_content(more_content)

    def document_members(self, all_members: bool = False) -> None:
        if self.doc_as_attr:
            return
        super().document_members(all_members)

    def generate(self, more_content: Optional[StringList] = None, real_modname: str = None,
                 check_module: bool = False, all_members: bool = False) -> None:
        # Do not pass real_modname and use the name from the __module__
        # attribute of the class.
        # If a class gets imported into the module real_modname
        # the analyzer won't find the source of the class, if
        # it looks in real_modname.
        return super().generate(more_content=more_content,
                                check_module=check_module,
                                all_members=all_members)
```
### 8 - sphinx/ext/autodoc/__init__.py:

Start line: 573, End line: 585

```python
class Documenter:

    def get_sourcename(self) -> str:
        if (getattr(self.object, '__module__', None) and
                getattr(self.object, '__qualname__', None)):
            # Get the correct location of docstring from self.object
            # to support inherited methods
            fullname = '%s.%s' % (self.object.__module__, self.object.__qualname__)
        else:
            fullname = self.fullname

        if self.analyzer:
            return '%s:docstring of %s' % (self.analyzer.srcname, fullname)
        else:
            return 'docstring of %s' % fullname
```
### 9 - sphinx/ext/autodoc/__init__.py:

Start line: 2237, End line: 2271

```python
class AttributeDocumenter(GenericAliasMixin, NewTypeMixin, SlotsMixin,  # type: ignore
                          TypeVarMixin, UninitializedInstanceAttributeMixin,
                          NonDataDescriptorMixin, DocstringStripSignatureMixin,
                          ClassLevelDocumenter):
    """
    Specialized Documenter subclass for attributes.
    """
    objtype = 'attribute'
    member_order = 60
    option_spec = dict(ModuleLevelDocumenter.option_spec)
    option_spec["annotation"] = annotation_option
    option_spec["no-value"] = bool_option

    # must be higher than the MethodDocumenter, else it will recognize
    # some non-data descriptors as methods
    priority = 10

    @staticmethod
    def is_function_or_method(obj: Any) -> bool:
        return inspect.isfunction(obj) or inspect.isbuiltin(obj) or inspect.ismethod(obj)

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any
                            ) -> bool:
        if inspect.isattributedescriptor(member):
            return True
        elif (not isinstance(parent, ModuleDocumenter) and
              not inspect.isroutine(member) and
              not isinstance(member, type)):
            return True
        else:
            return False

    def document_members(self, all_members: bool = False) -> None:
        pass
```
### 10 - sphinx/ext/autodoc/__init__.py:

Start line: 2273, End line: 2290

```python
class AttributeDocumenter(GenericAliasMixin, NewTypeMixin, SlotsMixin,  # type: ignore
                          TypeVarMixin, UninitializedInstanceAttributeMixin,
                          NonDataDescriptorMixin, DocstringStripSignatureMixin,
                          ClassLevelDocumenter):

    def isinstanceattribute(self) -> bool:
        """Check the subject is an instance attribute."""
        # uninitialized instance variable (PEP-526)
        with mock(self.config.autodoc_mock_imports):
            try:
                ret = import_object(self.modname, self.objpath[:-1], 'class',
                                    attrgetter=self.get_attr,
                                    warningiserror=self.config.autodoc_warningiserror)
                self.parent = ret[3]
                annotations = get_type_hints(self.parent, None,
                                             self.config.autodoc_type_aliases)
                if self.objpath[-1] in annotations:
                    self.object = UNINITIALIZED_ATTR
                    return True
            except ImportError:
                pass

        return False
```
### 12 - sphinx/ext/autodoc/__init__.py:

Start line: 2337, End line: 2359

```python
class AttributeDocumenter(GenericAliasMixin, NewTypeMixin, SlotsMixin,  # type: ignore
                          TypeVarMixin, UninitializedInstanceAttributeMixin,
                          NonDataDescriptorMixin, DocstringStripSignatureMixin,
                          ClassLevelDocumenter):

    def add_directive_header(self, sig: str) -> None:
        super().add_directive_header(sig)
        sourcename = self.get_sourcename()
        if self.options.annotation is SUPPRESS or self.should_suppress_directive_header():
            pass
        elif self.options.annotation:
            self.add_line('   :annotation: %s' % self.options.annotation, sourcename)
        else:
            # obtain type annotation for this attribute
            annotations = get_type_hints(self.parent, None, self.config.autodoc_type_aliases)
            if self.objpath[-1] in annotations:
                objrepr = stringify_typehint(annotations.get(self.objpath[-1]))
                self.add_line('   :type: ' + objrepr, sourcename)

            try:
                if (self.object is INSTANCEATTR or self.options.no_value or
                        self.should_suppress_value_header()):
                    pass
                else:
                    objrepr = object_description(self.object)
                    self.add_line('   :value: ' + objrepr, sourcename)
            except ValueError:
                pass
```
### 13 - sphinx/ext/autodoc/__init__.py:

Start line: 2462, End line: 2500

```python
# NOQA


def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_autodocumenter(ModuleDocumenter)
    app.add_autodocumenter(ClassDocumenter)
    app.add_autodocumenter(ExceptionDocumenter)
    app.add_autodocumenter(DataDocumenter)
    app.add_autodocumenter(NewTypeDataDocumenter)
    app.add_autodocumenter(FunctionDocumenter)
    app.add_autodocumenter(DecoratorDocumenter)
    app.add_autodocumenter(MethodDocumenter)
    app.add_autodocumenter(AttributeDocumenter)
    app.add_autodocumenter(PropertyDocumenter)
    app.add_autodocumenter(NewTypeAttributeDocumenter)

    app.add_config_value('autoclass_content', 'class', True, ENUM('both', 'class', 'init'))
    app.add_config_value('autodoc_member_order', 'alphabetical', True,
                         ENUM('alphabetic', 'alphabetical', 'bysource', 'groupwise'))
    app.add_config_value('autodoc_default_options', {}, True)
    app.add_config_value('autodoc_docstring_signature', True, True)
    app.add_config_value('autodoc_mock_imports', [], True)
    app.add_config_value('autodoc_typehints', "signature", True,
                         ENUM("signature", "description", "none"))
    app.add_config_value('autodoc_type_aliases', {}, True)
    app.add_config_value('autodoc_warningiserror', True, True)
    app.add_config_value('autodoc_inherit_docstrings', True, True)
    app.add_event('autodoc-before-process-signature')
    app.add_event('autodoc-process-docstring')
    app.add_event('autodoc-process-signature')
    app.add_event('autodoc-skip-member')

    app.connect('config-inited', migrate_autodoc_member_order, priority=800)

    app.setup_extension('sphinx.ext.autodoc.type_comment')
    app.setup_extension('sphinx.ext.autodoc.typehints')

    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
```
### 14 - sphinx/ext/autodoc/__init__.py:

Start line: 2134, End line: 2148

```python
class SlotsMixin(DataDocumenterMixinBase):

    def get_doc(self, encoding: str = None, ignore: int = None) -> List[List[str]]:
        if self.object is SLOTSATTR:
            try:
                __slots__ = inspect.getslots(self.parent)
                if __slots__ and __slots__.get(self.objpath[-1]):
                    docstring = prepare_docstring(__slots__[self.objpath[-1]])
                    return [docstring]
                else:
                    return []
            except (AttributeError, ValueError) as exc:
                logger.warning(__('Invalid __slots__ found on %s. Ignored.'),
                               (self.parent.__qualname__, exc), type='autodoc')
                return []
        else:
            return super().get_doc(encoding, ignore)  # type: ignore
```
### 15 - sphinx/ext/autodoc/__init__.py:

Start line: 2432, End line: 2462

```python
def get_documenters(app: Sphinx) -> Dict[str, "Type[Documenter]"]:
    """Returns registered Documenter classes"""
    warnings.warn("get_documenters() is deprecated.", RemovedInSphinx50Warning, stacklevel=2)
    return app.registry.documenters


def autodoc_attrgetter(app: Sphinx, obj: Any, name: str, *defargs: Any) -> Any:
    """Alternative getattr() for types"""
    for typ, func in app.registry.autodoc_attrgettrs.items():
        if isinstance(obj, typ):
            return func(obj, name, *defargs)

    return safe_getattr(obj, name, *defargs)


def migrate_autodoc_member_order(app: Sphinx, config: Config) -> None:
    if config.autodoc_member_order == 'alphabetic':
        # RemovedInSphinx50Warning
        logger.warning(__('autodoc_member_order now accepts "alphabetical" '
                          'instead of "alphabetic". Please update your setting.'))
        config.autodoc_member_order = 'alphabetical'  # type: ignore


# for compatibility
from sphinx.ext.autodoc.deprecated import DataDeclarationDocumenter  # NOQA
from sphinx.ext.autodoc.deprecated import GenericAliasDocumenter  # NOQA
from sphinx.ext.autodoc.deprecated import InstanceAttributeDocumenter  # NOQA
from sphinx.ext.autodoc.deprecated import SingledispatchFunctionDocumenter  # NOQA
from sphinx.ext.autodoc.deprecated import SingledispatchMethodDocumenter  # NOQA
from sphinx.ext.autodoc.deprecated import SlotsAttributeDocumenter  # NOQA
from sphinx.ext.autodoc.deprecated import TypeVarDocumenter
```
### 16 - sphinx/ext/autodoc/__init__.py:

Start line: 2151, End line: 2181

```python
class UninitializedInstanceAttributeMixin(DataDocumenterMixinBase):
    """
    Mixin for AttributeDocumenter to provide the feature for supporting uninitialized
    instance attributes (that are defined in __init__() methods with doc-comments).

    Example:

        class Foo:
            def __init__(self):
                self.attr = None  #: This is a target of this mix-in.
    """

    def get_attribute_comment(self, parent: Any) -> Optional[List[str]]:
        try:
            for cls in inspect.getmro(parent):
                try:
                    module = safe_getattr(cls, '__module__')
                    qualname = safe_getattr(cls, '__qualname__')

                    analyzer = ModuleAnalyzer.for_module(module)
                    analyzer.analyze()
                    if qualname and self.objpath:
                        key = (qualname, self.objpath[-1])
                        if key in analyzer.attr_docs:
                            return list(analyzer.attr_docs[key])
                except (AttributeError, PycodeError):
                    pass
        except (AttributeError, PycodeError):
            pass

        return None
```
### 17 - sphinx/ext/autodoc/importer.py:

Start line: 163, End line: 177

```python
Attribute = NamedTuple('Attribute', [('name', str),
                                     ('directly_defined', bool),
                                     ('value', Any)])


def _getmro(obj: Any) -> Tuple["Type", ...]:
    warnings.warn('sphinx.ext.autodoc.importer._getmro() is deprecated.',
                  RemovedInSphinx40Warning)
    return getmro(obj)


def _getannotations(obj: Any) -> Mapping[str, Any]:
    warnings.warn('sphinx.ext.autodoc.importer._getannotations() is deprecated.',
                  RemovedInSphinx40Warning)
    return getannotations(obj)
```
### 18 - sphinx/ext/autodoc/__init__.py:

Start line: 2183, End line: 2215

```python
class UninitializedInstanceAttributeMixin(DataDocumenterMixinBase):

    def is_uninitialized_instance_attribute(self, parent: Any) -> bool:
        """Check the subject is an attribute defined in __init__()."""
        # An instance variable defined in __init__().
        if self.get_attribute_comment(parent):
            return True
        else:
            return False

    def import_object(self, raiseerror: bool = False) -> bool:
        """Check the exisitence of uninitizlied instance attribute when failed to import
        the attribute.
        """
        try:
            return super().import_object(raiseerror=True)  # type: ignore
        except ImportError as exc:
            try:
                ret = import_object(self.modname, self.objpath[:-1], 'class',
                                    attrgetter=self.get_attr,  # type: ignore
                                    warningiserror=self.config.autodoc_warningiserror)
                parent = ret[3]
                if self.is_uninitialized_instance_attribute(parent):
                    self.object = UNINITIALIZED_ATTR
                    self.parent = parent
                    return True
            except ImportError:
                pass

            if raiseerror:
                raise
            else:
                logger.warning(exc.args[0], type='autodoc', subtype='import_object')
                self.env.note_reread()
                return False
```
### 20 - sphinx/ext/autodoc/__init__.py:

Start line: 289, End line: 363

```python
class Documenter:
    """
    A Documenter knows how to autodocument a single object type.  When
    registered with the AutoDirective, it will be used to document objects
    of that type when needed by autodoc.

    Its *objtype* attribute selects what auto directive it is assigned to
    (the directive name is 'auto' + objtype), and what directive it generates
    by default, though that can be overridden by an attribute called
    *directivetype*.

    A Documenter has an *option_spec* that works like a docutils directive's;
    in fact, it will be used to parse an auto directive's options that matches
    the documenter.
    """
    #: name by which the directive is called (auto...) and the default
    #: generated directive name
    objtype = 'object'
    #: indentation by which to indent the directive content
    content_indent = '   '
    #: priority if multiple documenters return True from can_document_member
    priority = 0
    #: order if autodoc_member_order is set to 'groupwise'
    member_order = 0
    #: true if the generated content may contain titles
    titles_allowed = False

    option_spec = {'noindex': bool_option}  # type: Dict[str, Callable]

    def get_attr(self, obj: Any, name: str, *defargs: Any) -> Any:
        """getattr() override for types such as Zope interfaces."""
        return autodoc_attrgetter(self.env.app, obj, name, *defargs)

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any
                            ) -> bool:
        """Called to see if a member can be documented by this documenter."""
        raise NotImplementedError('must be implemented in subclasses')

    def __init__(self, directive: "DocumenterBridge", name: str, indent: str = '') -> None:
        self.directive = directive
        self.config = directive.env.config
        self.env = directive.env    # type: BuildEnvironment
        self.options = directive.genopt
        self.name = name
        self.indent = indent
        # the module and object path within the module, and the fully
        # qualified name (all set after resolve_name succeeds)
        self.modname = None         # type: str
        self.module = None          # type: ModuleType
        self.objpath = None         # type: List[str]
        self.fullname = None        # type: str
        # extra signature items (arguments and return annotation,
        # also set after resolve_name succeeds)
        self.args = None            # type: str
        self.retann = None          # type: str
        # the object to document (set after import_object succeeds)
        self.object = None          # type: Any
        self.object_name = None     # type: str
        # the parent/owner of the object to document
        self.parent = None          # type: Any
        # the module analyzer to get at attribute docs, or None
        self.analyzer = None        # type: ModuleAnalyzer

    @property
    def documenters(self) -> Dict[str, "Type[Documenter]"]:
        """Returns registered Documenter classes"""
        return self.env.app.registry.documenters

    def add_line(self, line: str, source: str, *lineno: int) -> None:
        """Append one line of generated reST to the output."""
        if line.strip():  # not a blank line
            self.directive.result.append(self.indent + line, source, *lineno)
        else:
            self.directive.result.append('', source, *lineno)
```
### 21 - sphinx/ext/autodoc/__init__.py:

Start line: 1004, End line: 1020

```python
class ModuleDocumenter(Documenter):

    def import_object(self, raiseerror: bool = False) -> bool:
        ret = super().import_object(raiseerror)

        try:
            if not self.options.ignore_module_all:
                self.__all__ = inspect.getall(self.object)
        except AttributeError as exc:
            # __all__ raises an error.
            logger.warning(__('%s.__all__ raises an error. Ignored: %r'),
                           (self.fullname, exc), type='autodoc')
        except ValueError as exc:
            # invalid __all__ found.
            logger.warning(__('__all__ should be a list of strings, not %r '
                              '(in module %s) -- ignoring __all__') %
                           (exc.args[0], self.fullname), type='autodoc')

        return ret
```
### 24 - sphinx/ext/autodoc/__init__.py:

Start line: 1065, End line: 1082

```python
class ModuleDocumenter(Documenter):

    def sort_members(self, documenters: List[Tuple["Documenter", bool]],
                     order: str) -> List[Tuple["Documenter", bool]]:
        if order == 'bysource' and self.__all__:
            # Sort alphabetically first (for members not listed on the __all__)
            documenters.sort(key=lambda e: e[0].name)

            # Sort by __all__
            def keyfunc(entry: Tuple[Documenter, bool]) -> int:
                name = entry[0].name.split('::')[1]
                if name in self.__all__:
                    return self.__all__.index(name)
                else:
                    return len(self.__all__)
            documenters.sort(key=keyfunc)

            return documenters
        else:
            return super().sort_members(documenters, order)
```
### 25 - sphinx/ext/autodoc/__init__.py:

Start line: 2082, End line: 2101

```python
class NonDataDescriptorMixin(DataDocumenterMixinBase):
    """
    Mixin for AttributeDocumenter to provide the feature for supporting non
    data-descriptors.

    .. note:: This mix-in must be inherited after other mix-ins.  Otherwise, docstring
              and :value: header will be suppressed unexpectedly.
    """

    def should_suppress_value_header(self) -> bool:
        return (inspect.isattributedescriptor(self.object) or
                super().should_suppress_directive_header())

    def get_doc(self, encoding: str = None, ignore: int = None) -> List[List[str]]:
        if not inspect.isattributedescriptor(self.object):
            # the docstring of non datadescriptor is very probably the wrong thing
            # to display
            return []
        else:
            return super().get_doc(encoding, ignore)  # type: ignore
```
### 26 - sphinx/ext/autodoc/__init__.py:

Start line: 1876, End line: 1898

```python
class DataDocumenter(GenericAliasMixin, NewTypeMixin, TypeVarMixin,
                     UninitializedGlobalVariableMixin, ModuleLevelDocumenter):

    def add_directive_header(self, sig: str) -> None:
        super().add_directive_header(sig)
        sourcename = self.get_sourcename()
        if self.options.annotation is SUPPRESS or self.should_suppress_directive_header():
            pass
        elif self.options.annotation:
            self.add_line('   :annotation: %s' % self.options.annotation,
                          sourcename)
        else:
            # obtain annotation for this data
            annotations = get_type_hints(self.parent, None, self.config.autodoc_type_aliases)
            if self.objpath[-1] in annotations:
                objrepr = stringify_typehint(annotations.get(self.objpath[-1]))
                self.add_line('   :type: ' + objrepr, sourcename)

            try:
                if self.options.no_value or self.should_suppress_value_header():
                    pass
                else:
                    objrepr = object_description(self.object)
                    self.add_line('   :value: ' + objrepr, sourcename)
            except ValueError:
                pass
```
### 27 - sphinx/ext/autodoc/__init__.py:

Start line: 13, End line: 116

```python
import importlib
import re
import warnings
from inspect import Parameter, Signature
from types import ModuleType
from typing import (Any, Callable, Dict, Iterator, List, Optional, Sequence, Set, Tuple, Type,
                    TypeVar, Union)

from docutils.statemachine import StringList

import sphinx
from sphinx.application import Sphinx
from sphinx.config import ENUM, Config
from sphinx.deprecation import (RemovedInSphinx40Warning, RemovedInSphinx50Warning,
                                RemovedInSphinx60Warning)
from sphinx.environment import BuildEnvironment
from sphinx.ext.autodoc.importer import (get_class_members, get_module_members,
                                         get_object_members, import_object)
from sphinx.ext.autodoc.mock import mock
from sphinx.locale import _, __
from sphinx.pycode import ModuleAnalyzer, PycodeError
from sphinx.util import inspect, logging
from sphinx.util.docstrings import extract_metadata, prepare_docstring
from sphinx.util.inspect import (evaluate_signature, getdoc, object_description, safe_getattr,
                                 stringify_signature)
from sphinx.util.typing import get_type_hints, restify
from sphinx.util.typing import stringify as stringify_typehint

if False:
    # For type annotation
    from typing import Type  # NOQA # for python3.5.1

    from sphinx.ext.autodoc.directive import DocumenterBridge


logger = logging.getLogger(__name__)


# This type isn't exposed directly in any modules, but can be found
# here in most Python versions
MethodDescriptorType = type(type.__subclasses__)


#: extended signature RE: with explicit module name separated by ::
py_ext_sig_re = re.compile(
    r'''^ ([\w.]+::)?            # explicit module name
          ([\w.]+\.)?            # module and/or class name(s)
          (\w+)  \s*             # thing name
          (?: \((.*)\)           # optional: arguments
           (?:\s* -> \s* (.*))?  #           return annotation
          )? $                   # and nothing more
          ''', re.VERBOSE)
special_member_re = re.compile(r'^__\S+__$')


def identity(x: Any) -> Any:
    return x


class _All:
    """A special value for :*-members: that matches to any member."""

    def __contains__(self, item: Any) -> bool:
        return True


class _Empty:
    """A special value for :exclude-members: that never matches to any member."""

    def __contains__(self, item: Any) -> bool:
        return False


ALL = _All()
EMPTY = _Empty()
UNINITIALIZED_ATTR = object()
INSTANCEATTR = object()
SLOTSATTR = object()


def members_option(arg: Any) -> Union[object, List[str]]:
    """Used to convert the :members: option to auto directives."""
    if arg is None or arg is True:
        return ALL
    elif arg is False:
        return None
    else:
        return [x.strip() for x in arg.split(',') if x.strip()]


def members_set_option(arg: Any) -> Union[object, Set[str]]:
    """Used to convert the :members: option to auto directives."""
    warnings.warn("members_set_option() is deprecated.",
                  RemovedInSphinx50Warning, stacklevel=2)
    if arg is None:
        return ALL
    return {x.strip() for x in arg.split(',') if x.strip()}


def exclude_members_option(arg: Any) -> Union[object, Set[str]]:
    """Used to convert the :exclude-members: option."""
    if arg is None:
        return EMPTY
    return {x.strip() for x in arg.split(',') if x.strip()}
```
### 28 - sphinx/ext/autodoc/__init__.py:

Start line: 1106, End line: 1136

```python
class ClassLevelDocumenter(Documenter):
    """
    Specialized Documenter subclass for objects on class level (methods,
    attributes).
    """
    def resolve_name(self, modname: str, parents: Any, path: str, base: Any
                     ) -> Tuple[str, List[str]]:
        if modname is None:
            if path:
                mod_cls = path.rstrip('.')
            else:
                mod_cls = None
                # if documenting a class-level object without path,
                # there must be a current class, either from a parent
                # auto directive ...
                mod_cls = self.env.temp_data.get('autodoc:class')
                # ... or from a class directive
                if mod_cls is None:
                    mod_cls = self.env.ref_context.get('py:class')
                # ... if still None, there's no way to know
                if mod_cls is None:
                    return None, []
            modname, sep, cls = mod_cls.rpartition('.')
            parents = [cls]
            # if the module name is still missing, get it like above
            if not modname:
                modname = self.env.temp_data.get('autodoc:module')
            if not modname:
                modname = self.env.ref_context.get('py:module')
            # ... else, it stays None, which means invalid
        return modname, parents + [base]
```
### 29 - sphinx/ext/autodoc/importer.py:

Start line: 74, End line: 137

```python
def import_object(modname: str, objpath: List[str], objtype: str = '',
                  attrgetter: Callable[[Any, str], Any] = safe_getattr,
                  warningiserror: bool = False) -> Any:
    if objpath:
        logger.debug('[autodoc] from %s import %s', modname, '.'.join(objpath))
    else:
        logger.debug('[autodoc] import %s', modname)

    try:
        module = None
        exc_on_importing = None
        objpath = list(objpath)
        while module is None:
            try:
                module = import_module(modname, warningiserror=warningiserror)
                logger.debug('[autodoc] import %s => %r', modname, module)
            except ImportError as exc:
                logger.debug('[autodoc] import %s => failed', modname)
                exc_on_importing = exc
                if '.' in modname:
                    # retry with parent module
                    modname, name = modname.rsplit('.', 1)
                    objpath.insert(0, name)
                else:
                    raise

        obj = module
        parent = None
        object_name = None
        for attrname in objpath:
            parent = obj
            logger.debug('[autodoc] getattr(_, %r)', attrname)
            mangled_name = mangle(obj, attrname)
            obj = attrgetter(obj, mangled_name)
            logger.debug('[autodoc] => %r', obj)
            object_name = attrname
        return [module, parent, object_name, obj]
    except (AttributeError, ImportError) as exc:
        if isinstance(exc, AttributeError) and exc_on_importing:
            # restore ImportError
            exc = exc_on_importing

        if objpath:
            errmsg = ('autodoc: failed to import %s %r from module %r' %
                      (objtype, '.'.join(objpath), modname))
        else:
            errmsg = 'autodoc: failed to import %s %r' % (objtype, modname)

        if isinstance(exc, ImportError):
            # import_module() raises ImportError having real exception obj and
            # traceback
            real_exc, traceback_msg = exc.args
            if isinstance(real_exc, SystemExit):
                errmsg += ('; the module executes module level statement '
                           'and it might call sys.exit().')
            elif isinstance(real_exc, ImportError) and real_exc.args:
                errmsg += '; the following exception was raised:\n%s' % real_exc.args[0]
            else:
                errmsg += '; the following exception was raised:\n%s' % traceback_msg
        else:
            errmsg += '; the following exception was raised:\n%s' % traceback.format_exc()

        logger.debug(errmsg)
        raise ImportError(errmsg) from exc
```
### 31 - sphinx/ext/autodoc/__init__.py:

Start line: 119, End line: 152

```python
def inherited_members_option(arg: Any) -> Union[object, Set[str]]:
    """Used to convert the :members: option to auto directives."""
    if arg is None:
        return 'object'
    else:
        return arg


def member_order_option(arg: Any) -> Optional[str]:
    """Used to convert the :members: option to auto directives."""
    if arg is None:
        return None
    elif arg in ('alphabetical', 'bysource', 'groupwise'):
        return arg
    else:
        raise ValueError(__('invalid value for member-order option: %s') % arg)


SUPPRESS = object()


def annotation_option(arg: Any) -> Any:
    if arg is None:
        # suppress showing the representation of the object
        return SUPPRESS
    else:
        return arg


def bool_option(arg: Any) -> bool:
    """Used to convert flag options to auto directives.  (Instead of
    directives.flag(), which returns None).
    """
    return True
```
### 32 - sphinx/ext/autodoc/__init__.py:

Start line: 1085, End line: 1103

```python
class ModuleLevelDocumenter(Documenter):
    """
    Specialized Documenter subclass for objects on module level (functions,
    classes, data/constants).
    """
    def resolve_name(self, modname: str, parents: Any, path: str, base: Any
                     ) -> Tuple[str, List[str]]:
        if modname is None:
            if path:
                modname = path.rstrip('.')
            else:
                # if documenting a toplevel object without explicit module,
                # it can be contained in another auto directive ...
                modname = self.env.temp_data.get('autodoc:module')
                # ... or in the scope of a module directive
                if not modname:
                    modname = self.env.ref_context.get('py:module')
                # ... else, it stays None, which means invalid
        return modname, parents + [base]
```
### 33 - sphinx/ext/autodoc/importer.py:

Start line: 321, End line: 340

```python
from sphinx.ext.autodoc.mock import (MockFinder, MockLoader, _MockModule, _MockObject,  # NOQA
                                     mock)

deprecated_alias('sphinx.ext.autodoc.importer',
                 {
                     '_MockModule': _MockModule,
                     '_MockObject': _MockObject,
                     'MockFinder': MockFinder,
                     'MockLoader': MockLoader,
                     'mock': mock,
                 },
                 RemovedInSphinx40Warning,
                 {
                     '_MockModule': 'sphinx.ext.autodoc.mock._MockModule',
                     '_MockObject': 'sphinx.ext.autodoc.mock._MockObject',
                     'MockFinder': 'sphinx.ext.autodoc.mock.MockFinder',
                     'MockLoader': 'sphinx.ext.autodoc.mock.MockLoader',
                     'mock': 'sphinx.ext.autodoc.mock.mock',
                 })
```
### 34 - sphinx/ext/autodoc/__init__.py:

Start line: 1022, End line: 1033

```python
class ModuleDocumenter(Documenter):

    def add_directive_header(self, sig: str) -> None:
        Documenter.add_directive_header(self, sig)

        sourcename = self.get_sourcename()

        # add some module-specific options
        if self.options.synopsis:
            self.add_line('   :synopsis: ' + self.options.synopsis, sourcename)
        if self.options.platform:
            self.add_line('   :platform: ' + self.options.platform, sourcename)
        if self.options.deprecated:
            self.add_line('   :deprecated:', sourcename)
```
### 35 - sphinx/ext/autodoc/__init__.py:

Start line: 2292, End line: 2310

```python
class AttributeDocumenter(GenericAliasMixin, NewTypeMixin, SlotsMixin,  # type: ignore
                          TypeVarMixin, UninitializedInstanceAttributeMixin,
                          NonDataDescriptorMixin, DocstringStripSignatureMixin,
                          ClassLevelDocumenter):

    def update_annotations(self, parent: Any) -> None:
        """Update __annotations__ to support type_comment and so on."""
        try:
            annotations = inspect.getannotations(parent)

            for cls in inspect.getmro(parent):
                try:
                    module = safe_getattr(cls, '__module__')
                    qualname = safe_getattr(cls, '__qualname__')

                    analyzer = ModuleAnalyzer.for_module(module)
                    analyzer.analyze()
                    for (classname, attrname), annotation in analyzer.annotations.items():
                        if classname == qualname and attrname not in annotations:
                            annotations[attrname] = annotation  # type: ignore
                except (AttributeError, PycodeError):
                    pass
        except AttributeError:
            pass
```
### 36 - sphinx/ext/autodoc/__init__.py:

Start line: 801, End line: 844

```python
class Documenter:

    def document_members(self, all_members: bool = False) -> None:
        """Generate reST for member documentation.

        If *all_members* is True, do all members, else those given by
        *self.options.members*.
        """
        # set current namespace for finding members
        self.env.temp_data['autodoc:module'] = self.modname
        if self.objpath:
            self.env.temp_data['autodoc:class'] = self.objpath[0]

        want_all = all_members or self.options.inherited_members or \
            self.options.members is ALL
        # find out which members are documentable
        members_check_module, members = self.get_object_members(want_all)

        # document non-skipped members
        memberdocumenters = []  # type: List[Tuple[Documenter, bool]]
        for (mname, member, isattr) in self.filter_members(members, want_all):
            classes = [cls for cls in self.documenters.values()
                       if cls.can_document_member(member, mname, isattr, self)]
            if not classes:
                # don't know how to document this member
                continue
            # prefer the documenter with the highest priority
            classes.sort(key=lambda cls: cls.priority)
            # give explicitly separated module name, so that members
            # of inner classes can be documented
            full_mname = self.modname + '::' + \
                '.'.join(self.objpath + [mname])
            documenter = classes[-1](self.directive, full_mname, self.indent)
            memberdocumenters.append((documenter, isattr))

        member_order = self.options.member_order or self.config.autodoc_member_order
        memberdocumenters = self.sort_members(memberdocumenters, member_order)

        for documenter, isattr in memberdocumenters:
            documenter.generate(
                all_members=True, real_modname=self.real_modname,
                check_module=members_check_module and not isattr)

        # reset current objects
        self.env.temp_data['autodoc:module'] = None
        self.env.temp_data['autodoc:class'] = None
```
### 37 - sphinx/ext/autodoc/__init__.py:

Start line: 1839, End line: 1874

```python
class DataDocumenter(GenericAliasMixin, NewTypeMixin, TypeVarMixin,
                     UninitializedGlobalVariableMixin, ModuleLevelDocumenter):
    """
    Specialized Documenter subclass for data items.
    """
    objtype = 'data'
    member_order = 40
    priority = -10
    option_spec = dict(ModuleLevelDocumenter.option_spec)
    option_spec["annotation"] = annotation_option
    option_spec["no-value"] = bool_option

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any
                            ) -> bool:
        return isinstance(parent, ModuleDocumenter) and isattr

    def update_annotations(self, parent: Any) -> None:
        """Update __annotations__ to support type_comment and so on."""
        try:
            annotations = inspect.getannotations(parent)

            analyzer = ModuleAnalyzer.for_module(self.modname)
            analyzer.analyze()
            for (classname, attrname), annotation in analyzer.annotations.items():
                if classname == '' and attrname not in annotations:
                    annotations[attrname] = annotation  # type: ignore
        except AttributeError:
            pass

    def import_object(self, raiseerror: bool = False) -> bool:
        ret = super().import_object(raiseerror)
        if self.parent:
            self.update_annotations(self.parent)

        return ret
```
### 38 - sphinx/ext/autodoc/__init__.py:

Start line: 2104, End line: 2132

```python
class SlotsMixin(DataDocumenterMixinBase):
    """
    Mixin for AttributeDocumenter to provide the feature for supporting __slots__.
    """

    def isslotsattribute(self) -> bool:
        """Check the subject is an attribute in __slots__."""
        try:
            __slots__ = inspect.getslots(self.parent)
            if __slots__ and self.objpath[-1] in __slots__:
                return True
            else:
                return False
        except (AttributeError, ValueError):
            return False

    def import_object(self, raiseerror: bool = False) -> bool:
        ret = super().import_object(raiseerror)  # type: ignore
        if self.isslotsattribute():
            self.object = SLOTSATTR

        return ret

    def should_suppress_directive_header(self) -> bool:
        if self.object is SLOTSATTR:
            self._datadescriptor = True
            return True
        else:
            return super().should_suppress_directive_header()
```
### 39 - sphinx/ext/autodoc/__init__.py:

Start line: 1211, End line: 1231

```python
class DocstringSignatureMixin:

    def get_doc(self, encoding: str = None, ignore: int = None) -> List[List[str]]:
        if encoding is not None:
            warnings.warn("The 'encoding' argument to autodoc.%s.get_doc() is deprecated."
                          % self.__class__.__name__,
                          RemovedInSphinx40Warning, stacklevel=2)
        if self._new_docstrings is not None:
            return self._new_docstrings
        return super().get_doc(None, ignore)  # type: ignore

    def format_signature(self, **kwargs: Any) -> str:
        if self.args is None and self.config.autodoc_docstring_signature:  # type: ignore
            # only act if a signature is not explicitly given already, and if
            # the feature is enabled
            result = self._find_signature()
            if result is not None:
                self.args, self.retann = result
        sig = super().format_signature(**kwargs)  # type: ignore
        if self._signatures:
            return "\n".join([sig] + self._signatures)
        else:
            return sig
```
### 40 - sphinx/ext/autodoc/__init__.py:

Start line: 1800, End line: 1836

```python
class UninitializedGlobalVariableMixin(DataDocumenterMixinBase):
    """
    Mixin for DataDocumenter to provide the feature for supporting uninitialized
    (type annotation only) global variables.
    """

    def import_object(self, raiseerror: bool = False) -> bool:
        try:
            return super().import_object(raiseerror=True)  # type: ignore
        except ImportError as exc:
            # annotation only instance variable (PEP-526)
            try:
                self.parent = importlib.import_module(self.modname)
                annotations = get_type_hints(self.parent, None,
                                             self.config.autodoc_type_aliases)
                if self.objpath[-1] in annotations:
                    self.object = UNINITIALIZED_ATTR
                    return True
            except ImportError:
                pass

            if raiseerror:
                raise
            else:
                logger.warning(exc.args[0], type='autodoc', subtype='import_object')
                self.env.note_reread()
                return False

    def should_suppress_value_header(self) -> bool:
        return (self.object == UNINITIALIZED_ATTR or
                super().should_suppress_value_header())

    def get_doc(self, encoding: str = None, ignore: int = None) -> List[List[str]]:
        if self.object is UNINITIALIZED_ATTR:
            return []
        else:
            return super().get_doc(encoding, ignore)  # type: ignore
```
### 41 - sphinx/ext/autodoc/__init__.py:

Start line: 2414, End line: 2429

```python
class NewTypeAttributeDocumenter(AttributeDocumenter):
    """
    Specialized Documenter subclass for NewTypes.

    Note: This must be invoked before MethodDocumenter because NewType is a kind of
    function object.
    """

    objtype = 'newvarattribute'
    directivetype = 'attribute'
    priority = MethodDocumenter.priority + 1

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any
                            ) -> bool:
        return not isinstance(parent, ModuleDocumenter) and inspect.isNewType(member)
```
### 42 - sphinx/ext/autodoc/importer.py:

Start line: 254, End line: 318

```python
def get_class_members(subject: Any, objpath: List[str], attrgetter: Callable,
                      analyzer: ModuleAnalyzer = None) -> Dict[str, ClassAttribute]:
    """Get members and attributes of target class."""
    from sphinx.ext.autodoc import INSTANCEATTR

    # the members directly defined in the class
    obj_dict = attrgetter(subject, '__dict__', {})

    members = {}  # type: Dict[str, ClassAttribute]

    # enum members
    if isenumclass(subject):
        for name, value in subject.__members__.items():
            if name not in members:
                members[name] = ClassAttribute(subject, name, value)

        superclass = subject.__mro__[1]
        for name in obj_dict:
            if name not in superclass.__dict__:
                value = safe_getattr(subject, name)
                members[name] = ClassAttribute(subject, name, value)

    # members in __slots__
    try:
        __slots__ = getslots(subject)
        if __slots__:
            from sphinx.ext.autodoc import SLOTSATTR

            for name, docstring in __slots__.items():
                members[name] = ClassAttribute(subject, name, SLOTSATTR, docstring)
    except (AttributeError, TypeError, ValueError):
        pass

    # other members
    for name in dir(subject):
        try:
            value = attrgetter(subject, name)
            unmangled = unmangle(subject, name)
            if unmangled and unmangled not in members:
                if name in obj_dict:
                    members[unmangled] = ClassAttribute(subject, unmangled, value)
                else:
                    members[unmangled] = ClassAttribute(None, unmangled, value)
        except AttributeError:
            continue

    # annotation only member (ex. attr: int)
    for cls in getmro(subject):
        try:
            for name in getannotations(cls):
                name = unmangle(cls, name)
                if name and name not in members:
                    members[name] = ClassAttribute(cls, name, INSTANCEATTR)
        except AttributeError:
            pass

    if analyzer:
        # append instance attributes (cf. self.attr1) if analyzer knows
        namespace = '.'.join(objpath)
        for (ns, name), docstring in analyzer.attr_docs.items():
            if namespace == ns and name not in members:
                members[name] = ClassAttribute(subject, name, INSTANCEATTR,
                                               '\n'.join(docstring))

    return members
```
### 44 - sphinx/ext/autodoc/__init__.py:

Start line: 1684, End line: 1719

```python
class ExceptionDocumenter(ClassDocumenter):
    """
    Specialized ClassDocumenter subclass for exceptions.
    """
    objtype = 'exception'
    member_order = 10

    # needs a higher priority than ClassDocumenter
    priority = 10

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any
                            ) -> bool:
        return isinstance(member, type) and issubclass(member, BaseException)


class DataDocumenterMixinBase:
    # define types of instance variables
    config = None  # type: Config
    env = None  # type: BuildEnvironment
    modname = None  # type: str
    parent = None  # type: Any
    object = None  # type: Any
    objpath = None  # type: List[str]

    def should_suppress_directive_header(self) -> bool:
        """Check directive header should be suppressed."""
        return False

    def should_suppress_value_header(self) -> bool:
        """Check :value: header should be suppressed."""
        return False

    def update_content(self, more_content: StringList) -> None:
        """Update docstring for the NewType object."""
        pass
```
### 46 - sphinx/ext/autodoc/__init__.py:

Start line: 250, End line: 286

```python
# This class is used only in ``sphinx.ext.autodoc.directive``,
# But we define this class here to keep compatibility (see #4538)
class Options(dict):
    """A dict/attribute hybrid that returns None on nonexisting keys."""
    def __getattr__(self, name: str) -> Any:
        try:
            return self[name.replace('_', '-')]
        except KeyError:
            return None


class ObjectMember(tuple):
    """A member of object.

    This is used for the result of `Documenter.get_object_members()` to
    represent each member of the object.

    .. Note::

       An instance of this class behaves as a tuple of (name, object)
       for compatibility to old Sphinx.  The behavior will be dropped
       in the future.  Therefore extensions should not use the tuple
       interface.
    """

    def __new__(cls, name: str, obj: Any, **kwargs: Any) -> Any:
        return super().__new__(cls, (name, obj))  # type: ignore

    def __init__(self, name: str, obj: Any, docstring: Optional[str] = None,
                 skipped: bool = False) -> None:
        self.__name__ = name
        self.object = obj
        self.docstring = docstring
        self.skipped = skipped


ObjectMembers = Union[List[ObjectMember], List[Tuple[str, Any]]]
```
### 48 - sphinx/ext/autodoc/__init__.py:

Start line: 376, End line: 411

```python
class Documenter:

    def parse_name(self) -> bool:
        """Determine what module to import and what attribute to document.

        Returns True and sets *self.modname*, *self.objpath*, *self.fullname*,
        *self.args* and *self.retann* if parsing and resolving was successful.
        """
        # first, parse the definition -- auto directives for classes and
        # functions can contain a signature which is then used instead of
        # an autogenerated one
        try:
            explicit_modname, path, base, args, retann = \
                py_ext_sig_re.match(self.name).groups()
        except AttributeError:
            logger.warning(__('invalid signature for auto%s (%r)') % (self.objtype, self.name),
                           type='autodoc')
            return False

        # support explicit module and class name separation via ::
        if explicit_modname is not None:
            modname = explicit_modname[:-2]
            parents = path.rstrip('.').split('.') if path else []
        else:
            modname = None
            parents = []

        with mock(self.config.autodoc_mock_imports):
            self.modname, self.objpath = self.resolve_name(modname, parents, path, base)

        if not self.modname:
            return False

        self.args = args
        self.retann = retann
        self.fullname = (self.modname or '') + \
                        ('.' + '.'.join(self.objpath) if self.objpath else '')
        return True
```
### 49 - sphinx/ext/autodoc/__init__.py:

Start line: 654, End line: 692

```python
class Documenter:

    def filter_members(self, members: ObjectMembers, want_all: bool
                       ) -> List[Tuple[str, Any, bool]]:
        """Filter the given member list.

        Members are skipped if

        - they are private (except if given explicitly or the private-members
          option is set)
        - they are special methods (except if given explicitly or the
          special-members option is set)
        - they are undocumented (except if the undoc-members option is set)

        The user can override the skipping decision by connecting to the
        ``autodoc-skip-member`` event.
        """
        def is_filtered_inherited_member(name: str) -> bool:
            if inspect.isclass(self.object):
                for cls in self.object.__mro__:
                    if cls.__name__ == self.options.inherited_members and cls != self.object:
                        # given member is a member of specified *super class*
                        return True
                    elif name in cls.__dict__:
                        return False
                    elif name in self.get_attr(cls, '__annotations__', {}):
                        return False

            return False

        ret = []

        # search for members in source code too
        namespace = '.'.join(self.objpath)  # will be empty for modules

        if self.analyzer:
            attr_docs = self.analyzer.find_attr_docs()
        else:
            attr_docs = {}

        # process members and determine which to skip
        # ... other code
```
### 50 - sphinx/ext/autodoc/importer.py:

Start line: 180, End line: 251

```python
def get_object_members(subject: Any, objpath: List[str], attrgetter: Callable,
                       analyzer: ModuleAnalyzer = None) -> Dict[str, Attribute]:
    """Get members and attributes of target object."""
    from sphinx.ext.autodoc import INSTANCEATTR

    # the members directly defined in the class
    obj_dict = attrgetter(subject, '__dict__', {})

    members = {}  # type: Dict[str, Attribute]

    # enum members
    if isenumclass(subject):
        for name, value in subject.__members__.items():
            if name not in members:
                members[name] = Attribute(name, True, value)

        superclass = subject.__mro__[1]
        for name in obj_dict:
            if name not in superclass.__dict__:
                value = safe_getattr(subject, name)
                members[name] = Attribute(name, True, value)

    # members in __slots__
    try:
        __slots__ = getslots(subject)
        if __slots__:
            from sphinx.ext.autodoc import SLOTSATTR

            for name in __slots__:
                members[name] = Attribute(name, True, SLOTSATTR)
    except (AttributeError, TypeError, ValueError):
        pass

    # other members
    for name in dir(subject):
        try:
            value = attrgetter(subject, name)
            directly_defined = name in obj_dict
            name = unmangle(subject, name)
            if name and name not in members:
                members[name] = Attribute(name, directly_defined, value)
        except AttributeError:
            continue

    # annotation only member (ex. attr: int)
    for i, cls in enumerate(getmro(subject)):
        try:
            for name in getannotations(cls):
                name = unmangle(cls, name)
                if name and name not in members:
                    members[name] = Attribute(name, i == 0, INSTANCEATTR)
        except AttributeError:
            pass

    if analyzer:
        # append instance attributes (cf. self.attr1) if analyzer knows
        namespace = '.'.join(objpath)
        for (ns, name) in analyzer.find_attr_docs():
            if namespace == ns and name not in members:
                members[name] = Attribute(name, True, INSTANCEATTR)

    return members


class ClassAttribute:
    """The attribute of the class."""

    def __init__(self, cls: Any, name: str, value: Any, docstring: Optional[str] = None):
        self.class_ = cls
        self.name = name
        self.value = value
        self.docstring = docstring
```
### 51 - sphinx/ext/autodoc/__init__.py:

Start line: 1722, End line: 1738

```python
class GenericAliasMixin(DataDocumenterMixinBase):
    """
    Mixin for DataDocumenter and AttributeDocumenter to provide the feature for
    supporting GenericAliases.
    """

    def should_suppress_directive_header(self) -> bool:
        return (inspect.isgenericalias(self.object) or
                super().should_suppress_directive_header())

    def update_content(self, more_content: StringList) -> None:
        if inspect.isgenericalias(self.object):
            alias = stringify_typehint(self.object)
            more_content.append(_('alias of %s') % alias, '')
            more_content.append('', '')

        super().update_content(more_content)
```
### 52 - sphinx/ext/autodoc/__init__.py:

Start line: 365, End line: 374

```python
class Documenter:

    def resolve_name(self, modname: str, parents: Any, path: str, base: Any
                     ) -> Tuple[str, List[str]]:
        """Resolve the module and name of the object to document given by the
        arguments and the current module/class.

        Must return a pair of the module name and a chain of attributes; for
        example, it would return ``('zipfile', ['ZipFile', 'open'])`` for the
        ``zipfile.ZipFile.open`` method.
        """
        raise NotImplementedError('must be implemented in subclasses')
```
### 53 - sphinx/ext/autodoc/__init__.py:

Start line: 626, End line: 652

```python
class Documenter:

    def get_object_members(self, want_all: bool) -> Tuple[bool, ObjectMembers]:
        """Return `(members_check_module, members)` where `members` is a
        list of `(membername, member)` pairs of the members of *self.object*.

        If *want_all* is True, return all members.  Else, only return those
        members given by *self.options.members* (which may also be none).
        """
        warnings.warn('The implementation of Documenter.get_object_members() will be '
                      'removed from Sphinx-6.0.', RemovedInSphinx60Warning)
        members = get_object_members(self.object, self.objpath, self.get_attr, self.analyzer)
        if not want_all:
            if not self.options.members:
                return False, []  # type: ignore
            # specific members given
            selected = []
            for name in self.options.members:  # type: str
                if name in members:
                    selected.append((name, members[name].value))
                else:
                    logger.warning(__('missing attribute %s in object %s') %
                                   (name, self.fullname), type='autodoc')
            return False, selected
        elif self.options.inherited_members:
            return False, [(m.name, m.value) for m in members.values()]
        else:
            return False, [(m.name, m.value) for m in members.values()
                           if m.directly_defined]
```
### 54 - sphinx/ext/autodoc/__init__.py:

Start line: 1252, End line: 1352

```python
class FunctionDocumenter(DocstringSignatureMixin, ModuleLevelDocumenter):  # type: ignore
    """
    Specialized Documenter subclass for functions.
    """
    objtype = 'function'
    member_order = 30

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any
                            ) -> bool:
        # supports functions, builtins and bound methods exported at the module level
        return (inspect.isfunction(member) or inspect.isbuiltin(member) or
                (inspect.isroutine(member) and isinstance(parent, ModuleDocumenter)))

    def format_args(self, **kwargs: Any) -> str:
        if self.config.autodoc_typehints in ('none', 'description'):
            kwargs.setdefault('show_annotation', False)

        try:
            self.env.app.emit('autodoc-before-process-signature', self.object, False)
            sig = inspect.signature(self.object, type_aliases=self.config.autodoc_type_aliases)
            args = stringify_signature(sig, **kwargs)
        except TypeError as exc:
            logger.warning(__("Failed to get a function signature for %s: %s"),
                           self.fullname, exc)
            return None
        except ValueError:
            args = ''

        if self.config.strip_signature_backslash:
            # escape backslashes for reST
            args = args.replace('\\', '\\\\')
        return args

    def document_members(self, all_members: bool = False) -> None:
        pass

    def add_directive_header(self, sig: str) -> None:
        sourcename = self.get_sourcename()
        super().add_directive_header(sig)

        if inspect.iscoroutinefunction(self.object):
            self.add_line('   :async:', sourcename)

    def format_signature(self, **kwargs: Any) -> str:
        sigs = []
        if (self.analyzer and
                '.'.join(self.objpath) in self.analyzer.overloads and
                self.config.autodoc_typehints == 'signature'):
            # Use signatures for overloaded functions instead of the implementation function.
            overloaded = True
        else:
            overloaded = False
            sig = super().format_signature(**kwargs)
            sigs.append(sig)

        if inspect.is_singledispatch_function(self.object):
            # append signature of singledispatch'ed functions
            for typ, func in self.object.registry.items():
                if typ is object:
                    pass  # default implementation. skipped.
                else:
                    self.annotate_to_first_argument(func, typ)

                    documenter = FunctionDocumenter(self.directive, '')
                    documenter.object = func
                    documenter.objpath = [None]
                    sigs.append(documenter.format_signature())
        if overloaded:
            __globals__ = safe_getattr(self.object, '__globals__', {})
            for overload in self.analyzer.overloads.get('.'.join(self.objpath)):
                overload = evaluate_signature(overload, __globals__,
                                              self.config.autodoc_type_aliases)

                sig = stringify_signature(overload, **kwargs)
                sigs.append(sig)

        return "\n".join(sigs)

    def annotate_to_first_argument(self, func: Callable, typ: Type) -> None:
        """Annotate type hint to the first argument of function if needed."""
        try:
            sig = inspect.signature(func, type_aliases=self.config.autodoc_type_aliases)
        except TypeError as exc:
            logger.warning(__("Failed to get a function signature for %s: %s"),
                           self.fullname, exc)
            return
        except ValueError:
            return

        if len(sig.parameters) == 0:
            return

        params = list(sig.parameters.values())
        if params[0].annotation is Parameter.empty:
            params[0] = params[0].replace(annotation=typ)
            try:
                func.__signature__ = sig.replace(parameters=params)  # type: ignore
            except TypeError:
                # failed to update signature (ex. built-in or extension types)
                return
```
### 55 - sphinx/ext/autodoc/__init__.py:

Start line: 2383, End line: 2411

```python
class PropertyDocumenter(DocstringStripSignatureMixin, ClassLevelDocumenter):  # type: ignore
    """
    Specialized Documenter subclass for properties.
    """
    objtype = 'property'
    directivetype = 'method'
    member_order = 60

    # before AttributeDocumenter
    priority = AttributeDocumenter.priority + 1

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any
                            ) -> bool:
        return inspect.isproperty(member) and isinstance(parent, ClassDocumenter)

    def document_members(self, all_members: bool = False) -> None:
        pass

    def get_real_modname(self) -> str:
        return self.get_attr(self.parent or self.object, '__module__', None) \
            or self.modname

    def add_directive_header(self, sig: str) -> None:
        super().add_directive_header(sig)
        sourcename = self.get_sourcename()
        if inspect.isabstractmethod(self.object):
            self.add_line('   :abstractmethod:', sourcename)
        self.add_line('   :property:', sourcename)
```
### 56 - sphinx/ext/autodoc/__init__.py:

Start line: 1784, End line: 1797

```python
class TypeVarMixin(DataDocumenterMixinBase):

    def update_content(self, more_content: StringList) -> None:
        if isinstance(self.object, TypeVar):
            attrs = [repr(self.object.__name__)]
            for constraint in self.object.__constraints__:
                attrs.append(stringify_typehint(constraint))
            if self.object.__covariant__:
                attrs.append("covariant=True")
            if self.object.__contravariant__:
                attrs.append("contravariant=True")

            more_content.append(_('alias of TypeVar(%s)') % ", ".join(attrs), '')
            more_content.append('', '')

        super().update_content(more_content)
```
### 58 - sphinx/ext/autodoc/importer.py:

Start line: 11, End line: 37

```python
import importlib
import traceback
import warnings
from typing import Any, Callable, Dict, List, Mapping, NamedTuple, Optional, Tuple

from sphinx.deprecation import RemovedInSphinx40Warning, deprecated_alias
from sphinx.pycode import ModuleAnalyzer
from sphinx.util import logging
from sphinx.util.inspect import (getannotations, getmro, getslots, isclass, isenumclass,
                                 safe_getattr)

if False:
    # For type annotation
    from typing import Type  # NOQA

logger = logging.getLogger(__name__)


def mangle(subject: Any, name: str) -> str:
    """mangle the given name."""
    try:
        if isclass(subject) and name.startswith('__') and not name.endswith('__'):
            return "_%s%s" % (subject.__name__, name)
    except AttributeError:
        pass

    return name
```
### 59 - sphinx/ext/autodoc/__init__.py:

Start line: 1916, End line: 1931

```python
class NewTypeDataDocumenter(DataDocumenter):
    """
    Specialized Documenter subclass for NewTypes.

    Note: This must be invoked before FunctionDocumenter because NewType is a kind of
    function object.
    """

    objtype = 'newtypedata'
    directivetype = 'data'
    priority = FunctionDocumenter.priority + 1

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any
                            ) -> bool:
        return inspect.isNewType(member) and isattr
```
### 61 - sphinx/ext/autodoc/__init__.py:

Start line: 960, End line: 1002

```python
class ModuleDocumenter(Documenter):
    """
    Specialized Documenter subclass for modules.
    """
    objtype = 'module'
    content_indent = ''
    titles_allowed = True

    option_spec = {
        'members': members_option, 'undoc-members': bool_option,
        'noindex': bool_option, 'inherited-members': inherited_members_option,
        'show-inheritance': bool_option, 'synopsis': identity,
        'platform': identity, 'deprecated': bool_option,
        'member-order': member_order_option, 'exclude-members': exclude_members_option,
        'private-members': members_option, 'special-members': members_option,
        'imported-members': bool_option, 'ignore-module-all': bool_option
    }  # type: Dict[str, Callable]

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        merge_members_option(self.options)
        self.__all__ = None  # type: Optional[Sequence[str]]

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any
                            ) -> bool:
        # don't document submodules automatically
        return False

    def resolve_name(self, modname: str, parents: Any, path: str, base: Any
                     ) -> Tuple[str, List[str]]:
        if modname is not None:
            logger.warning(__('"::" in automodule name doesn\'t make sense'),
                           type='autodoc')
        return (path or '') + base, []

    def parse_name(self) -> bool:
        ret = super().parse_name()
        if self.args or self.retann:
            logger.warning(__('signature arguments or return annotation '
                              'given for automodule %s') % self.fullname,
                           type='autodoc')
        return ret
```
### 62 - sphinx/ext/autodoc/__init__.py:

Start line: 1355, End line: 1681

```python
class DecoratorDocumenter(FunctionDocumenter):
    """
    Specialized Documenter subclass for decorator functions.
    """
    objtype = 'decorator'

    # must be lower than FunctionDocumenter
    priority = -1

    def format_args(self, **kwargs: Any) -> Any:
        args = super().format_args(**kwargs)
        if ',' in args:
            return args
        else:
            return None


# Types which have confusing metaclass signatures it would be best not to show.
# These are listed by name, rather than storing the objects themselves, to avoid
# needing to import the modules.
_METACLASS_CALL_BLACKLIST = [
    'enum.EnumMeta.__call__',
]


# Types whose __new__ signature is a pass-thru.
_CLASS_NEW_BLACKLIST = [
    'typing.Generic.__new__',
]


class ClassDocumenter(DocstringSignatureMixin, ModuleLevelDocumenter):
```
### 65 - sphinx/ext/autodoc/__init__.py:

Start line: 1741, End line: 1757

```python
class NewTypeMixin(DataDocumenterMixinBase):
    """
    Mixin for DataDocumenter and AttributeDocumenter to provide the feature for
    supporting NewTypes.
    """

    def should_suppress_directive_header(self) -> bool:
        return (inspect.isNewType(self.object) or
                super().should_suppress_directive_header())

    def update_content(self, more_content: StringList) -> None:
        if inspect.isNewType(self.object):
            supertype = restify(self.object.__supertype__)
            more_content.append(_('alias of %s') % supertype, '')
            more_content.append('', '')

        super().update_content(more_content)
```
### 67 - sphinx/ext/autodoc/__init__.py:

Start line: 1934, End line: 2079

```python
class MethodDocumenter(DocstringSignatureMixin, ClassLevelDocumenter):  # type: ignore
    """
    Specialized Documenter subclass for methods (normal, static and class).
    """
    objtype = 'method'
    directivetype = 'method'
    member_order = 50
    priority = 1  # must be more than FunctionDocumenter

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any
                            ) -> bool:
        return inspect.isroutine(member) and \
            not isinstance(parent, ModuleDocumenter)

    def import_object(self, raiseerror: bool = False) -> bool:
        ret = super().import_object(raiseerror)
        if not ret:
            return ret

        # to distinguish classmethod/staticmethod
        obj = self.parent.__dict__.get(self.object_name)
        if obj is None:
            obj = self.object

        if (inspect.isclassmethod(obj) or
                inspect.isstaticmethod(obj, cls=self.parent, name=self.object_name)):
            # document class and static members before ordinary ones
            self.member_order = self.member_order - 1

        return ret

    def format_args(self, **kwargs: Any) -> str:
        if self.config.autodoc_typehints in ('none', 'description'):
            kwargs.setdefault('show_annotation', False)

        try:
            if self.object == object.__init__ and self.parent != object:
                # Classes not having own __init__() method are shown as no arguments.
                #
                # Note: The signature of object.__init__() is (self, /, *args, **kwargs).
                #       But it makes users confused.
                args = '()'
            else:
                if inspect.isstaticmethod(self.object, cls=self.parent, name=self.object_name):
                    self.env.app.emit('autodoc-before-process-signature', self.object, False)
                    sig = inspect.signature(self.object, bound_method=False,
                                            type_aliases=self.config.autodoc_type_aliases)
                else:
                    self.env.app.emit('autodoc-before-process-signature', self.object, True)
                    sig = inspect.signature(self.object, bound_method=True,
                                            type_aliases=self.config.autodoc_type_aliases)
                args = stringify_signature(sig, **kwargs)
        except TypeError as exc:
            logger.warning(__("Failed to get a method signature for %s: %s"),
                           self.fullname, exc)
            return None
        except ValueError:
            args = ''

        if self.config.strip_signature_backslash:
            # escape backslashes for reST
            args = args.replace('\\', '\\\\')
        return args

    def add_directive_header(self, sig: str) -> None:
        super().add_directive_header(sig)

        sourcename = self.get_sourcename()
        obj = self.parent.__dict__.get(self.object_name, self.object)
        if inspect.isabstractmethod(obj):
            self.add_line('   :abstractmethod:', sourcename)
        if inspect.iscoroutinefunction(obj):
            self.add_line('   :async:', sourcename)
        if inspect.isclassmethod(obj):
            self.add_line('   :classmethod:', sourcename)
        if inspect.isstaticmethod(obj, cls=self.parent, name=self.object_name):
            self.add_line('   :staticmethod:', sourcename)
        if self.analyzer and '.'.join(self.objpath) in self.analyzer.finals:
            self.add_line('   :final:', sourcename)

    def document_members(self, all_members: bool = False) -> None:
        pass

    def format_signature(self, **kwargs: Any) -> str:
        sigs = []
        if (self.analyzer and
                '.'.join(self.objpath) in self.analyzer.overloads and
                self.config.autodoc_typehints == 'signature'):
            # Use signatures for overloaded methods instead of the implementation method.
            overloaded = True
        else:
            overloaded = False
            sig = super().format_signature(**kwargs)
            sigs.append(sig)

        meth = self.parent.__dict__.get(self.objpath[-1])
        if inspect.is_singledispatch_method(meth):
            # append signature of singledispatch'ed functions
            for typ, func in meth.dispatcher.registry.items():
                if typ is object:
                    pass  # default implementation. skipped.
                else:
                    self.annotate_to_first_argument(func, typ)

                    documenter = MethodDocumenter(self.directive, '')
                    documenter.parent = self.parent
                    documenter.object = func
                    documenter.objpath = [None]
                    sigs.append(documenter.format_signature())
        if overloaded:
            __globals__ = safe_getattr(self.object, '__globals__', {})
            for overload in self.analyzer.overloads.get('.'.join(self.objpath)):
                overload = evaluate_signature(overload, __globals__,
                                              self.config.autodoc_type_aliases)

                if not inspect.isstaticmethod(self.object, cls=self.parent,
                                              name=self.object_name):
                    parameters = list(overload.parameters.values())
                    overload = overload.replace(parameters=parameters[1:])
                sig = stringify_signature(overload, **kwargs)
                sigs.append(sig)

        return "\n".join(sigs)

    def annotate_to_first_argument(self, func: Callable, typ: Type) -> None:
        """Annotate type hint to the first argument of function if needed."""
        try:
            sig = inspect.signature(func, type_aliases=self.config.autodoc_type_aliases)
        except TypeError as exc:
            logger.warning(__("Failed to get a method signature for %s: %s"),
                           self.fullname, exc)
            return
        except ValueError:
            return
        if len(sig.parameters) == 1:
            return

        params = list(sig.parameters.values())
        if params[1].annotation is Parameter.empty:
            params[1] = params[1].replace(annotation=typ)
            try:
                func.__signature__ = sig.replace(parameters=params)  # type: ignore
            except TypeError:
                # failed to update signature (ex. built-in or extension types)
                return
```
### 77 - sphinx/ext/autodoc/__init__.py:

Start line: 871, End line: 957

```python
class Documenter:

    def generate(self, more_content: Optional[StringList] = None, real_modname: str = None,
                 check_module: bool = False, all_members: bool = False) -> None:
        """Generate reST for the object given by *self.name*, and possibly for
        its members.

        If *more_content* is given, include that content. If *real_modname* is
        given, use that module name to find attribute docs. If *check_module* is
        True, only generate if the object is defined in the module name it is
        imported from. If *all_members* is True, document all members.
        """
        if not self.parse_name():
            # need a module to import
            logger.warning(
                __('don\'t know which module to import for autodocumenting '
                   '%r (try placing a "module" or "currentmodule" directive '
                   'in the document, or giving an explicit module name)') %
                self.name, type='autodoc')
            return

        # now, import the module and get object to document
        if not self.import_object():
            return

        # If there is no real module defined, figure out which to use.
        # The real module is used in the module analyzer to look up the module
        # where the attribute documentation would actually be found in.
        # This is used for situations where you have a module that collects the
        # functions and classes of internal submodules.
        guess_modname = self.get_real_modname()
        self.real_modname = real_modname or guess_modname

        # try to also get a source code analyzer for attribute docs
        try:
            self.analyzer = ModuleAnalyzer.for_module(self.real_modname)
            # parse right now, to get PycodeErrors on parsing (results will
            # be cached anyway)
            self.analyzer.find_attr_docs()
        except PycodeError as exc:
            logger.debug('[autodoc] module analyzer failed: %s', exc)
            # no source file -- e.g. for builtin and C modules
            self.analyzer = None
            # at least add the module.__file__ as a dependency
            if hasattr(self.module, '__file__') and self.module.__file__:
                self.directive.filename_set.add(self.module.__file__)
        else:
            self.directive.filename_set.add(self.analyzer.srcname)

        if self.real_modname != guess_modname:
            # Add module to dependency list if target object is defined in other module.
            try:
                analyzer = ModuleAnalyzer.for_module(guess_modname)
                self.directive.filename_set.add(analyzer.srcname)
            except PycodeError:
                pass

        # check __module__ of object (for members not given explicitly)
        if check_module:
            if not self.check_module():
                return

        sourcename = self.get_sourcename()

        # make sure that the result starts with an empty line.  This is
        # necessary for some situations where another directive preprocesses
        # reST and no starting newline is present
        self.add_line('', sourcename)

        # format the object's signature, if any
        try:
            sig = self.format_signature()
        except Exception as exc:
            logger.warning(__('error while formatting signature for %s: %s'),
                           self.fullname, exc, type='autodoc')
            return

        # generate the directive header and options, if applicable
        self.add_directive_header(sig)
        self.add_line('', sourcename)

        # e.g. the module directive doesn't have content
        self.indent += self.content_indent

        # add all content (from docstrings, attribute docs etc.)
        self.add_content(more_content)

        # document members, if possible
        self.document_members(all_members)
```
### 78 - sphinx/ext/autodoc/__init__.py:

Start line: 413, End line: 432

```python
class Documenter:

    def import_object(self, raiseerror: bool = False) -> bool:
        """Import the object given by *self.modname* and *self.objpath* and set
        it as *self.object*.

        Returns True if successful, False if an error occurred.
        """
        with mock(self.config.autodoc_mock_imports):
            try:
                ret = import_object(self.modname, self.objpath, self.objtype,
                                    attrgetter=self.get_attr,
                                    warningiserror=self.config.autodoc_warningiserror)
                self.module, self.parent, self.object_name, self.object = ret
                return True
            except ImportError as exc:
                if raiseerror:
                    raise
                else:
                    logger.warning(exc.args[0], type='autodoc', subtype='import_object')
                    self.env.note_reread()
                    return False
```
### 83 - sphinx/ext/autodoc/__init__.py:

Start line: 1234, End line: 1249

```python
class DocstringStripSignatureMixin(DocstringSignatureMixin):
    """
    Mixin for AttributeDocumenter to provide the
    feature of stripping any function signature from the docstring.
    """
    def format_signature(self, **kwargs: Any) -> str:
        if self.args is None and self.config.autodoc_docstring_signature:  # type: ignore
            # only act if a signature is not explicitly given already, and if
            # the feature is enabled
            result = self._find_signature()
            if result is not None:
                # Discarding _args is a only difference with
                # DocstringSignatureMixin.format_signature.
                # Documenter.format_signature use self.args value to format.
                _args, self.retann = result
        return super().format_signature(**kwargs)
```
### 86 - sphinx/ext/autodoc/__init__.py:

Start line: 434, End line: 482

```python
class Documenter:

    def get_real_modname(self) -> str:
        """Get the real module name of an object to document.

        It can differ from the name of the module through which the object was
        imported.
        """
        return self.get_attr(self.object, '__module__', None) or self.modname

    def check_module(self) -> bool:
        """Check if *self.object* is really defined in the module given by
        *self.modname*.
        """
        if self.options.imported_members:
            return True

        subject = inspect.unpartial(self.object)
        modname = self.get_attr(subject, '__module__', None)
        if modname and modname != self.modname:
            return False
        return True

    def format_args(self, **kwargs: Any) -> str:
        """Format the argument signature of *self.object*.

        Should return None if the object does not have a signature.
        """
        return None

    def format_name(self) -> str:
        """Format the name of *self.object*.

        This normally should be something that can be parsed by the generated
        directive, but doesn't need to be (Sphinx will display it unparsed
        then).
        """
        # normally the name doesn't contain the module (except for module
        # directives of course)
        return '.'.join(self.objpath) or self.modname

    def _call_format_args(self, **kwargs: Any) -> str:
        if kwargs:
            try:
                return self.format_args(**kwargs)
            except TypeError:
                # avoid chaining exceptions, by putting nothing here
                pass

        # retry without arguments for old documenters
        return self.format_args()
```
### 87 - sphinx/ext/autodoc/__init__.py:

Start line: 846, End line: 869

```python
class Documenter:

    def sort_members(self, documenters: List[Tuple["Documenter", bool]],
                     order: str) -> List[Tuple["Documenter", bool]]:
        """Sort the given member list."""
        if order == 'groupwise':
            # sort by group; alphabetically within groups
            documenters.sort(key=lambda e: (e[0].member_order, e[0].name))
        elif order == 'bysource':
            if self.analyzer:
                # sort by source order, by virtue of the module analyzer
                tagorder = self.analyzer.tagorder

                def keyfunc(entry: Tuple[Documenter, bool]) -> int:
                    fullname = entry[0].name.split('::')[1]
                    return tagorder.get(fullname, len(tagorder))
                documenters.sort(key=keyfunc)
            else:
                # Assume that member discovery order matches source order.
                # This is a reasonable assumption in Python 3.6 and up, where
                # module.__dict__ is insertion-ordered.
                pass
        else:  # alphabetical
            documenters.sort(key=lambda e: e[0].name)

        return documenters
```
### 89 - sphinx/ext/autodoc/__init__.py:

Start line: 558, End line: 571

```python
class Documenter:

    def process_doc(self, docstrings: List[List[str]]) -> Iterator[str]:
        """Let the user process the docstrings before adding them."""
        for docstringlines in docstrings:
            if self.env.app:
                # let extensions preprocess docstrings
                self.env.app.emit('autodoc-process-docstring',
                                  self.objtype, self.fullname, self.object,
                                  self.options, docstringlines)

                if docstringlines and docstringlines[-1] != '':
                    # append a blank line to the end of the docstring
                    docstringlines.append('')

            yield from docstringlines
```
### 92 - sphinx/ext/autodoc/__init__.py:

Start line: 1139, End line: 1209

```python
class DocstringSignatureMixin:
    """
    Mixin for FunctionDocumenter and MethodDocumenter to provide the
    feature of reading the signature from the docstring.
    """
    _new_docstrings = None  # type: List[List[str]]
    _signatures = None      # type: List[str]

    def _find_signature(self, encoding: str = None) -> Tuple[str, str]:
        if encoding is not None:
            warnings.warn("The 'encoding' argument to autodoc.%s._find_signature() is "
                          "deprecated." % self.__class__.__name__,
                          RemovedInSphinx40Warning, stacklevel=2)

        # candidates of the object name
        valid_names = [self.objpath[-1]]  # type: ignore
        if isinstance(self, ClassDocumenter):
            valid_names.append('__init__')
            if hasattr(self.object, '__mro__'):
                valid_names.extend(cls.__name__ for cls in self.object.__mro__)

        docstrings = self.get_doc()
        self._new_docstrings = docstrings[:]
        self._signatures = []
        result = None
        for i, doclines in enumerate(docstrings):
            for j, line in enumerate(doclines):
                if not line:
                    # no lines in docstring, no match
                    break

                if line.endswith('\\'):
                    multiline = True
                    line = line.rstrip('\\').rstrip()
                else:
                    multiline = False

                # match first line of docstring against signature RE
                match = py_ext_sig_re.match(line)
                if not match:
                    continue
                exmod, path, base, args, retann = match.groups()

                # the base name must match ours
                if base not in valid_names:
                    continue

                # re-prepare docstring to ignore more leading indentation
                tab_width = self.directive.state.document.settings.tab_width  # type: ignore
                self._new_docstrings[i] = prepare_docstring('\n'.join(doclines[j + 1:]),
                                                            tabsize=tab_width)

                if result is None:
                    # first signature
                    result = args, retann
                else:
                    # subsequent signatures
                    self._signatures.append("(%s) -> %s" % (args, retann))

                if multiline:
                    # the signature have multiple signatures on docstring
                    continue
                else:
                    # don't look any further
                    break

            if result:
                # finish the loop when signature found
                break

        return result
```
### 93 - sphinx/ext/autodoc/importer.py:

Start line: 40, End line: 56

```python
def unmangle(subject: Any, name: str) -> Optional[str]:
    """unmangle the given name."""
    try:
        if isclass(subject) and not name.endswith('__'):
            prefix = "_%s__" % subject.__name__
            if name.startswith(prefix):
                return name.replace(prefix, "__", 1)
            else:
                for cls in subject.__mro__:
                    prefix = "_%s__" % cls.__name__
                    if name.startswith(prefix):
                        # mangled attribute defined in parent class
                        return None
    except AttributeError:
        pass

    return name
```
### 96 - sphinx/ext/autodoc/__init__.py:

Start line: 587, End line: 624

```python
class Documenter:

    def add_content(self, more_content: Optional[StringList], no_docstring: bool = False
                    ) -> None:
        """Add content from docstrings, attribute documentation and user."""
        if no_docstring:
            warnings.warn("The 'no_docstring' argument to %s.add_content() is deprecated."
                          % self.__class__.__name__,
                          RemovedInSphinx50Warning, stacklevel=2)

        # set sourcename and add content from attribute documentation
        sourcename = self.get_sourcename()
        if self.analyzer:
            attr_docs = self.analyzer.find_attr_docs()
            if self.objpath:
                key = ('.'.join(self.objpath[:-1]), self.objpath[-1])
                if key in attr_docs:
                    no_docstring = True
                    # make a copy of docstring for attributes to avoid cache
                    # the change of autodoc-process-docstring event.
                    docstrings = [list(attr_docs[key])]

                    for i, line in enumerate(self.process_doc(docstrings)):
                        self.add_line(line, sourcename, i)

        # add content from docstrings
        if not no_docstring:
            docstrings = self.get_doc()
            if not docstrings:
                # append at least a dummy docstring, so that the event
                # autodoc-process-docstring is fired and can add some
                # content if desired
                docstrings.append([])
            for i, line in enumerate(self.process_doc(docstrings)):
                self.add_line(line, sourcename, i)

        # add additional content (e.g. from document), if present
        if more_content:
            for line, src in zip(more_content.data, more_content.items):
                self.add_line(line, src[0], src[1])
```
### 99 - sphinx/ext/autodoc/importer.py:

Start line: 140, End line: 160

```python
def get_module_members(module: Any) -> List[Tuple[str, Any]]:
    """Get members of target module."""
    from sphinx.ext.autodoc import INSTANCEATTR

    members = {}  # type: Dict[str, Tuple[str, Any]]
    for name in dir(module):
        try:
            value = safe_getattr(module, name, None)
            members[name] = (name, value)
        except AttributeError:
            continue

    # annotation only member (ex. attr: int)
    try:
        for name in getannotations(module):
            if name not in members:
                members[name] = (name, INSTANCEATTR)
    except AttributeError:
        pass

    return sorted(list(members.values()))
```
### 100 - sphinx/ext/autodoc/__init__.py:

Start line: 541, End line: 556

```python
class Documenter:

    def get_doc(self, encoding: str = None, ignore: int = None) -> List[List[str]]:
        """Decode and return lines of the docstring(s) for the object."""
        if encoding is not None:
            warnings.warn("The 'encoding' argument to autodoc.%s.get_doc() is deprecated."
                          % self.__class__.__name__,
                          RemovedInSphinx40Warning, stacklevel=2)
        if ignore is not None:
            warnings.warn("The 'ignore' argument to autodoc.%s.get_doc() is deprecated."
                          % self.__class__.__name__,
                          RemovedInSphinx50Warning, stacklevel=2)
        docstring = getdoc(self.object, self.get_attr, self.config.autodoc_inherit_docstrings,
                           self.parent, self.object_name)
        if docstring:
            tab_width = self.directive.state.document.settings.tab_width
            return [prepare_docstring(docstring, ignore, tab_width)]
        return []
```
### 130 - sphinx/ext/autodoc/__init__.py:

Start line: 519, End line: 539

```python
class Documenter:

    def add_directive_header(self, sig: str) -> None:
        """Add the directive header and options to the generated content."""
        domain = getattr(self, 'domain', 'py')
        directive = getattr(self, 'directivetype', self.objtype)
        name = self.format_name()
        sourcename = self.get_sourcename()

        # one signature per line, indented by column
        prefix = '.. %s:%s:: ' % (domain, directive)
        for i, sig_line in enumerate(sig.split("\n")):
            self.add_line('%s%s%s' % (prefix, name, sig_line),
                          sourcename)
            if i == 0:
                prefix = " " * len(prefix)

        if self.options.noindex:
            self.add_line('   :noindex:', sourcename)
        if self.objpath:
            # Be explicit about the module, this is necessary since .. class::
            # etc. don't support a prepended module name
            self.add_line('   :module: %s' % self.modname, sourcename)
```
### 131 - sphinx/ext/autodoc/__init__.py:

Start line: 1760, End line: 1782

```python
class TypeVarMixin(DataDocumenterMixinBase):
    """
    Mixin for DataDocumenter and AttributeDocumenter to provide the feature for
    supporting TypeVars.
    """

    def should_suppress_directive_header(self) -> bool:
        return (isinstance(self.object, TypeVar) or
                super().should_suppress_directive_header())

    def get_doc(self, encoding: str = None, ignore: int = None) -> List[List[str]]:
        if ignore is not None:
            warnings.warn("The 'ignore' argument to autodoc.%s.get_doc() is deprecated."
                          % self.__class__.__name__,
                          RemovedInSphinx50Warning, stacklevel=2)

        if isinstance(self.object, TypeVar):
            if self.object.__doc__ != TypeVar.__doc__:
                return super().get_doc()  # type: ignore
            else:
                return []
        else:
            return super().get_doc()  # type: ignore
```
### 137 - sphinx/ext/autodoc/__init__.py:

Start line: 155, End line: 181

```python
def merge_special_members_option(options: Dict) -> None:
    """Merge :special-members: option to :members: option."""
    warnings.warn("merge_special_members_option() is deprecated.",
                  RemovedInSphinx50Warning, stacklevel=2)
    if 'special-members' in options and options['special-members'] is not ALL:
        if options.get('members') is ALL:
            pass
        elif options.get('members'):
            for member in options['special-members']:
                if member not in options['members']:
                    options['members'].append(member)
        else:
            options['members'] = options['special-members']


def merge_members_option(options: Dict) -> None:
    """Merge :*-members: option to the :members: option."""
    if options.get('members') is ALL:
        # merging is not needed when members: ALL
        return

    members = options.setdefault('members', [])
    for key in {'private-members', 'special-members'}:
        if key in options and options[key] not in (ALL, None):
            for member in options[key]:
                if member not in members:
                    members.append(member)
```