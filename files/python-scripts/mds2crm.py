import argparse
import logging
import os
from datetime import datetime
from itertools import chain

from rdflib import Graph, BNode, Literal, RDF, URIRef, XSD, SDO, DCTERMS, DCMITYPE
from rdflib.term import Identifier

from lido_pydantic import Lido, is_url
from namespaces import CRM

type Triple = tuple[Identifier, str | Identifier, str | Identifier]


def object_title(lido: Lido, subject: Identifier) -> list[Triple]:
    triplets: list[Triple] = []
    titles = lido.descriptiveMetadata.objectIdentificationWrap.titleWrap.titleSet
    for title in titles:
        node = BNode(title.get_hash())
        triplets.append((subject, CRM.P102_has_title, node))
        triplets.append((node, RDF.type, CRM.E35_Title))
        if title.type is not None and is_url(title.type):
            triplets.append((node, CRM.P2_has_type, URIRef(title.type)))
        if title.pref is not None and is_url(title.pref):
            triplets.append((node, CRM.P2_has_type, URIRef(title.pref)))
        for appellation in title.appellationValue:
            triplets.append((node, CRM.P190_has_symbolic_content, Literal(appellation.text, lang=appellation.lang)))

    if len(triplets) == 0:
        logging.error(f"{lido.get_record_id()}: No object title found; an object title is mandatory.")

    return triplets


def object_type(lido: Lido, subject: Identifier) -> list[Triple]:
    triplets: list[Triple] = []

    for object_work_type in lido.descriptiveMetadata.objectClassificationWrap.objectWorkTypeWrap.objectWorkType:
        uri = object_work_type.get_concept_uri()
        if uri is not None:
            triplets.append((subject, CRM.P2_has_type, URIRef(uri)))

    if len(triplets) == 0:
        logging.error(f"{lido.get_record_id()}: No object type found; an object type is mandatory.")

    return triplets


def classifications(lido: Lido, subject: Identifier) -> list[Triple]:
    triplets: list[Triple] = []

    if lido.descriptiveMetadata.objectClassificationWrap.classificationWrap is None:
        return triplets

    for classification in lido.descriptiveMetadata.objectClassificationWrap.classificationWrap.classification:
        uri = classification.get_concept_uri()
        if uri is not None:
            """Legacy Lido 1.0 handling, exclude material from being mapped as "has_type". 
            Mapping as "consists_of" is done in material function."""
            if classification.type in ['http://terminology.lido-schema.org/lido00132',
                                       'http://terminology.lido-schema.org/lido00513']:
                continue

            triplets.append((subject, CRM.P2_has_type, URIRef(uri)))

    if len(triplets) == 0:
        logging.warning(f"{lido.get_record_id()}: No classification found; a classification is recommended.")

    return triplets


def inventory_number(lido: Lido, subject: Identifier) -> list[Triple]:
    triplets: list[Triple] = []

    for repository_set in lido.descriptiveMetadata.objectIdentificationWrap.repositoryWrap.repositorySet:
        for work_id in repository_set.workID:
            if work_id.type != work_id.INVENTORY_NUMBER_URI:
                continue

            node = BNode(work_id.get_hash())
            triplets.append((subject, CRM.P1_is_identified_by, node))
            triplets.append((node, RDF.type, CRM.E42_Identifier))
            triplets.append((node, CRM.P190_has_symbolic_content, Literal(work_id.text)))
            if work_id.type is not None:
                triplets.append((node, CRM.P2_has_type, URIRef(work_id.type)))

    if len(triplets) == 0:
        logging.error(f"{lido.get_record_id()}: No inventory number found; an inventory number is mandatory.")

    return triplets


def object_description(lido: Lido, subject: Identifier) -> list[Triple]:
    triplets: list[Triple] = []
    for object_description_set in lido.descriptiveMetadata.objectIdentificationWrap.objectDescriptionWrap.objectDescriptionSet:
        for descriptive_note_value in object_description_set.descriptiveNoteValue:
            triplets.append(
                (subject, CRM.P3_has_note, Literal(descriptive_note_value.text, lang=descriptive_note_value.lang)))

    if len(triplets) == 0:
        logging.warning(f"{lido.get_record_id()}: No object description found, an object description is recommended.")

    return triplets


