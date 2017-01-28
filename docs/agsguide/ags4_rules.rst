
.. role:: csv_rule

    :class: ags-csv-rule

.. role:: data_rule

    :class: ags-data-rule

.. _ags4_rules:


====================================================
AGS4 - Rules
====================================================


The following rules shall be used when creating an AGS4 data file (eg :file:`my_stuff.ags`).

- :csv_rule:`CSV Rule` - means :ref:`CSV` file format rule
- :data_rule:`Data Rule` - means and aata rule


.. _ags4_rule_1:

Rule 1 - Character Set
=======================================


:csv_rule:`CSV Rule`

- The data file shall be entirely composed of :ref:`ASCII` characters.

.. warning::

    It is quite easy to violate this rule, eg Excel can insert a Windows character, or a cut paste from pdf.

.. seealso::

    - :ref:`ags4_rule_note_1`
    - :func:`~ogt.ags.ags4.rule_1`

.. _ags4_rule_2:

Rule 2 - GROUP's required
=======================================

:csv_rule:`CSV Rule`


- Each data file shall contain one or more data :term:`GROUP`'s.
- Each data GROUP shall comprise a number of :term:`GROUP HEADER`
- rows must have one or more \ref DATA rows


.. _ags4_rule_2a:

Rule 2a - CRLF New Line
-----------------------

- Each row is located on a separate line, delimited by a **new line**
- A **new line** consists of the two characters:

    - a **carriage return** (CR) (:ref:`ASCII` character 13)
    - followed by a **line feed** (LF) (:ref:`ASCII` character 10)


.. note:: Note

   For Windows; CRLF is the default, and all text files are saved as CRLF by default.

.. seealso:: See also

    - :func:`~ogt.ags.ags4.rule_2`


.. _ags4_rule_2b:

Rule 2b - GROUP HEADER
---------------------------
- The :term:`GROUP HEADER` rows fully define the data presented within the :term:`DATA` rows
  for that group (:ref:`ags4_rule_8`).
- As a minimum, the GROUP HEADER rows comprise
    - :term:`GROUP`, :term:`HEADING`, :term:`UNIT` and :term:`TYPE` rows, **presented in that order**.



.. _ags4_rule_3:

Rule 3 - Data Descriptors
=======================================

:csv_rule:`CSV Rule`

- Each row in the data file must start with a **DATA DESCRIPTOR** that defines the contents of that row.
- The following Data Descriptors are used as described below:

    - Each :term:`GROUP` row shall be preceded by the `"GROUP"` data descriptor
    - Each :term:`HEADING` row shall be preceded by the `"HEADING"` data descriptor
    - Each :term:`UNIT` row shall be preceded by the `"UNIT"` data descriptor
    - Each :term:`TYPE` row shall be preceded by the `"TYPE"` data descriptor
    - Each :term:`DATA` row shall be preceded by the `"DATA"` data descriptor


**Example**

.. code-block:: javascript

    "GROUP","HORN"
    "HEADING","LOCA_ID","HORN_TOP","HORN_BASE","HORN_ORNT","HORN_INCL","HORN_REM","FILE_FSET"
    "UNIT","","m","m","deg","deg","",""
    "TYPE","ID","2DP","2DP","0DP","0DP","X","X"
    "DATA","BH502","0.00","1.20","210","65","",""
    "DATA","BH502","0.00","15.45","210","65","",""


.. seealso::

    - :class:`ogt.ags.ags4.AGS4_DATA_DESCRIPTORS`
    - :func:`~ogt.ags.ags4.rule_3`

.. _ags4_rule_4:

Rule 4 - FIELD's
=======================================

:csv_rule:`CSV Rule`

- Within each GROUP, the DATA items are contained in data FIELDs. Each data
  FIELD contains a single data VARIABLE in each row. Each DATA
  row of a data file will contain one or more data FIELDs.
- The GROUP row contains only one DATA item, the GROUP name, in
  addition to the Data Descriptor (:ref:`ags4_rule_3`).
- All other rows in the GROUP have a number of DATA items defined by the HEADING row.
 
.. seealso::

    - :func:`~ogt.ags.ags4.rule_4`

 
.. _ags4_rule_5:

Rule 5 - Double Quotes
=======================================

:csv_rule:`CSV Rule`

- :term:`DATA DESCRIPTORS`,  :term:`GROUP` names, data field :term:`HEADING` s, data field :term:`UNIT` s,
  data field :term:`TYPE` s, and data :term:`VARIABLE` s shall be enclosed in double quotes (`"..."`).
