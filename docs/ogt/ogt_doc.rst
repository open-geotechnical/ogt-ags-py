######################
ogt.ogt_doc.*
######################

An :class:`~ogt.ogt_doc.OGTDocument` contains the groups (:class:`~ogt.ogt_group.OGTGroup`) in a document.

**Examples**

.. code-block:: python

    from ogt import ogt_doc
    
    # Create a doc from an ags4 file
    doc, err = ogt_doc.create_doc_from_ags4_file("/path/to/my.ags")
    if err:
        print err
    else:
        # print the groups index
        print doc.groups_index()
        
        # outputs the SAMP group in json
        print doc.group("SAMP").to_json()
        
        
        # Return a list of units used in the document
        print doc.units()
        


.. automodule:: ogt.ogt_doc
    :members:
        