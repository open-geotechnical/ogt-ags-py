AGS Toolkit in Python
===========================================

This project is some R&D for converting AGS data using Python. Circa Jan 2017 is in active development.

- See :ref:`ogt-cli.py` for command line examples

.. code-block:: python

    # api example

    from ogt import ogt_doc

    # Create a doc from an ags4 file
    doc, err = ogt_doc.create_doc_from_ags4_file("/path/to/my.ags")
    if err:
        print err
    else:
        # print the groups index
        print doc.groups_index()

        # outputs the SAMP group as json string
        print doc.group("SAMP").to_json()

        # write doc as yaml
        print doc.write("/path/to.my.yaml", format="yaml)

        # Return a list of units used in the document
        print doc.units()



**Contents:**

.. toctree::
    :maxdepth: 1


    ogt/index.rst
    ogtgui/index.rst
    ogtserver/index.rst
    commands.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


