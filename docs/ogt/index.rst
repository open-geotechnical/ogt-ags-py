#####################
ogt:  Base API
#####################

The base API deals with:
    
- File input and output, serialisation to different :attr:`~ogt.__init__.FORMATS`
    - see :mod:`ogt.utils`
    - the :ref:`json` functions, eg :func:`~ogt.utils.to_json`, :func:`~ogt.utils.read_json_file`
- **Project**
    - todo
- **Document**
    - the module :mod:`ogt.ogt_doc`
    - the class :class:`~ogt.ogt_doc.OGTDocument`
- **Groups**
    - the module :mod:`ogt.ogt_group`
    - the class :class:`~ogt.ogt_group.OGTGroup`
- **AGS**
    - the module :mod:`ogt.ags.ags4`
    - the class :class:`~ogt.ags.ags4.AGS4GroupDataDict`
    - the function :func:`~ogt.ogt_doc.create_doc_from_ags4_file`


**Index**


.. toctree::
    :maxdepth: 3

    ogt_init.rst
    ogt_doc.rst
    ogt_group.rst
    utils.rst
    ags4.rst