def measurement(lido: Lido, subject: Identifier) -> list[Triple]:
    triplets: list[Triple] = []

    for object_measurement_set in lido.descriptiveMetadata.objectIdentificationWrap.objectMeasurementsWrap.objectMeasurementsSet:
        if object_measurement_set.objectMeasurements is None:
            continue
        for measurements_set in object_measurement_set.objectMeasurements.measurementsSet:
            node = BNode(measurements_set.get_hash())
            value = measurements_set.measurementValue.text

            datatype = XSD.string
            if type(value) is float:
                datatype = XSD.decimal
            if type(value) is int:
                datatype = XSD.integer

            triplets.append((subject, CRM.P43_has_dimension, node))
            triplets.append((node, RDF.type, CRM.E54_Dimension))
            triplets.append((node, CRM.P90_has_value, Literal(value, datatype=datatype)))
            triplets.append((node, CRM.P91_has_unit, URIRef(str(measurements_set.measurementUnit.get_concept_uri()))))
            triplets.append((node, CRM.P2_has_type, URIRef(str(measurements_set.measurementType.get_concept_uri()))))

    if len(triplets) == 0:
        logging.warning(f"{lido.get_record_id()}: No measurements found for, measurements are recommended.")

    return triplets


def material(lido: Lido, subject: Identifier) -> list[Triple]:
    triplets: list[Triple] = []

    if lido.descriptiveMetadata.objectIdentificationWrap.objectMaterialsTechWrap is None:
        return triplets

    for object_materials_tech_set in lido.descriptiveMetadata.objectIdentificationWrap.objectMaterialsTechWrap.objectMaterialsTechSet:
        for materials_tech in object_materials_tech_set.materialsTech:
            for term_material_tech in materials_tech.termMaterialsTech:
                if term_material_tech.type in ['http://terminology.lido-schema.org/lido00132',
                                               'http://terminology.lido-schema.org/lido00513']:
                    triplets.append((subject, CRM.P45_consists_of, URIRef(str(term_material_tech.get_concept_uri()))))

    if lido.descriptiveMetadata.objectClassificationWrap.classificationWrap is not None:
        for classification in lido.descriptiveMetadata.objectClassificationWrap.classificationWrap.classification:
            uri = classification.get_concept_uri()
            if uri is not None and classification.type in ['http://terminology.lido-schema.org/lido00132',
                                                           'http://terminology.lido-schema.org/lido00513']:
                triplets.append((subject, CRM.P45_consists_of, URIRef(uri)))

    if len(triplets) == 0:
        logging.warning(f"{lido.get_record_id()}: No object material found, an object material is recommended.")

    return triplets


def technic(lido: Lido, subject: Identifier) -> list[Triple]:
    triplets: list[Triple] = []

    if lido.descriptiveMetadata.objectIdentificationWrap.objectMaterialsTechWrap is None:
        return triplets

    for object_materials_tech_set in lido.descriptiveMetadata.objectIdentificationWrap.objectMaterialsTechWrap.objectMaterialsTechSet:
        for materials_tech in object_materials_tech_set.materialsTech:
            for term_material_tech in materials_tech.termMaterialsTech:
                if term_material_tech.type == 'http://terminology.lido-schema.org/lido00131':
                    triplets.append((subject, CRM.P2_has_type, URIRef(str(term_material_tech.get_concept_uri()))))

    if len(triplets) == 0:
        logging.warning(f"{lido.get_record_id()}: No object technic found, technic is recommended.")

    return triplets


