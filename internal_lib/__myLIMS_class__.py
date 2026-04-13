from pydantic import BaseModel, field_validator, ValidationError
from typing import Optional, List, Generic, TypeVar, Union
from datetime import datetime, date
from pydantic import BaseModel
from decimal import Decimal
import pandas as pd, json, sys

T = TypeVar("T", bound=BaseModel)

class BaseIntModel(BaseModel):
    @staticmethod
    def _normalize_int(v):

        if v is None:
            return None
        
        if isinstance(v, float) and pd.isna(v):
            return None

        if isinstance(v, pd.Series):
            if v.empty:
                return None

        if isinstance(v, str):
            v = v.strip()

            if v == "":
                return None

            if v.isdigit():
                return int(v)

            return v

        if isinstance(v, (int, float)):
            return int(v)

        return v

    @field_validator("*", mode="before")
    def normalize_all_int_fields(cls, v):
        return cls._normalize_int(v)
    
    @classmethod
    def model_validate(cls, data, *args, **kwargs):
        try:
            return super().model_validate(data, *args, **kwargs)
        except ValidationError as e:
            print(f"\nERROR de validación en {cls.__name__}", file=sys.stderr)
            print("Info:", file=sys.stderr)
            try:
                print(json.dumps(data, indent=4, ensure_ascii=False), file=sys.stderr)
            except Exception:
                print("(no se pudo serializar el objeto recibido)", file=sys.stderr)
            print("\nDetalle del error:", file=sys.stderr)
            raise

class PageResult(BaseIntModel, Generic[T]):
    Result: List[T]              # lista de objetos del tipo T
    Skip: Optional[int] = None   # número de registros adelantados
    Count: int                   # registros en esta página
    TotalCount: int              # total de registros que cumplen el criterio

class SampleInfoInsert(BaseIntModel):
    InfoId:	                    int
    DisplayValue:               Optional[Union[str, int]] = None
    Attribute:                  Optional[int]
    InfoGroupId:                int	
	
    ValueEquipmentId:	        Optional[int] = None	
    ValueAccountId:	            Optional[int] = None	
    ValueConsumableMovementId:  Optional[int] = None	
    ValueFileId:                Optional[int] = None	
    Inherit:                    Optional[bool] = None	
    Inherited:                  Optional[bool] = None	
    RequiredValue:              Optional[bool] = None

    @field_validator("DisplayValue", mode="before")
    def limpiar_display_value(cls, v):
        if v is None:
            return None

        # Si es string, revisar
        if isinstance(v, str):
            v = v.strip()
            
            # if v.strip().lower() in {"nan", "n/a", "n-a"}:
            if v.lower() in {"nan", "n-a"}:
                return None

            # Si es string pero contiene un número, conviértelo
            if v.isdigit():
                return int(v)

            if v.lower() == "si":
                return "Si"
            if v.lower() == "no":
                return "No"
        
        return v

class SampleAnalysisInsert(BaseIntModel):
    InfoId:                Optional[int]
    MethodId:              Optional[int]
    AnalysisGroupId:       Optional[int] = None
    MeasurementUnitId:     Optional[int] = None

    # def __init__(self, **data):
    #     super().__init__(**data)
    #     input(f"[SampleAnalysisInsert creado] {self}")


class SampleSpecificationInsert(BaseIntModel):
    SpecificationId:        Optional[int] = None

class SampleInsert(BaseIntModel):
    Identification:         str
    ControlIdentification:  Optional[str]	
    TakenDateTime:          Optional[datetime]	
    SampleTypeId:           Optional[int]	#get_int
    ServiceCenterId:        int	
    CollectionPointId:      Optional[int]	
    PriceListId:            int
    ConclusionTime:         Optional[int]	
    ConclusionTimeFixed:    bool	
    AccountId:              Optional[int] #get_int
    RelatedAccountId:       Optional[int]	
    SampleReasonId:         Optional[int]	
    ReferenceKey:           Optional[str]	
    SyncPortal:             bool	
    Latitude:               Optional[float]
    Altitude:               Optional[float]
    Longitude:              Optional[float]
    groupId:                Optional[int]	
    UpdateTermAndPrice:     bool
    Infos:                  List[SampleInfoInsert]
    Analyses:               Optional[List[SampleAnalysisInsert]] = None
    Specifications:         Optional[List[SampleSpecificationInsert]] = []

