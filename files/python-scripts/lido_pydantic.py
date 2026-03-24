import hashlib
from typing import ClassVar

from pydantic import HttpUrl, Field, field_validator, model_validator
from pydantic_xml import BaseXmlModel, element, attr

NSMAP = {"lido": 'http://www.lido-schema.org', 'xml': 'http://www.w3.org/XML/1998/namespace',
         'skos': 'http://www.w3.org/2004/02/skos/core#', 'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
         'owl': 'http://www.w3.org/2002/07/owl#'}


def is_url(v) -> bool:
    try:
        HttpUrl(v)
    except ValueError:
        return False
    return True


class LidoRecord(BaseXmlModel, ns='lido', nsmap=NSMAP, skip_empty=True, search_mode='ordered'):
    def get_hash(self, algorithm: str = 'md5', prefix: str = 'L'):
        hasher = hashlib.new(algorithm)
        hasher.update(self.to_xml())
        return f'{prefix}{hasher.hexdigest()}'


class PrefMixin(LidoRecord):
    class Meta:
        abstract = True

    PREFERRED_LABEL_URI: ClassVar[str] = 'http://terminology.lido-schema.org/lido00169'
    ALTERNATIVE_LABEL_URI: ClassVar[str] = 'http://terminology.lido-schema.org/lido00170'

    _PREF_MAP: ClassVar[dict[str, str]] = {
        'preferred': PREFERRED_LABEL_URI,
        'alternative': ALTERNATIVE_LABEL_URI
    }

    pref: str | None = attr('pref', 'lido', default=None)

    @field_validator('pref', mode='after')
    @classmethod
    def map_pref(cls, pref: str):
        return cls._PREF_MAP.get(pref.lower(), pref)


class IdentifierComplexType(PrefMixin):
    URI_TYPE: ClassVar[str] = 'http://terminology.lido-schema.org/lido00099'
    LOCAL_ID_TYPE: ClassVar[str] = 'http://terminology.lido-schema.org/lido00100'
    IRI_TYPE: ClassVar[str] = 'http://terminology.lido-schema.org/lido00501'

    _IDENTIFIER_TYPE_MAP: ClassVar[dict[str, str]] = {
        'http://terminology.lido-schema.org/identifier_type/uri': URI_TYPE,
        'uri': URI_TYPE,
        'url': URI_TYPE,
        'http://terminology.lido-schema.org/identifier_type/local_identifier': LOCAL_ID_TYPE,
        'localID': LOCAL_ID_TYPE,
        'http://terminology.lido-schema.org/identifier_type/iri': IRI_TYPE,
        'iri': IRI_TYPE,
    }

    text: str | None = None  # FIXME
    pref: str | None = attr('pref', 'lido', default=None)
    type: str = attr('type', 'lido')
    source: str | None = attr('source', 'lido', default=None)
    encodinganalog: str | None = attr('encodinganalog', 'lido', default=None)
    label: str | None = attr('label', 'lido', default=None)

    @field_validator('type', mode='before')
    @classmethod
    def map_identifier_type(cls, identifier: str):
        return cls._IDENTIFIER_TYPE_MAP.get(identifier.lower(), identifier)


class TermComplexType(PrefMixin):
    text: str | None = None  # FIXME
    pref: str | None = attr('pref', 'lido', default=None)
    addedSearchTerm: str | None = attr('addedSearchTerm', 'lido', default=None)
    lang: str | None = attr('lang', ns='xml', default=None)
    encodinganalog: str | None = attr('encodinganalog', 'lido', default=None)
    label: str | None = attr('label', 'lido', default=None)


class PrefLabel(BaseXmlModel, ns='skos', nsmap=NSMAP, skip_empty=True):
    text: str
    lang: str | None = attr('lang', ns='xml', default=None)


class ExactMatch(BaseXmlModel, ns='skos', nsmap=NSMAP, skip_empty=True):
    text: HttpUrl = None
    resource: HttpUrl | None = attr('resource', 'rdf', default=None)


class Notation(BaseXmlModel, ns='skos', nsmap=NSMAP, skip_empty=True):
    text: str


class Concept(BaseXmlModel, ns='skos', nsmap=NSMAP, skip_empty=True):
    about: HttpUrl = attr('about', 'rdf')
    prefLabel: list[PrefLabel] = element('prefLabel', default=[])
    exactMatch: list[ExactMatch] = element('exactMatch', default=[])
    notation: list[Notation] = element('notation', default=[])


class ConceptID(IdentifierComplexType):
    pass


class Term(TermComplexType):
    pass