def event(lido: Lido, subject: Identifier) -> list[Triple]:
    triplets: list[Triple] = []

    for event_set in lido.descriptiveMetadata.eventWrap.eventSet:
        if event_set.event is None:
            continue

        event_node = BNode(event_set.event.get_hash())

        # production
        if event_set.event.eventType.get_concept_uri() in ['http://terminology.lido-schema.org/lido00007']:
            triplets.append((subject, CRM.P108i_was_produced_by, event_node))
            triplets.append((event_node, RDF.type, CRM.E12_Production))

            if event_set.event.eventDate is not None and event_set.event.eventDate.date is not None:
                date_node = BNode(event_set.event.eventDate.date.get_hash())
                triplets.append((event_node, CRM.P4_has_time_span, date_node))
                triplets.append((date_node, RDF.type, CRM.E52_Time_Span))
                if event_set.event.eventDate.date.earliestDate is not None and event_set.event.eventDate.date.earliestDate.text is not None:
                    triplets.append((date_node, CRM.P82a_begin_of_the_begin,
                                     Literal(event_set.event.eventDate.date.earliestDate.text)))
                if event_set.event.eventDate.date.latestDate is not None and event_set.event.eventDate.date.latestDate.text is not None:
                    triplets.append((date_node, CRM.P82b_end_of_the_end,
                                     Literal(event_set.event.eventDate.date.latestDate.text)))

            for event_actor in event_set.event.eventActor:
                if any(event_actor.actorInRole.actor.actorID):
                    actor_id = event_actor.actorInRole.actor.actorID[0]
                    if any(event_actor.actorInRole.roleActor):
                        role_actor_uri = event_actor.actorInRole.roleActor[0].get_concept_uri()
                        actor_in_role = BNode(event_actor.actorInRole.get_hash())
                        triplets.append((actor_in_role, RDF.type, CRM.PC14_carried_out_by))
                        triplets.append((actor_in_role, CRM.P02_has_range, URIRef(actor_id.text.strip())))
                        triplets.append((actor_in_role, CRM.P14_1_in_the_role_of, URIRef(role_actor_uri)))
                        triplets.append((event_node, CRM.P01i_is_domain_of, actor_in_role))
                    else:
                        triplets.append((event_node, CRM.P14_carried_out_by, URIRef(actor_id.text.strip())))

            for event_place in event_set.event.eventPlace:
                if any(event_place.place.placeID):
                    place_id = event_place.place.placeID[0]
                    triplets.append((event_node, CRM.P7_took_place_at, URIRef(place_id.text.strip())))

            for event_material_tech in event_set.event.eventMaterialsTech:
                for material_tech in event_material_tech.materialsTech:
                    for term_material_tech in material_tech.termMaterialsTech:
                        if term_material_tech.type == 'http://terminology.lido-schema.org/lido00132':
                            triplets.append(
                                (event_node, CRM.P126_employed, URIRef(str(term_material_tech.get_concept_uri()))))
                        if term_material_tech.type == 'http://terminology.lido-schema.org/lido00131':
                            triplets.append((event_node, CRM.P32_used_general_technique,
                                             URIRef(str(term_material_tech.get_concept_uri()))))

    if len(triplets) == 0:
        logging.error(f"{lido.get_record_id()}: No event found, at least one event is mandatory.")

    return triplets


def subject_keyword(lido: Lido, subject: Identifier) -> list[Triple]:
    """
    E22 Human-Made Object -> P128 carries -> E73 Information Object (E36 Visual Item) -> P129 is about / P138 represents -> Something

    :param lido:
    :param subject:
    :return:
    """
    triplets: list[Triple] = []

    for subject_set in lido.descriptiveMetadata.objectRelationWrap.subjectWrap.subjectSet:
        if subject_set.subject is None:
            continue

        # description/iconclass
        if subject_set.subject.type in ['http://terminology.lido-schema.org/lido00745',
                                        'http://terminology.lido-schema.org/lido00525']:
            for subject_concept in subject_set.subject.subjectConcept:
                triplets.append((subject, CRM.P62_depicts, URIRef(str(subject_concept.get_concept_uri()))))

        # identification
        if subject_set.subject.type == 'http://terminology.lido-schema.org/lido00136':
            for subject_concept in subject_set.subject.subjectConcept:
                triplets.append((subject, CRM.P2_has_type, URIRef(str(subject_concept.get_concept_uri()))))

        # interpretation
        if subject_set.subject.type == 'http://terminology.lido-schema.org/lido00524':
            node = BNode(subject_set.get_hash())
            triplets.append((subject, CRM.P128_carries, node))
            triplets.append((node, RDF.type, CRM.E36_Visual_Item))
            for subject_concept in subject_set.subject.subjectConcept:
                triplets.append((node, CRM.P129_is_about, URIRef(str(subject_concept.get_concept_uri()))))

    if len(triplets) == 0:
        logging.warning(f"{lido.get_record_id()}: No subject keyword found, a subject keyword is recommended.")

    return triplets