- Any quotes within a data item must be defined with a second quote, example below.

.. code-block:: javascript

    "he said ""hello"" to me"

.. note::

    A double quote is :ref:`ASCII` char 34

.. seealso::

    - :func:`~ogt.ags.ags4.rule_5`

.. _ags4_rule_6:
 
Rule 6 - Comma Separated
=======================================

:csv_rule:`CSV Rule`

- The :term:`DATA DESCRIPTORS`, :term:`GROUP` names, data field :term:`HEADING` s, 
  data field :term:`UNIT` s,
  data field :term:`TYPE` s,  and data :term:`VARIABLE` s in each line
  of the data file shall be separated by a comma (**,**).


- No carriage returns (:ref:`ASCII` character 13) or line feeds (:ref:`ASCII` character 10) are 
  allowed in or between data :term:`VARIABLE` s within a :term:`DATA` row.


.. note::

    A comma (,) is :ref:`ASCII` char 44


.. _ags4_rule_7:

Rule 7 - Field Ordering
=======================================

:csv_rule:`CSV Rule`

- The order of data :term:`FIELD` s in each line within a :term:`GROUP` is 
  defined at the start of each :term:`GROUP` in the :term:`HEADING` row.
- :term:`HEADING` s shall be in the order described in
  the :ref:`ags4_data_dict` (see Section 9).


.. _ags4_rule_8:

Rule 8 - Units
=======================================

:data_rule:`Data Rule`

- Data :term:`VARIABLE` s shall be presented in the units of measurement and 
  type that are described by the appropriate data field :term:`UNIT` and
  data field :term:`TYPE` defined at the start of the :term:`GROUP` within the GROUP :term:`HEADER` rows.


**Example**

.. code-block:: bash
    
    "GROUP","HORN"
    "HEADING","LOCA_ID","HORN_TOP","HORN_BASE","HORN_ORNT","HORN_INCL","HORN_REM","FILE_FSET"
    "UNIT","","m","m","deg","deg","",""
    "TYPE","ID","2DP","2DP","0DP","0DP","X","X"
    
.. _ags4_rule_9:

Rule 9 - Data Dictionary
=======================================

:data_rule:`Data Rule`

- Data :term:`HEADING` and :term:`GROUP` names shall be taken from the :ref:`ags4_data_dict`.
- In cases where there is no suitable entry, a user-defined :term:`GROUP` and/or :term:`HEADING` may be 
  used in accordance with :ref:`ags4_rule_18a`. 
- Any user-defined :term:`HEADING` s shall be included at the end of the :term:`HEADING` row 
  after the standard :term:`HEADING` s in the order defined in the :term:`DICT` group (see :ref:`ags4_rule_18a`). 
    
    
.. _ags4_rule_10:

Rule 10 - Validation
=======================================

:data_rule:`Data Rule`

- :term:`HEADING` s are defined as **KEY**, **REQUIRED** or **OTHER**.
    - **KEY** fields are necessary to uniquely define the data.
    - **REQUIRED** fields are necessary to allow interpretation of the data file.
    - **OTHER** fields are included depending on the scope of the data file and availability of data to be included.

.. _ags4_rule_10a:
    
Rule 10a - KEY
-----------------
- In every :term:`GROUP`, certain :term:`HEADING` s are defined as **KEY**. 
- There shall not be more than one row of data in each :term:`GROUP` with the 
  same combination of KEY field entries.
- KEY fields must appear in each :term:`GROUP`, but may contain null data (see :ref:`ags4_rule_12`).

.. _ags4_rule_10b:
    
Rule 10b - REQUIRED
---------------------
- Some :term:`HEADING` s are marked as **REQUIRED**.
- **REQUIRED** fields must appear in the data :term:`GROUP` s where they 
  are indicated in the :ref:`ags4_data_dict`.
- These fields require data entry and cannot be null (i.e. left blank or empty). 



.. _ags4_rule_10c:
    
Rule 10c - PARENT GROUP
--------------------------------
- Links are made between data rows in :term:`GROUP` s by the :term:`KEY` fields. 
- Every entry made in the :term:`KEY` fields in any :term:`GROUP` must have an equivalent entry in its :term:`PARENT GROUP`. 
- The :term:`PARENT GROUP` must be included within the data file. 
- :term:`GROUP` parentage is defined in Section 7.3. 

.. seealso::

    - :ref:`ags4_rule_note_2`

