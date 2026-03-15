# Python Scripts

The script `mds2crm.py` transforms the example dataset
([Example_MKG-Kabinettschrank_LIDO_v1.1](../../example-files/Minimum%20Record%20Recommendation/Example_MKG-Kabinettschrank_LIDO_v1.1.xml))
into an RDF representation.

The resulting RDF can be used as the target for mapping efforts.

To generate the RDF, the libraries _rdflib_ and _pydantic-xml_ must be installed (see: [requirements.txt](requirements.txt)). Afterward, the script can be easily executed.

```bash
python mds2crm.py
```

[Example_MKG-Kabinettschrank_LIDO_v1.1](../../example-files/Minimum%20Record%20Recommendation/Example_MKG-Kabinettschrank_LIDO_v1.1.xml) is used as the default input. A file is output in both XML and TTL formats, following the pattern `<date>_<time>_generated_rdf`, in the folder [example-files/Minimum Record Recommendation](../../example-files/Minimum%20Record%20Recommendation).
Input and output can be controlled via the arguments -i --input and -o --output.

```bash
python mds2crm.py -i "<input_file_path>" -o "<output_file_path_without_extension>"
```