class ConceptComplexType(LidoRecord):
    concept: Concept | None = element('Concept', ns='skos', default=None)
    conceptID: list[ConceptID] = element('conceptID', default=[])
    term: list[Term] = element('term', default=[])

    def get_concept_uri(self) -> str | None:
        if self.concept is not None:
            return str(self.concept.about)

        for concept_id in self.conceptID:
            if not is_url(concept_id.text):
                continue

            if len(self.conceptID) == 1:
                return concept_id.text
            elif concept_id.pref == concept_id.PREFERRED_LABEL_URI:
                return concept_id.text

        return None


class ObjectWorkType(ConceptComplexType):
    type: str | None = attr('type', 'lido', default=None)
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class ObjectWorkTypeWrap(LidoRecord):
    objectWorkType: list[ObjectWorkType] = element('objectWorkType')


class TermMaterialsTech(ConceptComplexType):
    MATERIAL_URI: ClassVar[str] = 'http://terminology.lido-schema.org/lido00132'
    TECHNIQUE_URI: ClassVar[str] = 'http://terminology.lido-schema.org/lido00131'

    _MATERIAL_TECH_MAP: ClassVar[dict[str, str]] = {
        'material': MATERIAL_URI,
        'http://terminology.lido-schema.org/termMaterialsTech_type/material': MATERIAL_URI,
        'technique': TECHNIQUE_URI,
        'technik': TECHNIQUE_URI,
        'http://terminology.lido-schema.org/termMaterialsTech_type/technique': TECHNIQUE_URI,
    }

    type: str | None = attr('type', 'lido', default=None)
    sortorder: int | None = attr('sortorder', 'lido', default=None)

    @field_validator('type', mode='before')
    @classmethod
    def map_material_tech_type(cls, material_tech_type: str) -> str:
        return cls._MATERIAL_TECH_MAP.get(material_tech_type.lower(), material_tech_type)


class Classification(ConceptComplexType):
    _CLASSIFICATION_TYPE_MAP: ClassVar[dict[str, str]] = {
        'material': TermMaterialsTech.MATERIAL_URI,
    }

    type: str | None = attr('type', 'lido', default=None)
    sortorder: int | None = attr('sortorder', 'lido', default=None)

    @field_validator('type', mode='before')
    @classmethod
    def map_classification_type(cls, classification_type: str) -> str:
        return cls._CLASSIFICATION_TYPE_MAP.get(classification_type.lower(), classification_type)


class ClassificationWrap(LidoRecord):
    classification: list[Classification] = element('classification', default=[])


class ObjectClassificationWrap(LidoRecord):
    objectWorkTypeWrap: ObjectWorkTypeWrap = element('objectWorkTypeWrap')
    classificationWrap: ClassificationWrap | None = element('classificationWrap', default=None)


class AppellationValue(PrefMixin):
    text: str | None = None  # FIXME
    pref: str | None = attr('pref', 'lido', default=None)
    lang: str | None = attr('lang', ns='xml', default=None)
    encodinganalog: str | None = attr('encodinganalog', 'lido', default=None)
    label: str | None = attr('label', 'lido', default=None)


class SourceAppellation(LidoRecord):
    text: str
    lang: str | None = attr('lang', ns='xml', default=None)
    encodinganalog: str | None = attr('encodinganalog', 'lido', default=None)
    label: str | None = attr('label', 'lido', default=None)


class AppellationComplexType(LidoRecord):
    appellationValue: list[AppellationValue] = element('appellationValue', 'lido')
    sourceAppellation: list[SourceAppellation] = element('sourceAppellation', 'lido', default=[])


class TitleSet(AppellationComplexType, PrefMixin):
    type: str | None = attr('type', 'lido', default=None)
    sortorder: int | None = attr('sortorder', 'lido', default=None)
    pref: str | None = attr('pref', 'lido', default=None)


class TitleWrap(LidoRecord):
    titleSet: list[TitleSet] = element('titleSet')


class TextComplexType(LidoRecord):
    text: int | float | str | None = Field(union_mode='left_to_right',
                                           default=None)  # FIXME text is required according doku (https://lido-schema.org/schema/latest/lido.html#textComplexType)
    lang: str | None = attr('lang', ns='xml', default=None)
    encodinganalog: str | None = attr('encodinganalog', 'lido', default=None)
    label: str | None = attr('label', 'lido', default=None)

    @field_validator('text', mode='before')
    def fix_floats(cls, v):
        if v.replace(',', '').isnumeric():
            return v.replace(',', '.')
        return v


class InscriptionTranscription(TextComplexType):
    pass


class DescriptiveNoteID(IdentifierComplexType):
    pass


class DescriptiveNoteValue(TextComplexType):
    pass