class User(BaseIntModel):
    Active: Optional[bool] = None
    Id: int
    Identification: str
    Email: Optional[str] = None

class ServiceCenter(BaseIntModel):
    Active: Optional[bool] = None
    Id: int
    Identification: str

class AccountTypeBasic(BaseIntModel):
    Active: Optional[bool] = None
    RequireRegistryNumber: bool
    AccountTypeRegistryTypeId: Optional[int] = None
    Id: int
    Identification: str

class PriceListBasic(BaseIntModel):
    Active: Optional[bool] = None
    Expire: Optional[datetime] = None
    ConsiderServiceCenterPriceListFromSampleOrWork: Optional[bool] = None
    Id: Optional[int] = None
    Identification: Optional[str] = None

class AccountBasic(BaseIntModel):
    Complement: Optional[Union[str, int]] = None
    ReferenceKey: Optional[str] = None
    AccountType: AccountTypeBasic
    PriceList: Optional[PriceListBasic] = None
    Active: Optional[bool] = None
    RelatedAccountRequired: bool
    RegistryNumber: Optional[str] = None
    CultureId: Optional[str] = None
    Id: int
    Identification: str

class CountryBasic(BaseIntModel):
    Id: int
    Identification: str
    ShortName: str

class StateBasic(BaseIntModel):
    Id: int
    Identification: str
    ShortName: str
    Country: CountryBasic

class CityBasic(BaseIntModel):
    Id: int
    Identification: str
    State: StateBasic

class CollectionPointClassBasic(BaseIntModel):
    Id: int
    Identification: str

class CollectionPointBasic(BaseIntModel):
    Active: Optional[bool] = None
    Address1: str
    ZipCode: str
    District: str
    Latitude: Decimal
    Longitude: Decimal
    Altitude: Decimal
    Route: str
    Sequence: int
    Priority: bool
    UnrestrictedAccessServiceCenter: bool
    Account: 'AccountIdentification'
    Country: CountryBasic
    State: StateBasic
    City: CityBasic
    SampleReason: 'SampleReasonBasic'
    CollectionPointClass: CollectionPointClassBasic
    Id: int
    Identification: str

class AccountIdentification(BaseIntModel):
    Id: int
    Identification: str

class InfoTypeBasic(BaseIntModel):
    Id: int
    Identification: str

class MeasurementUnitBasic(BaseIntModel):
    Description: Optional[str] = None
    Id: Optional[int] = None
    Identification: Optional[str] = None

class ConsumableTypeIdentification(BaseIntModel):
    Id: int
    Identification: str

class InfoOptionBasic(BaseIntModel):
    Id: int
    InfoId: int
    InfoType: InfoTypeBasic
    MeasurementUnit: MeasurementUnitBasic
    ForceScale: int
    ForceSignifDigits: int
    DisplayValue: str

class InfoBasic(BaseIntModel):
    InfoTypeId: Optional[int] = None
    InfoType: Optional[InfoTypeBasic] = None
    Active: Optional[bool] = None
    MeasurementUnit: Optional[MeasurementUnitBasic] = None
    ForceScale: Optional[int] = None
    ForceSignifDigits: Optional[int] = None
    ReadOnlyValue: Optional[bool] = None
    EquipmentTypeId: Optional[int] = None
    AccountTypeId: Optional[int] = None
    AllowAnyValue: Optional[bool] = None
    AllowText: Optional[bool] = None
    ConsumableTypeId: Optional[int] = None
    ConsumableType: Optional[ConsumableTypeIdentification] = None
    Options: Optional[List[InfoOptionBasic]] = None
    DLLFileId: Optional[int] = None
    Custom01: Optional[str] = None
    Custom02: Optional[str] = None
    Custom03: Optional[str] = None
    Custom04: Optional[str] = None
    Id: Optional[int] = None
    Identification: Optional[str] = None

