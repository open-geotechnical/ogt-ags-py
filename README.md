ogt-ags-py
============================

Experimental library and tools for validating and converting AGS dataformat files, written in Python

- Docs at https://open-geotechnical.github.io/ogt-ags-py/
- Code at https://github.com/open-geotechnical/ogt-ags-py

Command line
===========================
```bash
# convert ags file to json
./ogt-cli.py convert -b -o -f json ./my_project.ags

# convert ags file to yaml
./ogt-cli.py convert -b -o -f  yaml ./my_project.ags

```



Requirements
===========================

The Installer is not started yet, so in the meantime the following
python2.7+ packages need installing, if you need them:

- openpyxl
- pyyaml 
- geojson
- bng_latlon

eg

```bash
pip install geojson
```

TODO
===========

- [x] convert to `json` - needs testing
- [ ] convert to `geojson` - started
- [x] convert to `yaml` - needs testing
- [ ] convert to `xlsx` (Excel) - started 
- [ ] convert to `ods` (LibreOffice) 
- [ ] validator - started
- [ ] gui - started
- [ ] server 
- [ ] packaging