class SourceDescriptiveNote(TextComplexType):
    pass


class DescriptiveNoteComplexType(LidoRecord):
    type: str | None = attr('type', 'lido', default=None)
    sortorder: int | None = attr('sortorder', 'lido', default=None)
    descriptiveNoteID: list[DescriptiveNoteID] = element('descriptiveNoteID', default=[])
    descriptiveNoteValue: list[DescriptiveNoteValue] = element('descriptiveNoteValue', default=[])
    sourceDescriptiveNote: list[SourceDescriptiveNote] = element('sourceDescriptiveNote', default=[])


class InscriptionDescription(DescriptiveNoteComplexType):
    pass


class Inscriptions(LidoRecord):
    type: str | None = attr('type', 'lido', default=None)
    sortorder: int | None = attr('sortorder', 'lido', default=None)
    inscriptionTranscription: list[InscriptionTranscription] = element('inscriptionTranscription', default=[])
    inscriptionDescription: list[InscriptionDescription] = element('inscriptionDescription', default=[])


class InscriptionsWrap(LidoRecord):
    inscriptions: list[Inscriptions] = element('inscriptions', default=[])


class DisplayRepository(TextComplexType):
    pass


class LegalBodyID(IdentifierComplexType):
    @model_validator(mode='after')
    def fix_legal_body_id(self):
        if self.text.startswith('info:isil'):
            self.text = self.text.replace('info:isil', 'http://ld.zdb-services.de/resource/organisations')
            self.type = self.URI_TYPE

        return self


class LegalBodyName(AppellationComplexType):
    pass


class WebResourceComplexType(PrefMixin):
    text: HttpUrl
    pref: str | None = attr('pref', 'lido', default=None)
    formatResource: str | None = attr('formatResource', 'lido', default=None)
    lang: str | None = attr('lang', ns='xml', default=None)
    encodinganalog: str | None = attr('encodinganalog', 'lido', default=None)
    label: str | None = attr('label', 'lido', default=None)


class LegalBodyWeblink(WebResourceComplexType):
    pass


class LegalBodyRefComplexType(LidoRecord):
    legalBodyID: list[LegalBodyID] = element('legalBodyID', default=[])
    legalBodyName: list[LegalBodyName] = element('legalBodyName', default=[])
    legalBodyWeblink: list[LegalBodyWeblink] = element('legalBodyWeblink', default=[])


class RepositoryName(LegalBodyRefComplexType):
    pass


class WorkID(LidoRecord):
    INVENTORY_NUMBER_URI: ClassVar[str] = 'http://terminology.lido-schema.org/lido00113'

    _WORK_ID_TYPE_MAP: ClassVar[dict[str, str]] = {
        'inventarnummer': INVENTORY_NUMBER_URI,
    }

    text: str
    type: str | None = attr('type', 'lido', default=None)
    sortorder: int | None = attr('sortorder', 'lido', default=None)
    encodinganalog: str | None = attr('encodinganalog', 'lido', default=None)
    label: str | None = attr('label', 'lido', default=None)

    @field_validator('type', mode='before')
    @classmethod
    def map_work_id_type(cls, work_id_type: str) -> str:
        return cls._WORK_ID_TYPE_MAP.get(work_id_type.lower(), work_id_type)


class PlaceID(IdentifierComplexType):
    pass


class NamePlaceSet(AppellationComplexType):
    pass


class PlaceClassification(ConceptComplexType):
    type: str | None = attr('type', 'lido', default=None)


class PlaceComplexType(LidoRecord):
    politicalEntity: str | None = attr('politicalEntity', 'lido', default=None)
    geographicalEntity: str | None = attr('geographicalEntity', 'lido', default=None)
    placeID: list[PlaceID] = element('placeID', default=[])
    namePlaceSet: list[NamePlaceSet] = element('namePlaceSet', default=[])
    # TODO gml
    partOfPlace: list['PlaceComplexType'] = element('partOfPlace', default=[])
    placeClassification: list[PlaceClassification] = element('placeClassification', default=[])


class RepositoryLocation(PlaceComplexType):
    pass


class SourceRepositorySet(TextComplexType):
    pass


class RepositorySet(LidoRecord):
    type: str | None = attr('type', 'lido', default=None)
    sortorder: int | None = attr('sortorder', 'lido', default=None)
    displayRepository: list[DisplayRepository] = element('displayRepository', default=[])
    repositoryName: RepositoryName | None = element('repositoryName', default=None)
    workID: list[WorkID] = element('workID', default=[])
    repositoryLocation: RepositoryLocation | None = element('repositoryLocation', default=None)
    sourceRepositorySet: list[SourceRepositorySet] = element('sourceRepositorySet', default=[])


