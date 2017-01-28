==================
References
==================

.. _ASCII:

ASCII
==================

The American Standard Code for Information Interchange (ASCII) is
a character-encoding scheme originally based on the English alphabet
that encodes 128 specified characters - the numbers 0-9, the letters a-z and
A-Z, some basic punctuation symbols, some control codes that
originated with Teletype machines, and a
blank space - into the 7-bit binary integers.

.. note:: See also

    - See :ref:`ags4_rule_1`


**Notable characters**

    +----------+------------------+---------+--------------------------+
    | No       | Name             | Preview | Links                    |
    +==========+==================+=========+==========================+
    | 10       | line feed        |         | :ref:`ags4_rule_2a`      |
    +----------+------------------+---------+--------------------------+
    | 13       | carriage return  |         | :ref:`ags4_rule_2a`      |
    +----------+------------------+---------+--------------------------+
    | 34       | double quote     | "       | :ref:`ags4_rule_5`       |
    +----------+------------------+---------+--------------------------+
    | 43       | plus sign        | \+      | :ref:`ags4_rule_11b`     |
    +----------+------------------+---------+--------------------------+
    | 44       | comma            | ,       | :ref:`ags4_rule_6`       |
    +----------+------------------+---------+--------------------------+
    | 124      | pipe             | \|      | :ref:`ags4_rule_11a`     |
    +----------+------------------+---------+--------------------------+


.. seealso:: Reference Links

    - http://en.wikipedia.org/wiki/ASCII
    - http://www.asciitable.com/
    - http://www.ascii.cl/htmlcodes.htm

.. _CSV:

CSV
==================

See https://en.wikipedia.org/wiki/Comma-separated_values

.. seealso:: See also

    - :ref:`ags4_rule_6`
    - :ref:`ags4_rule_note_1`


.. _edit_mode:

edit_mode
==================
The api serialises the data out in two formats (eg see  :meth:`~ogt.ogt_group.OGTGroup.to_dict`)

**With edit_mode=False**

- Groups are serialised as a minimal key:value pair

    .. code-block:: js

        "PROJ": {
            "DATA": [
                {
                    "PROJ_ID": "1234",
                    "PROJ_NAME": "Example Project"
                }
            ],
            "TYPE": {
                "PROJ_ID": "ID",
                "PROJ_NAME": "X"
            },
            "UNIT": {
                "PROJ_ID": "",
                "PROJ_NAME": ""
            }
        },


**With edit_mode=True**

- Extra data is added, such as descriptions, units, types, headers from the **data_dict**
- Note the extra **data_dict** added to `"group"` and `"headers"` in example below


    .. code-block:: js

        "PROJ": {
            "group_code": "PROJ",
            "data_dict": {
                "child": "-",
                "class": "Project / Data Transmission Details",
                "group_code": "PROJ",
                "group_description": "Project Information",
                "group_status": "Required in all files (Rule 13)",
                "parent": "-",
                "notes": [
                    "PROJ is required in all AGS4 files (Rule 13).",
                    "PROJ_ENG should contain the details of the consultant/designer for the project."
                ]
            },

            "headings_sort": [
                "PROJ_ID",
                "PROJ_NAME"
            ],
            "headings": [
                {
                    "head_code": "PROJ_ID",
                    "type": "ID",
                    "unit": "",
                    "data_dict": {
                        "example": "121415",
                        "head_code": "PROJ_ID",
                        "head_description": "Project identifier",
                        "head_status": "*R",
                        "sort_order": 1,
                        "suggested_type": "ID",
                        "suggested_unit": ""
                    }
                },
                {
                    "head_code": "PROJ_NAME",
                    "type": "X",
                    "unit": ""
                    "data_dict": {
                        "example": "ACME Gas Works Redevelopment",
                        "head_code": "PROJ_NAME",
                        "head_description": "Project title",
                        "head_status": "",
                        "sort_order": 2,
                        "suggested_type": "X",
                        "suggested_unit": ""
                    }
                }
            ]

            "data": [
                {
                    "PROJ_ID": "1234",
                    "PROJ_NAME": "Example Project"
                }
            ]
        }








.. _excel:
    
Excel
==================
    
TODO    



.. _json:

JSON
==================
**JavaScript Object Notation** (JSON) is a lightweight data-interchange format.  It is easy for humans to read
and write. It is easy for machines to parse and
generate. It is based on a subset of the JavaScript Programming Language,

.. hint::

    - It is highly recommended to use the functions in the :mod:`ogt.utils`  module to
      serialise json for consistency. See:

      - :func:`~ogt.utils.to_json`
      - :func:`~ogt.utils.write_json_file`
      - :func:`~ogt.utils.read_json_file`

.. seealso:: Reference Links

    - http://www.json.org/
    - https://en.wikipedia.org/wiki/JSON
    - http://www.w3schools.com/js/js_json_intro.asp

.. _python:

Python
==================
TODO


.. _yaml:

YAML
==================

- YAML: YAML Ain't Markup Language
- Is a human friendly data serialization standard for all programming languages

.. note:: Note:

    - The python `yaml` extention is required
    - Install with :code:`pip install yaml`
    - API reference at http://pyyaml.org/wiki/PyYAMLDocumentation

.. seealso:: Reference Links

    - http://yaml.org/
    - https://en.wikipedia.org/wiki/YAML

TODO list
==================

.. todolist::