class InfoIdentification(BaseIntModel):
    Id: int
    Identification: str


class ServiceCenterBasic(BaseIntModel):
    Active: Optional[bool] = None
    PriceList: Optional[PriceListBasic] = None
    Id: int
    Identification: str

class SampleConclusionBasic(BaseIntModel):
    Active: Optional[bool] = None
    Id: int
    Identification: str

class QCTestBasic2(BaseIntModel):
    Id: int
    Number: int
    Year: int
    ControlNumber: str
    QCRoutineBatchId: int

class SampleCustomInfo(BaseIntModel):
    DisplayValue: str
    InfoTypeId: int
    ForceScale: int
    ForceSignifDigits: int
    ValueDateTime: date

class SampleStatusBasic(BaseIntModel):
    Id: int
    Identification: str
    BeforeReceive: bool
    AfterPublish: bool
    PortalSampleStatus: bool

class ServiceAreaBasic(BaseIntModel):
    ServiceCenter: ServiceCenterBasic
    ExtraTime: int
    ExternalServiceArea: bool
    Active: Optional[bool] = None
    Id: int
    Identification: str

class LicenseGroupBasic(BaseIntModel):
    Id: int
    Identification: str
    UserReadOnlyAccessCount: int
    UserEditableAccessCount: int

class UserBasic(BaseIntModel):
    Active: Optional[bool] = None
    CultureId: Optional[str] = None
    Login: Optional[str] = None
    Email: Optional[str] = None
    ServiceCenter: Optional[ServiceCenterBasic] = None
    ServiceArea: Optional[ServiceAreaBasic] = None
    Account: Optional[AccountBasic] = None
    SignatureCertFileId: Optional[int] = None
    LicenseGroup: Optional[LicenseGroupBasic] = None
    ReadOnlyAccess: Optional[bool] = None
    Reserved: Optional[bool] = None
    ServiceAreaId: Optional[int] = None
    ExternalUser: Optional[str] = None
    Id: int
    Identification: str

class SampleStatusHistoryBasic(BaseIntModel):
    Id: int
    SampleStatus: SampleStatusBasic
    EditionUser: UserBasic
    EditionDateTime: Optional[datetime] = None

class SampleReasonBasic(BaseIntModel):
    Active: Optional[bool] = None
    Id: Optional[int] = 1
    Identification: Optional[str] = None

class SampleClassBasic(BaseIntModel):
    Id: int
    Identification: str

class SampleTypeParentBasic(BaseIntModel):
    Id: int
    Identification: str
    Active: Optional[bool] = None

class SamplePublishTypeBasic(BaseIntModel):
    Id: int
    Identification: str

class SpecificationBasic(BaseIntModel):
    IdAux: Optional[int] = None
    Version: Optional[int] = None
    LastVersion: Optional[bool] = None
    Description: Optional[str] = None
    Active: Optional[bool] = None
    ControlPlan: Optional[bool] = None
    Id: Optional[int] = None
    Identification: Optional[str] = None


class AccountDetail(BaseIntModel):
    PriceListId: Optional[int] = None
    PriceList: Optional[PriceListBasic] = None	
    Color: Optional[str] = None
    EditionUser: Optional[UserBasic] = None	
    EditionDateTime: Optional[datetime] = None
    Complement: Optional[Union[str, int]] = None
    ReferenceKey: Optional[str] = None
    AccountType: Optional[AccountTypeBasic] = None	
    Active: Optional[bool] = None
    RelatedAccountRequired: Optional[bool] = None	
    RegistryNumber: Optional[str] = None
    CultureId: Optional[str] = None
    Id: Optional[int] = None
    Identification: Optional[str] = None	