class RepositoryWrap(LidoRecord):
    repositorySet: list[RepositorySet] = element('repositorySet', default=[])


class DisplayState(TextComplexType):
    pass


class DisplayEdition(TextComplexType):
    pass


class SourceStateEdition(TextComplexType):
    pass


class DisplayStateEditionWrap(LidoRecord):
    displayState: list[DisplayState] = element('displayState', default=[])
    displayEdition: list[DisplayEdition] = element('displayEdition', default=[])
    sourceStateEdition: list[SourceStateEdition] = element('sourceStateEdition', default=[])


class RightsType(ConceptComplexType):
    type: str | None = attr('type', 'lido', default=None)


class EarliestDate(LidoRecord):
    text: str | None = None  # FIXME
    type: str | None = attr('type', 'lido', default=None)
    source: str | None = attr('source', 'lido', default=None)
    encodinganalog: str | None = attr('encodinganalog', 'lido', default=None)
    label: str | None = attr('label', 'lido', default=None)


class LatestDate(LidoRecord):
    text: str | None = None  # FIXME
    type: str | None = attr('type', 'lido', default=None)
    source: str | None = attr('source', 'lido', default=None)
    encodinganalog: str | None = attr('encodinganalog', 'lido', default=None)
    label: str | None = attr('label', 'lido', default=None)


class DateComplexType(LidoRecord):
    earliestDate: EarliestDate | None = element('earliestDate', default=None)
    latestDate: LatestDate | None = element('latestDate', default=None)


class RightsDate(DateComplexType):
    pass


class SameAs(BaseXmlModel, ns='owl', nsmap=NSMAP, skip_empty=True):
    text: HttpUrl = None
    resource: HttpUrl | None = attr('resource', 'rdf', default=None)


class RightsHolderComplexType(LidoRecord):
    legalBodyID: list[LegalBodyID] = element('legalBodyID', default=[])
    sameAs: list[SameAs] = element('sameAs', 'owl', default=[])
    legalBodyName: list[LegalBodyName] = element('legalBodyName', default=[])
    legalBodyWeblink: list[LegalBodyWeblink] = element('legalBodyWeblink', default=[])


class RightsHolder(RightsHolderComplexType):
    pass


class CreditLine(TextComplexType):
    pass


class RightsComplexType(LidoRecord):
    rightsType: list[RightsType] = element('rightsType', default=[])
    rightsDate: RightsDate | None = element('rightsDate', default=None)
    rightsHolder: list[RightsHolder] = element('rightsHolder', default=[])
    creditLine: list[CreditLine] = element('creditLine', default=[])


class ObjectDescriptionRights(RightsComplexType):
    pass


class ObjectDescriptionSet(DescriptiveNoteComplexType):
    objectDescriptionRights: list[ObjectDescriptionRights] = element('objectDescriptionRights', default=[])


class ObjectDescriptionWrap(LidoRecord):
    objectDescriptionSet: list[ObjectDescriptionSet] = element('objectDescriptionSet', default=[])


class DisplayObjectMeasurements(TextComplexType):
    pass


class ConceptMixedComplexType(ConceptComplexType, TextComplexType):
    def get_concept_uri(self) -> str | None:
        uri = super().get_concept_uri()
        if uri is None and is_url(self.text):
            return self.text
        return uri


class MeasurementType(ConceptMixedComplexType):
    pass


class MeasurementUnit(ConceptMixedComplexType):
    pass


class MeasurementValue(TextComplexType):
    pass


class MeasurementsSetComplexType(LidoRecord):
    measurementType: MeasurementType = element('measurementType')
    measurementUnit: MeasurementUnit = element('measurementUnit')
    measurementValue: MeasurementValue = element('measurementValue')


