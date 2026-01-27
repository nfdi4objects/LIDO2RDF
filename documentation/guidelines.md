# Documentation

This mapping deals with mapping LIDO 1.1 to the last official release of CIDOC CRM.


## Modeling:

LIDO-Bemerkungsfeld (objectDescription): P3 > E62 String

LIDO-Bemerkungsfeld (objectDescription) with further specification: E22 Human-Made-Object -> P70 is documented in -> E31 Document -> P190 has symbolic content -> E62 String

Events and activities with E5 / E7 > P2 has type > E55 – embed LIDO terminology here (embed complete URI here: http://terminology.lido-schema.org/lido00007)
If more specific events are available in CRM, use these (E12 Production, E11 Modification), then without E55.
There are not always event IDs for the respective data records. If one is available, use it. If none is available, one must be generated, see [https://lido-schema.org/schema/v1.1/lido-v1.1.html#event](https://lido-schema.org/schema/v1.1/lido-v1.1.html#event).

## Usage of blank notes

## Usage of short cuts

## Useful links:

[CIDOC CRM Last official release](https://cidoc-crm.org/get-last-official-release)

[CRM Compatible Models](https://cidoc-crm.org/collaborations)

[LIDO Primer](https://lido-schema.org/documents/primer/latest/lido-primer.html)

For CIDOC CRM also see [CIDOC-CRM in RDF Application Profile. Guidelines how to use CIDOC-CRM in RDF for interoperability](https://nfdi4objects.github.io/crm-rdf-ap/) by Jakob Voß.