class WorkBasic(BaseIntModel):
    Id: int
    ControlNumber: str
    Number: int
    Year: int
    Identification: str
    Active: Optional[bool] = None
    ReferenceKey: Optional[str] = None
    Confidential: bool
    Finished: bool
    WorkType: 'WorkTypeBasic'
    Account: AccountBasic
    RelatedAccount: Optional[AccountBasic] = None
    OwnerUser: UserBasic
    CurrentWorkFlow: 'WorkFlowBasic'
    Priority: 'PriorityBasic'
    ServiceCenter: ServiceCenterBasic
    WorkConclusion: 'WorkConclusionBasic'
    WorkClass: 'WorkClassBasic'
    WorkSubClass: 'WorkSubclassBasic'

class SampleWorkBasic(BaseIntModel):
    Id: int
    Work: WorkBasic

class WorkClassBasic(BaseIntModel):
    Id: int
    Identification: str
    Active: Optional[bool] = None

class WorkConclusionBasic(BaseIntModel):
    Id: int
    Identification: str
    Active: Optional[bool] = None

class WorkFlowStepBasic(BaseIntModel):
    Id: int
    Identification: str
    Active: Optional[bool] = None

class WorkFlowBasic(BaseIntModel):
    Id: int
    WorkFlowStepFrom: WorkFlowStepBasic
    WorkFlowStepTo: WorkFlowStepBasic
    ResponsibleUser: UserBasic
    ResponsibleServiceArea: ServiceAreaBasic
    Conclusion: date
    Execution: date
    EstimatedWork: Decimal
    AllowSamples: bool
    SampleStatus: SampleStatusBasic
    Returned: bool
    CreateDateTime: date
    ExecuteDateTime: date

class PriorityBasic(BaseIntModel):
    Id: int
    Identification: str

class WorkSubclassBasic(BaseIntModel):
    Id: int
    Identification: str
    Active: Optional[bool] = None

class WorkTypeSectionConfigBasic(BaseIntModel):
    SectionId: int
    Order: int
    Visible: bool

class WorkTypeBasic(BaseIntModel):
    Id: int
    MasterId: int
    Identification: str
    Active: Optional[bool] = None
    Confidential: bool
    LastVersion: bool
    Version: int
    Prefix: str
    SectionConfigs: List[WorkTypeSectionConfigBasic]

class AnalysisGroupBasic(BaseIntModel):
    Active: Optional[bool] = None
    KeepLink: bool
    ControlPlan: bool
    Id: int
    Identification: str

class CalcEngineTypeBasic(BaseIntModel):
    Id: int
    Identification: str

class CurrencyBasic(BaseIntModel):
    Id: int
    CurrencyCode: str

class CurrencyDetail(BaseIntModel):
    Id: int
    CurrencyCode: str

class EmailConfigIdentification(BaseIntModel):
    Id: int
    Identification: str

class EntityIdentification(BaseIntModel):
    Id: int
    Identification: str

class EquipmentTypeBasic(BaseIntModel):
    Id: int
    Identification: str
    Active: Optional[bool] = None

class EquipmentBasic(BaseIntModel):
    EquipmentType: EquipmentTypeBasic
    Active: Optional[bool] = None
    AvailableSchedule: bool
    Id: int
    Identification: str

class MailingListIdentification(BaseIntModel):
    Id: int
    Identification: str

class MethodAnalysisTypeBasic(BaseIntModel):
    Id: int
    Identification: str

class MethodStatusBehaviorBasic(BaseIntModel):
    Id: int
    Identification: str

class MethodStatusBasic(BaseIntModel):
    Active: Optional[bool] = None
    MethodStatusBehaviorId: int
    MethodStatusBehavior: MethodStatusBehaviorBasic
    Id: int
    Identification: str

class MethodStatusIdentification(BaseIntModel):
    Id: int
    Identification: str

class MethodMasterBasic(BaseIntModel):
    Active: Optional[bool] = None
    Id: int
    Identification: str

class MethodTypeFlowStatusBasic(BaseIntModel):
    Id: int
    MethodStatusFrom: MethodStatusBasic
    MethodStatusTo: MethodStatusBasic
    MinTimeLimit: Decimal
    MaxTimeLimit: Decimal
    ExecutionDeadline: Decimal
    BeforeReceive: bool
    ManualInitialDate: bool
    Default: bool
    Offline: bool

