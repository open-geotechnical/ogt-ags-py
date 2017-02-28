Dev Notes
=====================

.. _edit_mode:

edit_mode
------------------

With json and yaml, data can be serialised in two "structrues" set by **edit_mode** (eg see  :meth:`~ogt.ogt_group.OGTGroup.to_dict`)


**edit_mode=False**

- Groups are serialised as a minimal `key/value` pair
- This is suitable for just the raw data as repreented in the ags file

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


**edit_mode=True**

- Extra data is added from the data dict such as descriptions, units, types, etc
- This is suitable for editors or presentations

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
                        "head_code": "PROJ_ID",
                        "head_description": "Project identifier",
                        "head_status": "*R",
                        "sort_order": 1,
                        "data_type": "ID",
                        "unit": "",
                        "example": "121415"
                    }
                },
                {
                    "head_code": "PROJ_NAME",
                    "type": "X",
                    "unit": ""
                    "data_dict": {
                        "head_code": "PROJ_NAME",
                        "head_description": "Project title",
                        "head_status": "",
                        "sort_order": 2,
                        "data_type": "X",
                        "unit": "",
                        "example": "ACME Gas Works Redevelopment"
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


.. _circular_import:

Circular Imports
------------------

Thus far circular imports have been a real problem in this project. The reason is
then they are infact interdependant
- and if any `py dev` expert can solve that then please do
- Many things tried but failsafe is full path

So all import are full path **within the lib** eg

.. code-block:: python

    # good
    import ogt.ogt_doc
    doc = ogt.ogt_doc.OGTDocument()

    #vs
    import ogt.ogt_doc