class MeasurementsSet(MeasurementsSetComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class ExtentMeasurements(ConceptMixedComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class QualifierMeasurements(ConceptMixedComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class FormatMeasurements(ConceptMixedComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class ShapeMeasurements(ConceptMixedComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class ScaleMeasurements(ConceptMixedComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class ObjectMeasurementsComplexType(LidoRecord):
    measurementsSet: list[MeasurementsSet] = element('measurementsSet', default=[])
    extentMeasurements: list[ExtentMeasurements] = element('extentMeasurements', default=[])
    qualifierMeasurements: list[QualifierMeasurements] = element('qualifierMeasurements', default=[])
    formatMeasurements: list[FormatMeasurements] = element('formatMeasurements', default=[])
    shapeMeasurements: list[ShapeMeasurements] = element('shapeMeasurements', default=[])
    scaleMeasurements: list[ScaleMeasurements] = element('scaleMeasurements', default=[])


class ObjectMeasurements(ObjectMeasurementsComplexType):
    pass


class ObjectMeasurementsSetComplexType(LidoRecord):
    displayObjectMeasurements: list[DisplayObjectMeasurements] = element('displayObjectMeasurements', default=[])
    objectMeasurements: ObjectMeasurements | None = element('objectMeasurements', default=None)


class ObjectMeasurementsSet(ObjectMeasurementsSetComplexType):
    type: str | None = attr('type', 'lido', default=None)
    measurementsGroup: str | None = attr('measurementsGroup', 'lido', default=None)
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class ObjectMeasurementsWrap(LidoRecord):
    objectMeasurementsSet: list[ObjectMeasurementsSet] = element('objectMeasurementsSet', default=[])


class DisplayMaterialsTech(TextComplexType):
    pass


class ExtentMaterialsTech(ConceptMixedComplexType):
    pass


class SourceMaterialsTech(TextComplexType):
    pass


class MaterialsTechComplexType(LidoRecord):
    termMaterialsTech: list[TermMaterialsTech] = element('termMaterialsTech', default=[])
    extentMaterialsTech: list[ExtentMaterialsTech] = element('extentMaterialsTech', default=[])
    sourceMaterialsTech: list[SourceMaterialsTech] = element('sourceMaterialsTech', default=[])


class MaterialsTech(MaterialsTechComplexType):
    pass


class MaterialsTechSetComplexType(LidoRecord):
    displayMaterialsTech: list[DisplayMaterialsTech] = element('displayMaterialsTech', default=[])
    materialsTech: list[MaterialsTech] = element('materialsTech', default=[])


class ObjectMaterialsTechSet(MaterialsTechSetComplexType):
    pass


class ObjectMaterialsTechWrap(LidoRecord):
    objectMaterialsTechSet: list[ObjectMaterialsTechSet] = element('objectMaterialsTechSet', default=[])


class ObjectIdentificationWrap(LidoRecord):
    titleWrap: TitleWrap = element('titleWrap')
    inscriptionsWrap: InscriptionsWrap | None = element('inscriptionsWrap', default=None)
    repositoryWrap: RepositoryWrap | None = element('repositoryWrap', default=None)
    displayStateEditionWrap: DisplayStateEditionWrap | None = element('displayStateEditionWrap', default=None)
    objectDescriptionWrap: ObjectDescriptionWrap | None = element('objectDescriptionWrap', default=None)
    objectMeasurementsWrap: ObjectMeasurementsWrap | None = element('objectMeasurementsWrap', default=None)
    objectMaterialsTechWrap: ObjectMaterialsTechWrap | None = element('objectMaterialsTechWrap', default=None)


class DisplayEvent(TextComplexType):
    pass


class EventID(IdentifierComplexType):
    pass


class EventType(ConceptComplexType):
    pass


class RoleInEvent(ConceptComplexType):
    pass


class EventName(AppellationComplexType):
    pass


class DisplayActorInRole(TextComplexType):
    pass


class ActorID(IdentifierComplexType):
    pass


class NameActorSet(AppellationComplexType):
    pass


class NationalityActor(ConceptComplexType):
    pass


class VitalDatesActor(DateComplexType):
    type: str | None = attr('type', 'lido', default=None)


class VitalPlaceActor(PlaceComplexType):
    type: str | None = attr('type', 'lido', default=None)


class GenderActor(ConceptMixedComplexType):
    type: str | None = attr('type', 'lido', default=None)


class ActorComplexType(LidoRecord):
    type: str | None = attr('type', 'lido', default=None)
    actorID: list[ActorID] = element('actorID', default=[])
    # TODO owl:sameAs
    nameActorSet: list[NameActorSet] = element('nameActorSet')
    nationalityActor: list[NationalityActor] = element('nationalityActor', default=[])
    vitalDatesActor: list[VitalDatesActor] = element('vitalDatesActor', default=[])
    vitalPlaceActor: list[VitalPlaceActor] = element('vitalPlaceActor', default=[])
    genderActor: list[GenderActor] = element('genderActor', default=[])


class Actor(ActorComplexType):
    pass


class RoleActor(ConceptComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class AttributionQualifierActor(ConceptMixedComplexType):
    pass


class ExtentActor(ConceptMixedComplexType):
    pass


class SourceActorInRole(TextComplexType):
    pass


class ActorInRoleComplexType(LidoRecord):
    actor: Actor = element('actor')
    roleActor: list[RoleActor] = element('roleActor', default=[])
    attributionQualifierActor: list[AttributionQualifierActor] = element('attributionQualifierActor', default=[])
    extentActor: list[ExtentActor] = element('extentActor', default=[])
    sourceActorInRole: list[SourceActorInRole] = element('sourceActorInRole', default=[])


class ActorInRole(ActorInRoleComplexType):
    pass


class ActorInRoleSetComplexType(LidoRecord):
    displayActorInRole: list[DisplayActorInRole] = element('displayActorInRole', default=[])
    actorInRole: ActorInRole | None = element('actorInRole', default=None)


class EventActor(ActorInRoleSetComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class Culture(ConceptComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class Date(DateComplexType):
    pass


class DisplayDate(TextComplexType):
    pass


class DateSetComplexType(LidoRecord):
    displayDate: list[DisplayDate] = element('displayDate', default=[])
    date: Date | None = element('date', default=None)


class EventDate(DateSetComplexType):
    pass


class PeriodName(ConceptComplexType):
    type: str | None = attr('type', 'lido', default=None)
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class DisplayPlace(TextComplexType):
    pass


class Place(PlaceComplexType):
    pass


class PlaceSetComplexType(LidoRecord):
    displayPlace: list[DisplayPlace] = element('displayPlace', default=[])
    place: Place | None = element('place', default=None)


class EventPlace(PlaceSetComplexType):
    type: str | None = attr('type', 'lido', default=None)
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class EventMethod(ConceptComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class EventMaterialsTech(MaterialsTechSetComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class EventObjectMeasurements(ObjectMeasurementsSetComplexType):
    type: str | None = attr('type', 'lido', default=None)
    measurementsGroup: str | None = attr('measurementsGroup', 'lido', default=None)
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class DisplayObject(TextComplexType):
    pass


class ObjectWebResource(WebResourceComplexType):
    pass


class ObjectID(IdentifierComplexType):
    pass


class ObjectType(ConceptComplexType):
    pass


class ObjectName(AppellationComplexType, PrefMixin):
    sortorder: int | None = attr('sortorder', 'lido', default=None)
    pref: str | None = attr('pref', 'lido', default=None)


class ObjectNote(TextComplexType):
    pass


class ObjectComplexType(LidoRecord):
    objectWebResource: list[ObjectWebResource] = element('objectWebResource', default=[])
    objectID: list[ObjectID] = element('objectID', default=[])
    # TODO owl:sameAs
    objectType: list[ObjectType] = element('objectType', default=[])
    objectName: list[ObjectName] = element('objectName', default=[])
    objectNote: list[ObjectNote] = element('objectNote', default=[])


class Object(ObjectComplexType):
    pass


class ObjectSetComplexType(LidoRecord):
    displayObject: list[DisplayObject] = element('displayObject', default=[])
    object: Object | None = element('object', default=None)


class ThingPresent(ObjectSetComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class EventSetComplexType(LidoRecord):
    displayEvent: list[DisplayEvent] = element('displayEvent', default=[])
    # event: Optional['Event'] = element('event', default=None) # FIXME this isn't working


class RelatedEvent(EventSetComplexType):
    pass


class RelatedEventRelType(ConceptComplexType):
    pass


class RelatedEventSetComplexType(LidoRecord):
    relatedEvent: RelatedEvent | None = element('relatedEvent', default=None)
    relatedEventRelType: RelatedEventRelType | None = element('relatedEventRelType', 'lido', default=None)


class RelatedEventSet(RelatedEventSetComplexType):
    pass


class EventDescriptionSet(DescriptiveNoteComplexType):
    pass


class EventComplexType(LidoRecord):
    eventID: list[EventID] = element('eventID', default=[])
    # TODO owl:sameAs
    eventType: EventType = element('eventType')
    roleInEvent: list[RoleInEvent] = element('roleInEvent', default=[])
    eventName: list[EventName] = element('eventName', default=[])
    eventActor: list[EventActor] = element('eventActor', default=[])
    culture: list[Culture] = element('culture', default=[])
    eventDate: EventDate | None = element('eventDate', default=None)
    periodName: list[PeriodName] = element('periodName', default=[])
    eventPlace: list[EventPlace] = element('eventPlace', default=[])
    eventMethod: list[EventMethod] = element('eventMethod', default=[])
    eventMaterialsTech: list[EventMaterialsTech] = element('eventMaterialsTech', default=[])
    eventObjectMeasurements: list[EventObjectMeasurements] = element('eventObjectMeasurements', default=[])
    thingPresent: list[ThingPresent] = element('thingPresent', default=[])
    relatedEventSet: list[RelatedEventSet] = element('relatedEventSet', default=[])
    eventDescriptionSet: list[EventDescriptionSet] = element('eventDescriptionSet', default=[])


class Event(EventComplexType):
    pass


class EventSetComplexType(LidoRecord):
    displayEvent: list[DisplayEvent] = element('displayEvent', default=[])
    event: Event | None = element('event', default=None)


class EventSet(EventSetComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)
    mostNotableEvent: int | None = attr('mostNotableEvent', 'lido', default=None)


class EventWrap(LidoRecord):
    mostNotableEvent: int | None = attr('mostNotableEvent', 'lido', default=None)
    eventSet: list[EventSet] = element('eventSet', default=[])


class DisplaySubject(TextComplexType):
    pass


class ExtentSubject(ConceptMixedComplexType):
    pass


class SubjectConcept(ConceptComplexType):
    pass


class DisplayActor(TextComplexType):
    pass


class ActorSetComplexType(LidoRecord):
    displayActor: list[DisplayActor] = element('displayActor', default=[])
    actor: Actor | None = element('actor', default=None)


class SubjectActor(ActorSetComplexType):
    pass


class SubjectDate(DateSetComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class SubjectEvent(EventSetComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class SubjectPlace(PlaceSetComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class SubjectObject(ObjectSetComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class SubjectComplexType(LidoRecord):
    type: str | None = attr('type', 'lido', default=None)
    extentSubject: list[ExtentSubject] = element('extentSubject', default=[])
    subjectConcept: list[SubjectConcept] = element('subjectConcept', default=[])
    subjectActor: list[SubjectActor] = element('subjectActor', default=[])
    subjectDate: list[SubjectDate] = element('subjectDate', default=[])
    subjectEvent: list[SubjectEvent] = element('subjectEvent', default=[])
    subjectPlace: list[SubjectPlace] = element('subjectPlace', default=[])
    subjectObject: list[SubjectObject] = element('subjectObject', default=[])


class Subject(SubjectComplexType):
    ICONCLASS_NOTATION_URI: ClassVar[str] = 'http://terminology.lido-schema.org/lido00745'

    _MAP_SUBJECT_TYPE: ClassVar[dict[str, str]] = {
        'ikonographie': ICONCLASS_NOTATION_URI
    }

    @field_validator('type', mode='after')
    @classmethod
    def map_pref(cls, subject_type: str):
        return cls._MAP_SUBJECT_TYPE.get(subject_type.lower(), subject_type)


class SubjectSetComplexType(LidoRecord):
    displaySubject: list[DisplaySubject] = element('displaySubject', default=[])
    subject: Subject | None = element('subject', default=None)


class SubjectSet(SubjectSetComplexType):
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class SubjectWrap(LidoRecord):
    subjectSet: list[SubjectSet] = element('subjectSet', default=[])


class ObjectRelationWrap(LidoRecord):
    subjectWrap: SubjectWrap = element('subjectWrap')


class DescriptiveMetadataComplexType(LidoRecord):
    lang: str = attr('lang', 'xml')
    objectClassificationWrap: ObjectClassificationWrap = element('objectClassificationWrap')
    objectIdentificationWrap: ObjectIdentificationWrap = element('objectIdentificationWrap')
    eventWrap: EventWrap | None = element('eventWrap', default=None)
    objectRelationWrap: ObjectRelationWrap | None = element('objectRelationWrap', default=None)


class RightsWorkSet(RightsComplexType):
    sortorder: int | None = attr('sortorder', default=None)


class RightsWorkWrap(LidoRecord):
    rightsWorkSet: list[RightsWorkSet] = element('rightsWorkSet', default=[])


class RecordID(IdentifierComplexType):
    pass


class RecordType(ConceptComplexType):
    ITEM_LEVEL_URI: ClassVar[str] = 'http://terminology.lido-schema.org/lido00141'

    _MAP_RECORD_TYPE: ClassVar[dict[str, str]] = {
        'einzelobjekt': ITEM_LEVEL_URI
    }

    @model_validator(mode='after')
    def map_record_type(self):
        if self.concept is None and len(self.conceptID) == 0:
            for term in self.term:
                record_type_uri = self._MAP_RECORD_TYPE.get(term.text.lower())
                if record_type_uri is not None:
                    self.concept = Concept(about=HttpUrl(record_type_uri), prefLabel=[PrefLabel(text=term.text)])
        return self


class RecordSource(LegalBodyRefComplexType):
    type: str | None = attr('type', 'lido', default=None)
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class RecordRights(RightsComplexType):
    pass


class RecordInfoID(IdentifierComplexType):
    pass


class RecordInfoLink(WebResourceComplexType):
    pass


class RecordMetadataDate(TextComplexType):
    pass


class RecordInfoSetComplexType(LidoRecord):
    type: str | None = attr('type', 'lido', default=None)
    sortorder: int | None = attr('sortorder', 'lido', default=None)
    recordInfoID: list[RecordInfoID] = element('recordInfoID', default=[])
    recordInfoLink: list[RecordInfoLink] = element('recordInfoLink', default=[])
    recordMetadataDate: list[RecordMetadataDate] = element('recordMetadataDate', default=[])


class RecordInfoSet(RecordInfoSetComplexType):
    pass


class Collection(ObjectSetComplexType):
    pass


class RecordWrap(LidoRecord):
    recordID: list[RecordID] = element('recordID')
    recordType: RecordType = element('recordType')
    recordSource: list[RecordSource] = element('recordSource')
    recordRights: list[RecordRights] = element('recordRights', default=[])
    recordInfoSet: list[RecordInfoSet] = element('recordInfoSet', default=[])
    collection: list[Collection] = element('collection', default=[])


class ResourceID(IdentifierComplexType):
    pass


class LinkResource(WebResourceComplexType):
    codecResource: str | None = attr('codecResource', 'lido', default=None)


class ResourceMeasurementsSet(MeasurementsSetComplexType):
    pass


class ResourceRepresentation(LidoRecord):
    type: str | None = attr('type', 'lido', default=None)
    linkResource: LinkResource = element('linkResource')
    resourceMeasurementsSet: list[ResourceMeasurementsSet] = element('resourceMeasurementsSet', default=[])


class ResourceType(ConceptComplexType):
    pass


class ResourceRelType(ConceptComplexType):
    pass


class ResourcePerspective(ConceptComplexType):
    pass


class ResourceDescription(TextComplexType):
    pass


class ResourceDateTaken(DateSetComplexType):
    pass


class ResourceSource(LegalBodyRefComplexType):
    type: str | None = attr('type', 'lido', default=None)
    sortorder: int | None = attr('sortorder', 'lido', default=None)


class RightsResource(RightsComplexType):
    sortorder: int | None = attr('sortorder', default=None)


class ResourceSetComplexType(LidoRecord):
    resourceID: list[ResourceID] = element('resourceID', default=[])
    resourceRepresentation: list[ResourceRepresentation] = element('resourceRepresentation', default=[])
    resourceType: ResourceType | None = element('resourceType', default=None)
    resourceRelType: list[ResourceRelType] = element('resourceRelType', default=[])
    resourcePerspective: list[ResourcePerspective] = element('resourcePerspective', default=[])
    resourceDescription: list[ResourceDescription] = element('resourceDescription', default=[])
    resourceDateTaken: ResourceDateTaken | None = element('resourceDateTaken', default=None)
    resourceSource: list[ResourceSource] = element('resourceSource', default=[])
    rightsResource: list[RightsResource] = element('rightsResource', default=[])


class ResourceSet(ResourceSetComplexType):
    pass


class ResourceWrap(LidoRecord):
    resourceSet: list[ResourceSet] = element('resourceSet', default=[])


class AdministrativeMetadataComplexType(LidoRecord):
    lang: str = attr('lang', 'xml')
    rightsWorkWrap: RightsWorkWrap = element('rightsWorkWrap', default=RightsWorkWrap())
    recordWrap: RecordWrap = element('recordWrap')
    resourceWrap: ResourceWrap = element('resourceWrap')


class AdministrativeMetadata(AdministrativeMetadataComplexType):
    pass


class Category(ConceptComplexType):
    pass


class LidoRecId(IdentifierComplexType):
    pass


class Lido(LidoRecord, tag='lido'):
    relatedencoding: str | None = attr('relatedencoding', 'lido', default=None)
    lidoRecID: list[LidoRecId] = element('lidoRecID')
    objectPublishedID: list[IdentifierComplexType] = element('objectPublishedID', default=[])
    category: Category | None = element('category', default=None)
    applicationProfile: IdentifierComplexType | None = element('applicationProfile', default=None)
    descriptiveMetadata: DescriptiveMetadataComplexType = element('descriptiveMetadata')
    administrativeMetadata: AdministrativeMetadata = element('administrativeMetadata')

    def get_record_id(self) -> str:
        for record_id in self.lidoRecID:
            if record_id.pref == record_id.PREFERRED_LABEL_URI:
                return record_id.text

        return self.lidoRecID[0].text


class LidoWrap(LidoRecord, tag='lidoWrap'):
    relatedencoding: str | None = attr('relatedencoding', 'lido', default=None)
    lido: list[Lido] = element('lido', default=[])