class MethodTypeBasic(BaseIntModel):
    Id: int
    Identification: str
    Active: Optional[bool] = None
    RequiredMethodReferenceMethod: bool
    FlowStatus: Optional[List[MethodTypeFlowStatusBasic]] = None

class MethodBasic(BaseIntModel):
    MasterId: Optional[int] = None
    Version: Optional[int] = None
    LastVersion: Optional[bool] = None
    QCRoutineBatchIds: Optional[List[int]] = None
    Active: Optional[bool] = None
    Duration: Optional[float] = None
    AvailableSchedule: Optional[bool] = None
    Master: Optional[MethodMasterBasic] = None
    MethodType: Optional[MethodTypeBasic] = None
    CalcEngineType: Optional[CalcEngineTypeBasic] = None
    Id: Optional[int] = -1
    Identification: Optional[str] = None

class MultiCurrencyConfigCurrencyIdIdentification(BaseIntModel):
    Id: int
    Identification: str

class PriceItemTypeBasic(BaseIntModel):
    Id: int
    Identification: str
    Active: Optional[bool] = None

class PriceItemBasic(BaseIntModel):
    PriceItemType: PriceItemTypeBasic
    Price: Decimal
    Bill: bool
    Active: Optional[bool] = None
    EditionUser: 'UserBasic'
    MultiCurrencyConfigCurrencyId: int
    MultiCurrencyConfigCurrency: MultiCurrencyConfigCurrencyIdIdentification
    Id: int
    Identification: str

class PriorityBasic(BaseIntModel):
    Active: Optional[bool] = None
    Id: int
    Identification: str

class QCRoutineBatchBasic(BaseIntModel):
    Id: int
    Identification: str

class QCTestBasic(BaseIntModel):
    Id: int
    Number: int
    Year: int
    ControlNumber: str
    TaskCountLimit: int
    TaskCount: int
    QCRoutineBatchId: int
    QCRoutineBatch: QCRoutineBatchBasic
    Equipment: EquipmentBasic
    Started: date
    Expires: date
    AllRequiredControlSamplesPublished: bool


class SampleMethodStatusHistoryBasic(BaseIntModel):
    Id: int
    MethodStatus: MethodStatusBasic
    IsRework: bool
    InProcess: bool
    EditionUser: 'UserBasic'
    EditionDateTime: Optional[datetime] = None
    ExecuteUser: 'UserBasic'
    ExecuteDateTime: date
    StartUser: 'UserBasic'
    StartDateTime: date

class SampleMethodBasic(BaseIntModel):
    Id: int
    AnalysisDeadline: date
    Conclusion: date
    Sample: 'SampleBasic'
    Method: MethodBasic
    ServiceArea: 'ServiceAreaBasic'
    CurrentStatus: SampleMethodStatusHistoryBasic

class SampleMethodQCTestBasic(BaseIntModel):
    Id: int
    QCTest: QCTestBasic
    SampleMethod: SampleMethodBasic

class TaskPrerequisiteAnalysisBasic(BaseIntModel):
    SampleMethodFinalized: bool
    MethodIdentification: str

class SampleMethodDetail(BaseIntModel):
    QCTests: List[SampleMethodQCTestBasic]
    PrerequisiteAnalyses: List[TaskPrerequisiteAnalysisBasic]
    AnalysisDeadlineEmpty: int
    ConclusionEmpty: int
    SampleCustomInfo: 'SampleCustomInfo'
    Id: int
    AnalysisDeadline: date
    Conclusion: date
    Sample: 'SampleBasic'
    Method: MethodBasic
    ServiceArea: 'ServiceAreaBasic'
    CurrentStatus: SampleMethodStatusHistoryBasic


class SampleStatusIdentification(BaseIntModel):
    Id: int
    Identification: str

