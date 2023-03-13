## NER_eval
A effecient tool for extract dicom meta data from files.

This tool offers:
- convert dicom to png (if pixel array is 2D) / mp4 (3D)
- extract all meta data (dicom header) to a single csv file
- examize corrupted files and files with missing values

## Installation
```bash
pip install -r requirements.txt
pip install dcm-parser
```


## Usage

**ONE line for everything!**

```python
from dcm_parser import batch_extraction

batch_extraction(source_dir=[YOUR_SOURCE_DIR], dest_dir=[YOUR_TARGET_DIR], save_img=True)

```

## How to cite this work

If you find this git repo useful, please consider citing it using the snippet below:
```bibtex
@misc{ner_eval,
    author={Le Peng},
    title={DCM-parser: A Lightning DICOM Parser},
    howpublished={\url{https://github.com/PL97/DICOM_Parser}},
    year={2022}
}