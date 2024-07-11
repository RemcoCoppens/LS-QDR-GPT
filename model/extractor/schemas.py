from typing import List, Optional
from langchain_core.pydantic_v1 import BaseModel, Field

class SchemaLookup:
    @staticmethod
    def get_schema(doctype:str):
        schemas = {
            'KEURINGSRAPPORT': KeuringsRapport,
            'INSPECTIE_ONDERHOUDSRAPPORT': InspectieOnderhoudsRapport
        }

        if doctype in schemas:
            return schemas[doctype]
        else:
            raise ValueError(f"The given document type is not recognized. Please select one of the following: {list(schemas.keys())}")

class KeuringsRapport(BaseModel):
    """
    Een keuringsrapport documenteert de resultaten van een keuring, inclusief informatie over de geïnspecteerde installatie.
    """
    klant_naam: Optional[str] = Field(None, description="Naam van de klant of beheerder die verantwoordelijk is voor de uitgevoerde werkzaamheden.")
    gebouw_naam: Optional[str] = Field(None, description="Naam van het gebouw waarop de werkzaamheden zijn uitgevoerd.")
    adres: Optional[str] = Field(None, description="Adres van de locatie waar de werkzaamheden zijn verricht.")
    soort_installatie: Optional[List[str]] = Field(None, description="Type installatie dat is geïnspecteerd, zoals elektrisch, sanitair, HVAC, enz.")
    element_merk: Optional[List[str]] = Field(None, description="Merk(en) van de geïnspecteerde elementen, zoals apparaten, machines of onderdelen.")
    element_type: Optional[list[str]] = Field(None, description="Type(s) van de geïnspecteerde elementen, bijvoorbeeld boiler, airconditioning, lift, enz.")
    element_ID: Optional[list[str]] = Field(None, description="Unieke identificatiecode(s) van de geïnspecteerde elementen, zoals serienummers, modelnummers, enz.")
    ruimte_nummer: Optional[list[str]] = Field(None, description="Nummer(s) of code(s) die de specifieke ruimte(s) identificeren waarin de elementen zich bevinden.")
    ruimte_omschrijving: Optional[str] = Field(None, description="Beschrijving van de ruimte(s) waarin de inspectie heeft plaatsgevonden, zoals 'kantoor', 'hal', 'technische ruimte', enz.")
    datum_van_keuring: Optional[str] = Field(None, description="Datum waarop de keuring heeft plaatsgevonden, in het formaat YYYY-MM-DD.")
    keuringsresultaat: Optional[list[str]] = Field(None, description="Resultaten van de keuring, bijvoorbeeld 'goedgekeurd', 'afgekeurd', 'vereist onderhoud', enz.")
    herstel_acties: Optional[list[str]] = Field(None, description="Acties die moeten worden ondernomen om eventuele gebreken of tekortkomingen te herstellen.")
    gebreken: Optional[list[str]] = Field(None, description="Eventuele gebreken, defecten of tekortkomingen die zijn geconstateerd tijdens de keuring.")
    opmerkingen: Optional[list[str]] = Field(None, description="Aanvullende opmerkingen van de inspecteur over de staat van de installatie of andere relevante informatie.")
    tijdsbesteding_monteur: Optional[list[str]] = Field(None, description="De tijd die de monteur heeft besteed aan de keuring of aan het uitvoeren van herstelwerkzaamheden, indien van toepassing.")

    @classmethod
    def get_attribute_names(cls) -> list:
        """Retrieve a list of attribute names comprising the schema.

        Returns:
            list: A overview of the attribute names.
        """
        return [attr_name for attr_name in cls.__fields__.keys()]
    
    @classmethod
    def get_attribute_names_and_dtypes(cls) -> list:
        """Retrieve a list of attribute names and datatypes (dtypes) comprising the schema.

        Returns:
            list: A overview of the attribute names and the corresponding data type (dtype).
        """
        attr_info = []
        for attr_name, field in cls.__fields__.items():
            if field.outer_type_ == list:
                attr_type = 'list'
            elif hasattr(field.outer_type_, '__origin__') and field.outer_type_.__origin__ == list:
                attr_type = 'list'
            else:
                attr_type = 'str'
            attr_info.append((attr_name, attr_type))
        return attr_info

    @classmethod
    def get_attribute_names_and_descriptions(cls) -> dict:
        """Retrieve a list of attribute names and descriptions comprising the schema.

        Returns:
            dict: An overview of the attribute names and descriptions.
        """
        return {attr_name:field.field_info.description for (attr_name, field) in cls.__fields__.items()}

    def to_dict(self) -> dict:
        """Transform the attribute names and values of the schema into a dictionary.

        Returns:
            dict: Overview of the attributes and their values.
        """
        return self.dict()

