#####################
ogt:  Base API
#####################

The base API converts ags4 files into various formats, and provided validation (WIP) to the data dictionary


.. graphviz::

   digraph {
      Project [shape=box]
      Document [label="Document.ags"]
      Group1 [label="Group"]
      Group2 [label="Group"]

      Head11 [label="Heading", color=blue]
      Head12 [label="Heading", color=blue]

      Head21 [label="Heading", color=blue]
      Head22 [label="Heading", color=blue]

      dd1 [label="Group Data Dict", color=green]
      dd2 [label="Group Data Dict", color=green]

      Files [label="Files"]
      f1 [label="File", color=blue]
      f2 [label="File", color=blue]

      Agsdd [label="Ags4 Data Dict", color=green]

      Project -> Files

      Files -> f1
      Files -> f2

      Project -> Document



      Document -> Group1
      Document -> Group2


      Group1 -> Head11
      Group1 -> Head12
      Group2 -> Head21
      Group2 -> Head22

      Group1 -> dd1
      Group2 -> dd2

      Agsdd -> dd1
      Agsdd -> dd2

      Head11 -> dd1
      Head12 -> dd1

      Head21 -> dd2
      Head22 -> dd2
   }



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

Index
-------------
.. toctree::
    :maxdepth: 3

    ogt_init.rst
    ogt_doc.rst
    ogt_group.rst
    utils.rst
    ags4.rst
    notes.rst

