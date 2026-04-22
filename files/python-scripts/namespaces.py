from rdflib import URIRef
from rdflib.namespace import DefinedNamespace, Namespace


class CRM(DefinedNamespace):
    _NS = Namespace('http://www.cidoc-crm.org/cidoc-crm/')

    # Classes
    E7_Activity: URIRef
    E5_Event: URIRef
    E8_Acquisition: URIRef
    E12_Production: URIRef
    E15_Identifier_Assignment: URIRef
    E16_Measurement: URIRef
    E17_Type_Assignment: URIRef
    E18_Physical_Thing: URIRef
    E22_Human_Made_Object: URIRef = URIRef('http://www.cidoc-crm.org/cidoc-crm/E22_Human-Made_Object')
    E28_Conceptual_Object: URIRef
    E33_Linguistic_Object: URIRef
    E35_Title: URIRef
    E42_Identifier: URIRef
    E52_Time_Span: URIRef = URIRef('http://www.cidoc-crm.org/cidoc-crm/E52_Time-Span')
    E53_Place: URIRef
    E54_Dimension: URIRef
    E55_Type: URIRef
    E56_Language: URIRef
    E58_Measurement_Unit: URIRef
    E74_Group: URIRef
    E78_Curated_Holding: URIRef

    # Properties
    P1_is_identified_by: URIRef
    P1i_identifies: URIRef
    P2_has_type: URIRef
    P3_has_note: URIRef
    P3_1_has_type: URIRef = URIRef('http://www.cidoc-crm.org/cidoc-crm/P3.1_has_type')
    P4_has_time_span: URIRef = URIRef('http://www.cidoc-crm.org/cidoc-crm/P4_has_time-span')
    P7_took_place_at: URIRef
    P14_carried_out_by: URIRef
    P14_1_in_the_role_of: URIRef = URIRef('http://www.cidoc-crm.org/cidoc-crm/P14.1_in_the_role_of')
    P15_was_influenced_by: URIRef
    P15i_influenced: URIRef
    P22_transferred_title_to: URIRef
    P22i_acquired_title_through: URIRef
    P23_transferred_title_from: URIRef
    P23i_surrendered_title_through: URIRef
    P24_transferred_title_of: URIRef
    P24i_changed_ownership_through: URIRef
    P32_used_general_technique: URIRef
    P37_assigned: URIRef
    P39i_was_measured_by: URIRef
    P40_observed_dimension: URIRef
    P41_classified: URIRef
    P41i_was_classified_by: URIRef
    P42_assigned: URIRef
    P42i_was_assigned_by: URIRef
    P43_has_dimension: URIRef
    P45_consists_of: URIRef
    P46_is_composed_of: URIRef
    P46i_forms_part_of: URIRef
    P52_has_current_owner: URIRef
    P54_has_current_permanent_location: URIRef
    P62_depicts: URIRef
    P67i_is_referred_to_by: URIRef
    P72_has_language: URIRef
    P72i_is_language_of: URIRef
    P82a_begin_of_the_begin: URIRef
    P82b_end_of_the_end: URIRef
    P90_has_value: URIRef
    P91_has_unit: URIRef
    P102_has_title: URIRef
    P102i_is_title_of: URIRef
    P108_has_produced: URIRef
    P108i_was_produced_by: URIRef
    P126_employed: URIRef
    P140i_was_attributed_by: URIRef
    P190_has_symbolic_content: URIRef

    # Property Classes
    PC0_Typed_CRM_Property: URIRef
    PC3_has_note: URIRef
    PC14_carried_out_by: URIRef

    # Property Class Properties
    P01_has_domain: URIRef
    P01i_is_domain_of: URIRef
    P02_has_range: URIRef
    P02i_is_range_of: URIRef
    P03_has_range_literal: URIRef
    P04_represents: URIRef


class LRMOO(DefinedNamespace):
    _NS = Namespace('http://iflastandards.info/ns/lrm/lrmoo/')

    # Classes
    F3_Manifestation: URIRef


class SCI(DefinedNamespace):
    _NS = Namespace('http://www.cidoc-crm.org/extensions/crmsci/')

    # Classes
    S19_Encounter_Event: URIRef

    # Properties
    O19_encountered_object: URIRef
    O19i_was_object_encountered_through: URIRef
    O21_encountered_at: URIRef
    O21i_witnessed_encounter: URIRef
