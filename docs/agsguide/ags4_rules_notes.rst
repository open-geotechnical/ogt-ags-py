==============================
AGS4 - Notes on the Rules
==============================


A fundamental consideration in developing the Rules has been that potential users of the AGS Format
should be able to use standard software tools to produce the data files.

The spreadsheet is the most basic tool for the task and the revised Rules presented in AGS4 simplify
the process of creating data from spreadsheet software. Likewise, data files produced according to the
Rules can be read directly by spreadsheet software.

Although the Rules make it possible for users to manipulate data files using spreadsheets alone, it is to
be expected that more specific software will be used to automate the reading and writing of data files.
These software systems may range from simple data entry and edit programs through to complete
database systems with AGS Format data import and export capability.

Another fundamental point is that the resulting data file has been designed to be easy to read with
minimal computer software. The data files do not replace the printed reports to which they relate,
however, the layout does allow data items to be readily identified should the need arise.

The following notes explain some points of detail in the Rules.


.. _ags4_rule_note_1:

Note i - ASCII 'CSV' Files
---------------------------------

The :ref:`ags4_rules` define :ref:`ASCII` data files of a type commonly referred to as Comma Separated Value (:ref:`CSV`).
The data items are separated by commas and surrounded by quotes (").

It should be noted that not all software is able to read and write :ref:`CSV` files to the requirements of the
AGS Format.


.. _ags4_rule_note_2:

Note ii - HEADINGs, KEY and REQUIRED Fields
-------------------------------------------------

The :term:`HEADING` s should be seen as the equivalent of a field name within a database. However, the
term :term:`HEADING` is used within the rules to highlight that this document defines a data transfer format
and not a database schema.

:term:`KEY FIELD` s are important for maintaining data integrity. Without this, the receiving software may not
be able to create the inter-relationships within the data in a meaningful way. For the purpose of
creating data files, this means that data entered into the combination of :term:`KEY FIELD` s must be unique
in each :term:`GROUP` and that the corresponding entries are made in the :term:`PARENT GROUP` where required
by :ref:`ags4_rule_10c`.

:term:`REQUIRED` Fields (:ref:`ags4_rule_10b`) are critical to interpreting the data file. Without data in these fields the
user or receiving software may not be able to access the data or process the information within.
Note that there is no requirement to include all :term:`HEADING` s in a :term:`GROUP`. The general approach
should be to only include the :term:`HEADING` s for which data is required or provided (:ref:`ags4_rule_10`). This is
subject to meeting the requirement to include all :term:`KEY` and
:term:`REQUIRED` fields (:ref:`ags4_rule_10a` and :ref:`ags4_rule_10b`).


.. _ags4_rule_note_3:

Note iii - Units and Data Types
-------------------------------------------------

Suggested units of measurement and data types for each of the HEADINGs are given in the Data
Dictionary (Section 8). These represent the typical units of measurement that are used in the UK.
They will either be the appropriate SI units or the unit defined by the particular Eurocode or British
Standard relating to the measurement data under that specific HEADING.

It is recognised that situations will occur where neither the SI unit nor the suggested unit of
measurement are appropriate. In these cases, the unit of measurement and/or data TYPE for the
results presented may be changed from the one shown in this document and the results presented
according to the revised data UNIT / data TYPE.

All entries in the UNIT row must be defined in the UNIT GROUP (:ref:`ags4_rule_15`). All entries in the TYPE row
must be fully defined in the TYPE GROUP (:ref:`ags4_rule_17`).


.. _ags4_rule_note_4:

Note iv - Sample Referencing
------------------------------------------

The SAMP Group has 5 KEY FIELDs which comprise 4 descriptive FIELDs (LOCA_ID, SAMP_TOP,
SAMP_TYPE, SAMP_REF) and a single non descriptive ID (SAMP_ID).

If descriptive information regarding the sample is not to be disclosed to the data receiver (for example
a laboratory), then the single SAMP_ID field is used and the remaining 4 KEY FIELDs are transmitted
as null values. If no such requirement exists then the 4 descriptive fields can be used and the
SAMP_ID can either be transmitted or contain a null value.

This approach is extended to all GROUPs that are descended from SAMP in the Group Hierarchy
(Section 7.3). Laboratory test results may, therefore, be reported using the single or descriptive Key
Field options to reference the parent sample depending on what reference system was given to the
laboratory.

Samples that have a null LOCA_ID in the SAMP Group are required to have a null parent entry in the
LOCA group when submitted to comply with :ref:`ags4_rule_10c`.

.. note::

    Note: where these options for sample data exchange are deployed, there may be requirements for
    additional data acceptance protocols for both data receivers and data producers to ensure that data
    containing only partial :term:`KEY FIELD` information can be successfully recombined if data is to be round-
    tripped.