class InspectieOnderhoudsRapport(BaseModel):
    """
    Een Inspectie- en Onderhoudsrapport documenteert de resultaten van een inspectie of onderhoudswerkzaamheden, inclusief informatie over de geïnspecteerde installatie.
    """
    klant_naam: Optional[str] = Field(None, description="De naam van de klant of beheerder die verantwoordelijk is voor de uitgevoerde werkzaamheden.")
    gebouw_naam: Optional[str] = Field(None, description="Naam van het gebouw waar de inspectie of het onderhoud plaatsvond.")
    adres: Optional[str] = Field(None, description="Het adres van de locatie waar de werkzaamheden zijn verricht.")
    soort_installatie: Optional[List[str]] = Field(None, description="Type installatie dat is geïnspecteerd of onderhouden, zoals elektrisch, sanitair, HVAC, enz.")
    element_merk: Optional[List[str]] = Field(None, description="Merk(en) van de geïnspecteerde of onderhouden elementen, zoals apparaten, machines of onderdelen.")
    element_type: Optional[list[str]] = Field(None, description="Type(s) van de geïnspecteerde of onderhouden elementen, bijvoorbeeld boiler, airconditioning, lift, enz.")
    element_capaciteit: Optional[list[str]] = Field(None, description="Capaciteit van de geïnspecteerde of onderhouden elementen, zoals vermogen, volume, of draagvermogen.")
    ruimte_nummer: Optional[list[str]] = Field(None, description="Nummer(s) of code(s) die de specifieke ruimte(s) identificeren waarin de elementen zich bevinden.")
    ruimte_omschrijving: Optional[str] = Field(None, description="Beschrijving van de ruimte(s) waarin de inspectie of het onderhoud plaatsvond, zoals 'kantoor', 'hal', 'technische ruimte', enz.")
    element_ID: Optional[list[str]] = Field(None, description="Unieke identificatiecode(s) van de geïnspecteerde of onderhouden elementen, zoals serienummers, modelnummers, enz.")
    conditie: Optional[list[str]] = Field(None, description="Algemene conditie van de geïnspecteerde of onderhouden elementen, bijvoorbeeld 'goed', 'matig', 'slecht', enz.")
    datum_van_onderhoud_en_inspectie: Optional[str] = Field(None, description="Datum van inspectie of onderhoud in het formaat YYYY-MM-DD.")
    uitgevoerd_onderhoud: Optional[list[str]] = Field(None, description="Uitgevoerde onderhoudswerkzaamheden tijdens de inspectie, zoals 'schoonmaken', 'smeren', 'repareren', enz.")
    gebreken: Optional[list[str]] = Field(None, description="Eventuele gebreken, defecten of tekortkomingen die zijn geconstateerd tijdens de inspectie of het onderhoud.")
    opmerkingen: Optional[list[str]] = Field(None, description="Aanvullende opmerkingen van de inspecteur of monteur over de staat van de installatie of andere relevante informatie.")
    tijdsbesteding_monteur: Optional[list[str]] = Field(None, description="De tijd die de monteur heeft besteed aan de inspectie of aan het uitvoeren van onderhoudswerkzaamheden, indien van toepassing.")

    @classmethod
    def get_attribute_names(cls) -> list:
        """Retrieve a list of attribute names comprising the schema.

        Returns:
            list: A overview of the attribute names.
        """
        return [attr_name for attr_name in cls.__fields__.keys()]
    
    @classmethod
    def get_attribute_names_and_dtypes(cls) -> list:
        """Retrieve a list of attribute names and datatypes (dtypes) comprising the schema.

        Returns:
            list: A overview of the attribute names and the corresponding data type (dtype).
        """
        attr_info = []
        for attr_name, field in cls.__fields__.items():
            if field.outer_type_ == list:
                attr_type = 'list'
            elif hasattr(field.outer_type_, '__origin__') and field.outer_type_.__origin__ == list:
                attr_type = 'list'
            else:
                attr_type = 'str'
            attr_info.append((attr_name, attr_type))
        return attr_info

    @classmethod
    def get_attribute_names_and_descriptions(cls) -> dict:
        """Retrieve a list of attribute names and descriptions comprising the schema.

        Returns:
            dict: An overview of the attribute names and descriptions.
        """
        return {attr_name:field.field_info.description for (attr_name, field) in cls.__fields__.items()}

    def to_dict(self) -> dict:
        """Transform the attribute names and values of the schema into a dictionary.

        Returns:
            dict: Overview of the attributes and their values.
        """
        return self.dict()

    
if __name__ == "__main__":
    schema = SchemaLookup.get_schema('KEURINGSRAPPORT')