class SampleTypeBasic(BaseIntModel):
    #SAMPLE TYPE MATRIZ NO PUEDE SER NULO
    Id: Optional[int] = None  
    Identification: Optional[str] = None
    Prefix: Optional[str] = None
    Active: Optional[bool] = None
    SampleClassId: Optional[int] = None
    SampleClass: Optional[SampleClassBasic] = None
    SamplePublishTypeId: Optional[int]= None
    SamplePublishType: Optional[SamplePublishTypeBasic]= None
    SampleReasonId: Optional[int] = 1
    SampleReason: Optional['SampleReasonBasic']= None
    SampleTypeParentId: Optional[int]= None
    SampleTypeParent: Optional[SampleTypeParentBasic]= None
    ReferenceKey: Optional[str] = None
    PackagingAlert: Optional[bool]= None

class SendEmailRecipientIdentification(BaseIntModel):
    Id: int
    Identification: str

class SendEmailStatusIdentification(BaseIntModel):
    Id: int
    Identification: str

class SendEmailBasic(BaseIntModel):
    Id: int
    Identification: str
    EntityId: int
    Entity: EntityIdentification
    SampleStatusId: int
    SampleStatus: SampleStatusIdentification
    MethodStatusId: int
    MethodStatus: MethodStatusIdentification
    StatusId: int
    Status: SendEmailStatusIdentification
    Active: Optional[bool] = None
    SendEmailRecipientId: int
    SendEmailRecipient: SendEmailRecipientIdentification

class UserIdentification(BaseIntModel):
    Id: int
    Identification: str

class SampleBasic(BaseIntModel):
    Id: int
    Identification: Optional[Union[int,str]]

    ControlIdentification: Optional[Union[int,str]] = None
    Prefix: Optional[str] = None

    ControlNumber: str
    ReferenceKey: Optional[str] = None

    GroupId: int
    Number: int
    Year: int
    SubNumber: int
    Revision: int

    Active: Optional[bool] = None
    SyncPortal: bool
    Received: bool
    Finalized: bool
    Published: bool
    Reviewed: bool

    # fechas que llegan None
    Conclusion: Optional[datetime] = None
    TakenDateTime: Optional[datetime] = None
    ReceivedTime: Optional[datetime] = None
    FinalizedTime: Optional[datetime] = None
    PublishedTime: Optional[datetime] = None
    ReviewedTime: Optional[datetime] = None
    ExpectedCollectionTime: Optional[datetime] = None

    ReferenceSampleId: Optional[int] = None
    ReferenceSample: Optional['SampleBasic'] = None

    ConclusionTime: Optional[int] = None
    ConclusionTimeFixed: bool

    # listas que llegan None → lista vacía
    QCTestsControlSample: Optional[List['QCTestControlSampleBasic']] = []
    SampleWorks: Optional[List['SampleWorkBasic']] = []

    ServiceCenter: 'ServiceCenterBasic'
    SampleConclusion: Optional[SampleConclusionBasic] = None
    PriceList: Optional[PriceListBasic] = None
    SampleReason: SampleReasonBasic
    CurrentStatus: 'SampleStatusHistoryBasic'
    SampleType: 'SampleTypeBasic'

    # vienen None
    CollectionPointId: Optional[int] = None
    CollectionPoint: Optional[CollectionPointBasic] = None

    Account: AccountBasic
    RelatedAccount: Optional[AccountBasic] = None

    # viene None
    CustomInfo: Optional['SampleCustomInfo'] = None

    # vienen None
    TotalPrice: Optional[Decimal] = None
    TotalPriceBusinessUnit: Optional[Decimal] = None