def media(lido: Lido, subject: Identifier, as_dc: bool = False) -> list[Triple]:
    """
    E22->E65->D1
    :param lido:
    :param subject:
    :return:
    """
    triplets: list[Triple] = []

    for resource_set in lido.administrativeMetadata.resourceWrap.resourceSet:
        node = BNode(resource_set.get_hash())

        if as_dc:
            triplets.append((node, RDF.type, DCMITYPE.Image))
            triplets.append((node, DCTERMS.subject, subject))
        else:
            triplets.append((subject, SDO.image, node))
            triplets.append((node, RDF.type, SDO.ImageObject))

        # media link
        for resource_representation in resource_set.resourceRepresentation:
            triplets.append((node, DCTERMS.identifier if as_dc else SDO.contentUrl,
                             URIRef(resource_representation.linkResource.text.encoded_string())))

        # media description
        for resource_description in resource_set.resourceDescription:
            triplets.append((node, DCTERMS.description if as_dc else SDO.description,
                             Literal(resource_description.text.strip())))

        for rights_resource in resource_set.rightsResource:

            # rights holder
            for rights_holder in rights_resource.rightsHolder:
                if any(rights_holder.legalBodyID):
                    for legal_body_id in rights_holder.legalBodyID:
                        triplets.append((node, DCTERMS.rightsHolder if as_dc else SDO.copyrightHolder,
                                         URIRef(legal_body_id.text.strip())))
                else:
                    for legal_body_name in rights_holder.legalBodyName:
                        for appellation_value in legal_body_name.appellationValue:
                            triplets.append((node, DCTERMS.rightsHolder if as_dc else SDO.copyrightHolder,
                                             Literal(appellation_value.text.strip())))

            # license
            for rights_type in rights_resource.rightsType:
                if rights_type.get_concept_uri() is not None:
                    triplets.append(
                        (node, DCTERMS.license if as_dc else SDO.license, URIRef(rights_type.get_concept_uri())))

    if len(triplets) == 0:
        logging.error(f"{lido.get_record_id()}: No media file found, a media file is mandatory.")

    return triplets


def mds_lido_2_rdf(lido: Lido, subject: URIRef = None) -> Graph:
    if subject is None:
        subject = BNode(lido.get_hash())

    g = Graph()
    g.bind('crm', CRM)
    g.add((subject, RDF.type, CRM.E22_Human_Made_Object))

    for triple in chain(
            object_title(lido, subject),
            object_type(lido, subject),
            classifications(lido, subject),
            inventory_number(lido, subject),
            object_description(lido, subject),
            material(lido, subject),
            technic(lido, subject),
            measurement(lido, subject),
            event(lido, subject),
            subject_keyword(lido, subject),
            media(lido, subject)):
        g.add(triple)

    return g


if __name__ == '__main__':
    input_file = '../../example-files/Minimum Record Recommendation/Example_MKG-Kabinettschrank_LIDO_v1.1.xml'
    output_file = f'../../example-files/Minimum Record Recommendation/{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}_generated_rdf'

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input file', default=input_file)
    parser.add_argument('-o', '--output', help='Output file (without extension)', default=output_file)

    args = parser.parse_args()

    with open(args.input) as f:
        xml = f.read()
        lido = Lido.from_xml(xml.encode('utf-8'))

        g = mds_lido_2_rdf(lido)

        g.serialize(f'{os.path.splitext(args.output)[0]}.ttl', format='turtle')
        g.serialize(f'{os.path.splitext(args.output)[0]}.xml', format='pretty-xml', encoding='utf-8')
