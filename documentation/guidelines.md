# Documentation

This mapping deals with mapping LIDO 1.1 to the last official release of CIDOC CR (7.1.3).


## Modeling:

LIDO-Bemerkungsfeld (objectDescription): P3 > E62 String

LIDO-Bemerkungsfeld (objectDescription) with further specification: E22 Human-Made-Object -> P70 is documented in -> E31 Document -> P190 has symbolic content -> E62 String

Authority files for E39_Actor, E53_Place ec. via  P1_is-identified-by

Events and activities with E5 / E7 > P2_has_type > E55 – embed LIDO terminology here (embed complete URI here: http://terminology.lido-schema.org/lido00007)
If more specific events are available in CRM, use these (E12 Production, E11 Modification), then without E55.
There are not always event IDs for the respective data records. If one is available, use it. If none is available, one must be generated, see [https://lido-schema.org/schema/v1.1/lido-v1.1.html#event](https://lido-schema.org/schema/v1.1/lido-v1.1.html#event).

Literals can be modeled via P3 using “note” or “rdfs:label”: the information hidden behind the URI should be resolved into a human-readable form.
For the mapping the usage'rdfs:label' is recommended.

Actor roles in LIDO > CRM: focussing on th main activities in CRM

## Usage of blank notes

## Usage of short cuts

## Useful links:

[CIDOC CRM Last official release](https://cidoc-crm.org/get-last-official-release)

[CRM Compatible Models](https://cidoc-crm.org/collaborations)

[LIDO Primer](https://lido-schema.org/documents/primer/latest/lido-primer.html)

For CIDOC CRM also see [CIDOC-CRM in RDF Application Profile. Guidelines how to use CIDOC-CRM in RDF for interoperability](https://nfdi4objects.github.io/crm-rdf-ap/) by Jakob Voß.

[Linked Art Model](https://linked.art/model/)