class SampleDetail(BaseIntModel):
    Id: Optional[int] = None
    Identification: Optional[str] = None
    ControlIdentification: Optional[str] = None
    ControlNumber: Optional[str] = None
    ReferenceKey: Optional[str] = None
    Prefix: Optional[str] = None
    GroupId: int
    Number: int
    Year: int
    SubNumber: int
    Revision: int
    StatusWarning: Optional[str] = None
    EditionUser: Optional[UserBasic] = None
    PriceUpdateUser: Optional[UserBasic] = None
    ActivationUser: Optional[UserBasic] = None
    PriceUpdateDateTime: Optional[datetime] = None
    EditionDateTime: Optional[datetime] = None
    ActivationDateTime: Optional[datetime] = None
    Active: Optional[bool] = None
    SyncPortal: bool
    Received: bool
    Finalized: bool
    Published: bool
    Reviewed: bool
    Conclusion: Optional[datetime] = None
    TakenDateTime: Optional[datetime] = None
    ReceivedTime: Optional[datetime] = None
    FinalizedTime: Optional[datetime] = None
    PublishedTime: Optional[datetime] = None
    ReviewedTime: Optional[datetime] = None
    ExpectedCollectionTime: Optional[datetime] = None
    ReferenceSampleId: Optional[int] = None
    ReferenceSample: Optional[SampleBasic] = None
    ConclusionTime: Optional[int] = None
    ConclusionTimeFixed: bool
    QCTestsControlSample: Optional[List['QCTestControlSampleBasic']] = None
    ServiceCenter: ServiceCenterBasic
    SampleConclusion: Optional[SampleConclusionBasic] = None
    PriceList: Optional['PriceListBasic'] = None
    SampleReason: SampleReasonBasic
    CurrentStatus: SampleStatusHistoryBasic
    SampleType: SampleTypeBasic
    CollectionPointId: Optional[int] = None
    CollectionPoint: Optional[CollectionPointBasic] = None
    Account: AccountBasic
    RelatedAccount: Optional[AccountBasic] = None
    SampleWorks: Optional[List['SampleWorkBasic']] = None
    CustomInfo: Optional[SampleCustomInfo] = None
    TotalPrice: Optional[float] = None
    TotalPriceBusinessUnit: Optional[float] = None

class PageResultOfSampleBasic(BaseIntModel):
    Count: int
    TotalCount: int
    Result: Optional[SampleBasic] = None

class QCTestControlSampleBasic(BaseIntModel):
    Id: int
    QCTest: QCTestBasic2
    Sample: SampleBasic

class MethodPrerequisiteAnalysisBasic(BaseIntModel):
    Id: int

    Method: Optional[MethodBasic] = None
    MethodMasterId: Optional[int] = None
    MethodId: Optional[int] = None

    Info: Optional[InfoBasic] = None
    InfoId: Optional[int] = None

    MethodStatus: Optional[MethodStatusBasic] = None
    MethodStatusId: Optional[int] = None

    AutomaticInsert: Optional[bool] = None
    LastVersionMethod: Optional[MethodBasic] = None

class AnalysisGroupAnalysisBasic(BaseIntModel):
    Id:                     Optional[int]
    MethodMaster:           Optional[MethodMasterBasic]
    Info:                   Optional[InfoBasic]

class MethodAnalysisBasic(BaseIntModel):
    Id: Optional[int] = None

    Method: Optional[MethodBasic] = None
    Order: Optional[int] = None

    Uncertainty: Optional[float] = None
    K: Optional[float] = None

    Veff: Optional[str] = None

    DetectionLimit: Optional[float] = None
    QuantificationLimit: Optional[float] = None
    DetectionLimitDisplay: Optional[Union[int,str]] = None
    QuantificationLimitDisplay: Optional[Union[int,str]] = None

    Info01: Optional[str] = None
    Info02: Optional[str] = None
    Info03: Optional[str] = None
    Info04: Optional[str] = None
    Info05: Optional[str] = None
    Info06: Optional[str] = None
    Info07: Optional[str] = None
    Info08: Optional[str] = None
    Info09: Optional[str] = None
    Info10: Optional[str] = None

    MethodAnalysisType: Optional[MethodAnalysisTypeBasic] = None
    Info: Optional[InfoBasic] = None
    InfoType: Optional[InfoTypeBasic] = None
    MeasurementUnit: Optional[MeasurementUnitBasic] = None

    ForceScale: Optional[int] = None
    ForceSignifDigits: Optional[int] = None

    ReferenceMethod: Optional[str] = None
    Attribute: Optional[str] = None