.. _ags4_rule_11:

Rule 11 - Record Links
=======================================

:data_rule:`Data Rule`

- :term:`HEADING` s defined as a data :term:`TYPE` of :term:`Record Link` (RL) can be used to link data 
  rows to entries in :term:`GROUP` s outside of the defined
  hierarchy (Rule 10c) or DICT group for user defined :term:`GROUP` s.
- A heading of data :term:`TYPE` ':term:`Record Link`' shall comprise:
- The :term:`GROUP` name followed by the KEY FIELDs defining the cross-referenced data row, in the order presented in the AGS4 Data Dictionary (Section 8). 
    
.. _ags4_rule_11a:

Rule 11a - TRAN_DLIM
---------------------------
- Each GROUP/KEY FIELD shall be separated by a delimiter character. 
- This single delimiter character shall be defined in TRAN_DLIM. 
- The default is the ``pipe |`` (:ref:`ASCII` character 124). 
        
.. _ags4_rule_11b:
    
Rule 11b - TRAN_RCON
-------------------------
- A heading of data :term:`TYPE` 'Record Link' can refer to more 
  than one combination of :term:`GROUP` and :term:`KEY FIELD` s.
- The combination shall be separated by a defined concatenation character. 
- This single concatenation character shall be defined in TRAN_RCON. 
- The default being the ``plus sign +`` (:ref:`ASCII` character 43). 
            
.. _ags4_rule_11c:

Rule 11c - Multi Link
-------------------------
- Any heading of data :term:`TYPE` :term:`Record Link` included in a data file shall 
  cross-reference to 
  the :term:`KEY FIELD` s of data rows in the :term:`GROUP` referred to by the heading contents. 


.. _ags4_rule_12:
    
Rule 12 - Blank/Null Data 
=======================================

:csv_rule:`CSV Rule`

- Data does not have to be included against each :term:`HEADING` unless :term:`REQUIRED`. 
- The data :term:`FIELD` can be null
- a null entry is defined as "" (two quotes together, no space etc). 

**Example**

.. code-block:: bash

    "GROUP","HORN"
    "HEADING","LOCA_ID","HORN_TOP","HORN_BASE","HORN_ORNT","HORN_INCL","HORN_REM","FILE_FSET"
    "UNIT","","m","m","deg","deg","",""
    "TYPE","ID","2DP","2DP","0DP","0DP","X","X"
    



.. _ags4_rule_13:

Rule 13 - Mandatory Project Details
=======================================

:data_rule:`Data Rule`

- Each data file shall contain the :term:`PROJ` :term:`GROUP` which shall contain only one data row:
- As a minimum, shall contain data under the headings defined as REQUIRED (:ref:`ags4_rule_10b`). 

.. code-block:: bash
    
    "GROUP","PROJ"
    "HEADING","PROJ_ID","PROJ_NAME","PROJ_LOC","PROJ_CLNT","PROJ_CONT","PROJ_ENG","PROJ_MEMO","FILE_FSET"
    "UNIT","","","","","","","",""
    "TYPE","ID","X","X","X","X","X","X","X"
    "DATA","7845","Trumpington Sewerage","Trumpington","Trumpington District Council","GeoI Ltd","Geo-Knowlege","Example AGS file - assocaited files are not included","FS001"
    




.. _ags4_rule_14:
    
Rule 14 - TRAN GROUP
=======================================

:data_rule:`Data Rule`

- Each data file shall contain the :term:`TRAN GROUP` which shall contain 
    - only one data row
    - and as a minimum, shall contain data under the headings defined as :term:`REQUIRED` (:ref:`ags4_rule_10b`).


.. _ags4_rule_15:
    
Rule 15 - UNIT GROUP
=======================================

:data_rule:`Data Rule`

- Each data file shall contain the :term:`UNIT` :term:`GROUP` to **list all units** used within the data file.
- Every unit of measurement entered in the :term:`UNIT` row of a :term:`GROUP`  or data entered in
  a FIELD where the field TYPE is defined **"PU"** (for example ERES_RUNI, GCHM_UNIT or MOND_UNIT FIELDs) shall
  be listed and defined in the UNIT GROUP.


**Example snippet**

