.. highlight:: shell

SynthNotes
===============
A generator of synthetic psychiatric notes.

**UPDATES: we are starting migration of SynthNotes 1, and feature development of SynthNotes 2 (DL/LM-based) next week (2/17)**

**NOTE: We have temporarily moved the project development to ORNL-internal Gitlab repository while we are in the process of developing initial publications. Once we have Phases I and II implemented, and once we cleared the project for open sourcing, we will release the content back here, and under the same license.**

======
About
======
The purpose of this library is to generate randomly structured, high-fidelity psychiatric notes for depression and other conditions following the diagnost and note writing standards as recommended by DSM-V and note writing instructionals.

===============
Note Structure
===============
SOAP

==============
Implementation
==============
Patient model - age, gender, demographics, status at home, living conditions, set of variables representing the patient history, and the mental health characteristics/symptoms of the patient, and the variability associated with the age, gender, general demographics. 

Narrator Model - set of variables representing the writing style (grammar, thoroughness, use of abbreviations) and experience of the author. 

***************
Algorithm
***************

=====================
Running the generator
=====================
1. Clone the repo to your local machine.
2. Install the package with ::

    $ pip install -e .
    

3. Modify the settings in the conf.json file file found at synthnotes/resources/conf.json or create your own config file
and pass the file path on the command line through the -c or --config
4. Run the generator with ::

    $ python synthnotes --config path/to/your/config/file



