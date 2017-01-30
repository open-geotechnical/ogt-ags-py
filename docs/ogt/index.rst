#####################
ogt:  Base API
#####################

The base API deals with:

- **Project**
    - An AGS zip file and its images, media etc (coming soon)
- **Document**
    - represents an ags file
    - the module :mod:`ogt.ogt_doc`
    - the class :class:`~ogt.ogt_doc.OGTDocument`
- **Groups**
    - represents and ags group and headings
    - the module :mod:`ogt.ogt_group`
    - the class :class:`~ogt.ogt_group.OGTGroup`
- **AGS**
    - the ags data dict
    - validation (coming soon)
    - the module :mod:`ogt.ags4`
    - the class :class:`~ogt.ags4.AGS4GroupDataDict`
    - the function :func:`~ogt.ogt_doc.create_doc_from_ags4_file`
- **utils**
    - File input and output, serialisation to different :attr:`~ogt.__init__.FORMATS`
    - see :mod:`ogt.utils`
    - the :ref:`json` functions, eg :func:`~ogt.utils.to_json`, :func:`~ogt.utils.read_json_file`

**Index**


.. toctree::
    :maxdepth: 3

    ogt_init.rst
    ogt_doc.rst
    ogt_group.rst
    utils.rst
    ags4.rst