.. code-block:: bash

    "GROUP","UNIT"
    "HEADING","UNIT_UNIT","UNIT_DESC","FILE_FSET"
    "UNIT","","",""
    "TYPE","X","X","X"
    "DATA","m","metre",""
    "DATA","mm","millimetre",""
    "DATA","yyyy-mm-dd","year month day",""
    "DATA","yyyy-mm-ddThh:mm","year month day hours minutes",""
    "DATA","hh:mm:ss","hours minutes seconds",""
    "DATA","%","percentage",""
    "DATA","g/l","grams per litre",""
    "DATA","mg/l","milligrams per litre",""
    "DATA","%vol","percentage volume",""
    "DATA","deg","degrees",""
    "DATA","bar","bar",""
    "DATA","-","No Units",""
    "DATA","degC","degree Celsius",""
    "DATA","l/min","litres per minute",""
    


.. _ags4_rule_16:
    
Rule 16 - Abbreviations
=======================================

:data_rule:`Data Rule`

- Each data file shall contain the :term:`ABBR` :term:`GROUP` when abbreviations have been included in the data file. 
- The abbreviations listed in the :term:`ABBR` :term:`GROUP` shall include definitions for all
  abbreviations entered in a :term:`FIELD` where the data :term:`TYPE` is defined as **"PA"** or
  any abbreviation needing definition used within any other heading data type.


.. _ags4_rule_16a:
    
Rule 16a 
----------------
- Where multiple abbreviations are required to fully codify a :term:`FIELD`
- The abbreviations shall be separated by a defined concatenation character. 
- This single concatenation character shall be defined in `TRAN_RCON`. The default being "+" (:ref:`ASCII` character 43)
- Each abbreviation used in such combinations shall be listed separately in the :term:`ABBR` :term:`GROUP`.
- e.g. **"CP+RC"** must have entries for both **"CP"** and **"RC"** in ABBR GROUP, together with their full definition.


.. _ags4_rule_17:
    
Rule 17 - TYPE
=======================================

:data_rule:`Data Rule`

 - Each data file shall contain the :term:`TYPE` :term:`GROUP` to define the field :term:`TYPE` s used within the data file.
 - Every data type entered in the :term:`TYPE` row of a GROUP shall be listed and defined in the TYPE GROUP. 
 
 .. _ags4_rule_18:
     
Rule 18 - Dictionary
=======================================

:data_rule:`Data Rule`

- Each data file shall contain the :term:`DICT` :term:`GROUP` where non-standard 
  GROUP and HEADING names have been included in the data file.
     
 
.. _ags4_rule_18a:
     
Rule 18a
----------------------------
- The order in which the user-defined :term:`HEADING` s are listed in the DICT GROUP shall define 
  the order in which these HEADINGS are appended to an existing GROUP or appear in a user-defined GROUP.
- This order also defines the sequence in which such HEADINGS are used in a 
  heading of data TYPE :term:`Record Link` (:ref:`ags4_rule_11`).







.. _ags4_rule_19:
    
Rule 19 - Group headings
=======================================

:data_rule:`Data Rule`

 - A :term:`GROUP` name shall: 
     - not be more than **four** characters long
     - and shall consist of uppercase letters and numbers only.

.. code-block:: bash

    # Good
    "GROUP","TBAA"
    "GROUP","TB01"

    # Bad
    "GROUP","BAD"
    "GROUP","abc"
    "GROUP","TB_1"
    "GROUP","TX 3"


.. _ags4_rule_19a:
    
Rule 19a - Heading length
-------------------------------
- A :term:`HEADING` name shall:
    - not be more than **nine** characters long
    - and shall consist of uppercase letters, numbers or the underscore character only. 
    

.. _ags4_rule_19b:
    
Rule 19b - Heading Prefix
-------------------------------

- :term:`HEADING` names shall start with the :term:`GROUP` name followed by an underscore character.
      - e.g. :code:`"NGRP_HED1"`
- Where a :term:`HEADING` refers to an existing :term:`HEADING` within another :term:`GROUP`,
  the :term:`HEADING` name added to the group shall bear the same name.
  - e.g. :code:`"SAMP_REF"` in the :code:`"SAMP"` GROUP
  - or :code:`"CMPG_TESN"` in the :code:`"CMPT"` GROUP.

        
         
         
.. _ags4_rule_20:
    
Rule 20 - Additional files 
============================================

:data_rule:`Data Rule`

- Additional computer files (e.g. digital images) can be included within a data submission. 
- Each such file shall be defined in a FILE GROUP. 
- The additional files shall be transferred in a sub-folder named FILE. 
- This FILE sub-folder shall contain additional sub-folders each named by the FILE_FSET reference. 
- Each FILE_FSET named folder will contain the files listed in the FILE GROUP.

