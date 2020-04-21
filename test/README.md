# Introduction
These test scripts, designed to run with PyTest, should be helpful to developers wanting to ensure that their optimizations do not compromise functionality. Due to the licensing of the MIMIC-III dataset, we cannot provide our original test cases directly; however, this document will guide you through creating your own. We are also working on creating artificial data not derived from MIMIC-III to use as a baseline test case, but this is not part of the current beta release.

# Creating Your Own Test Data
You will need a set of at least three documents containing UMLS concepts. We recommend using a subset of the MIMIC-III notes. Place a parquet file containing these notes in "test/notes/mimic-notes.parquet"; you can use the tool provided in the "extra" directory to produce this file from a CSV file. Process these documents using cTAKES as described in the main readme, and place the resulting XML files in "test/xml".

From there, you will want to run the pipeline, using the optional "--seed 0" argument for all stages and "-n 3" for the generate stage. Place the results in "test/verify/parsed", "test/verify/preprocessed", "test/verify/cluster", and "test/verify/generate", respoectively. While you can do this manually, you can also run the test cases in order and copy the results into their appropriate "verify" directory after each stage.

# Test Cases
Each script tests a particular aspect of the pipeline. These scripts are designed such that each pipeline component can be tested independently, and a failure in one component will not propagate to tests of other components. Do note that pytest may not test components in order when run with no arguments.

Each test runs a particular stage of the pipeline, verifies that it ran, and then checks that the output matches what is expected by comparing to a verification set. Note that if you are using these tests for development that you should run "pip install -e ." in the main directory after making changes but before running the tests, since these scripts utilize the installed version.
