# ledestool
Tool for converting and manipulating LEDES 1998B and 1998BI files.

## Introduction
This tool is designed, by default, to convert a [LEDES 1998B](https://ledes.org/ledes-98b-format/) formatted file to [LEDES 1998BI](https://ledes.org/ledes-98bi-format/) formatted file.  Essentially, the file is extended to include all 51 fields of the 1998BI format, without any data in the additional fields.

Various profiles may be defined that will allow manipulation of the converted file.  Manipulation may include removing, replacing, copying, splitting, remapping, and/or case transformations.  Profiles should be defined in a `profiles.yaml` file in the same folder as the python file or executable.  A sample profile file is included that explains the various transformations.

Optionally, you may manipulate a LEDES 1998B file without converting to 1998BI.

## Instructions
All files to be converted should be placed in a common folder.  Files may have any extension, and may also be placed in subdirectories within the common folder.  

To use the tool, just launch it and select your folder using the `Browse` button.  Then select your profile (either `Default` or a custom one you defined in the `profiles.yaml` file).  You may also select `AutoSelect`, in which case the tool attempts to detect the right profile to use based on the `autoselect` key in the profile (if defined).  See the sample `profiles.yaml` for details.

Once the profile is selected, click on `Convert`.  Your converted files will appear in the same folders as to original files.  The converted file will have a `.converted` extension prior to the original extension of the file (e.g. `invoice.ledes` will become `invoice.converted.ledes`).

## Profiles
Each profile should be a separate item in the `profiles.yaml` file.  The general format is below:

```
ProfileName:
 output_format:    # either 1998B or 1998BI
 transformations:
  - FIELD_NAME_OR_NUMBER:
    value: "XXX"                  # value to set the field to
    source: FIELD_NAME_OR_NUMBER  # copy contents from source to this field
    oldtext: "XXX"                # text to remove or replace
    newtext: "XXX"                # text to replace the oldtext with
    upper: true                   # convert to upper-case
    lower: true                   # convert to lower-case
    split: ", "                   # divide into separate using delimiter
    index: PORTION_NUM            # portion to keep when using split (0 by default)
    map: {'X': 'Y', 'A': 'B'}     # map value X to Y, A to B, etc
  - NEXT_FIELD:
    ...
 autoselect:
  FIELD_NAME_OR_NUMBER: XXXXX       # match if specified field contains XXXXX
  FIELD_NAME_OR_NUMBER: ["X","Y"]   # match if specified field contains X or Y
  ...
NextProfileName:
 ...
``` 

## Author / Acknowledgments
This tool was created by @karlrees, copyright 2020.
