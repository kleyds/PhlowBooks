from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None


class ReceiptData(BaseModel):
    vendor: Optional[str] = Field(None, description="Merchant or vendor name")
    vendor_tin: Optional[str] = Field(None, description="Philippine TIN, if visible")
    or_number: Optional[str] = Field(None, description="Official Receipt number")
    si_number: Optional[str] = Field(None, description="Sales Invoice number")
    atp_number: Optional[str] = Field(None, description="BIR Authority to Print number, if visible")
    date: Optional[str] = Field(None, description="ISO date YYYY-MM-DD")
    currency: Optional[str] = Field("PHP", description="ISO 4217 currency code")
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    vat_type: Optional[str] = Field(
        None,
        description="One of: vatable, zero_rated, exempt, non_vat",
    )
    vatable_amount: Optional[float] = None
    vat_amount: Optional[float] = None
    total: Optional[float] = None
    doc_type: Optional[str] = Field(
        None,
        description="One of: official_receipt, sales_invoice, gcash, maya, bank_statement, other",
    )
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    line_items: List[LineItem] = Field(default_factory=list)


class ExtractResponse(BaseModel):
    raw_text: str
    data: ReceiptData


class UserPublic(BaseModel):
    id: int
    name: str
    email: str
    plan: str

    model_config = {"from_attributes": True}


class AuthRegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)
    name: str = Field(min_length=1, max_length=255)


class AuthLoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class RegisterResponse(BaseModel):
    message: str
    email: str


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=1)


class ResendVerificationRequest(BaseModel):
    email: str


class SimpleMessageResponse(BaseModel):
    message: str


class MeResponse(BaseModel):
    user: UserPublic


class ClientBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    tin: Optional[str] = Field(None, max_length=25)
    address: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=100)
    software: str = Field("other", max_length=50)


class ClientCreateRequest(ClientBase):
    pass


class ClientUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    tin: Optional[str] = Field(None, max_length=25)
    address: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=100)
    software: Optional[str] = Field(None, max_length=50)


class ClientPublic(ClientBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ClientsResponse(BaseModel):
    clients: List[ClientPublic]


class ClientMetrics(BaseModel):
    client_id: int
    unprocessed_invoices: int = 0
    unreconciled_bank_entries: int = 0
    missing_2307s: int = 0


class ClientMetricsResponse(BaseModel):
    metrics: List[ClientMetrics]


class ReceiptDataPublic(BaseModel):
    vendor: Optional[str] = None
    vendor_tin: Optional[str] = None
    or_number: Optional[str] = None
    si_number: Optional[str] = None
    atp_number: Optional[str] = None
    date: Optional[str] = None
    currency: Optional[str] = "PHP"
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    vat_type: Optional[str] = None
    vatable_amount: Optional[float] = None
    vat_amount: Optional[float] = None
    total: Optional[float] = None
    doc_type: Optional[str] = None
    confidence: Optional[float] = None
    vat_sanity_status: Optional[str] = None
    vat_sanity_message: Optional[str] = None

    model_config = {"from_attributes": True}


class ReceiptDataUpdate(BaseModel):
    vendor: Optional[str] = None
    vendor_tin: Optional[str] = None
    or_number: Optional[str] = None
    si_number: Optional[str] = None
    atp_number: Optional[str] = None
    date: Optional[str] = None
    currency: Optional[str] = "PHP"
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    vat_type: Optional[str] = None
    vatable_amount: Optional[float] = None
    vat_amount: Optional[float] = None
    total: Optional[float] = None
    doc_type: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class LineItemPublic(BaseModel):
    id: int
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None

    model_config = {"from_attributes": True}


class ReceiptCommentPublic(BaseModel):
    id: int
    receipt_id: int
    author_type: str
    author_name: str
    body: str
    is_read_by_bookkeeper: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ReceiptCommentCreateRequest(BaseModel):
    author_name: Optional[str] = Field(None, max_length=255)
    body: str = Field(min_length=1, max_length=2000)


class ReceiptCommentsResponse(BaseModel):
    comments: List[ReceiptCommentPublic]


class ReceiptAuditLogPublic(BaseModel):
    id: int
    receipt_id: int
    user_id: int
    actor_name: Optional[str] = None
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReceiptAuditLogsResponse(BaseModel):
    audit_logs: List[ReceiptAuditLogPublic]


class ReceiptPublic(BaseModel):
    id: int
    client_id: int
    user_id: int
    original_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size_kb: int
    status: str
    raw_text: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    data: Optional[ReceiptDataPublic] = None
    line_items: List[LineItemPublic] = Field(default_factory=list)
    comment_count: int = 0
    unread_portal_comment_count: int = 0
    latest_comment: Optional[ReceiptCommentPublic] = None

    model_config = {"from_attributes": True}


class ReceiptPatchRequest(BaseModel):
    status: Optional[str] = None
    data: Optional[ReceiptDataUpdate] = None
    line_items: Optional[List[LineItem]] = None


class ReceiptUploadItem(BaseModel):
    receipt_id: int
    original_name: Optional[str]
    status: str


class ReceiptUploadResponse(BaseModel):
    receipts: List[ReceiptUploadItem]


class ReceiptsResponse(BaseModel):
    receipts: List[ReceiptPublic]


class BankTransactionPublic(BaseModel):
    id: int
    client_id: int
    user_id: int
    bank_name: Optional[str] = None
    transaction_date: Optional[str] = None
    description: str
    reference: Optional[str] = None
    amount: float
    direction: str
    status: str
    category: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class BankImportResponse(BaseModel):
    imported: int
    skipped_duplicates: int = 0
    skipped_errors: int = 0
    errors: List[str] = Field(default_factory=list)
    transactions: List[BankTransactionPublic]


class BankTransactionsResponse(BaseModel):
    transactions: List[BankTransactionPublic]


class MatchSuggestion(BaseModel):
    receipt: ReceiptPublic
    score: float
    reasons: List[str]
    withholding_variance: Optional[float] = None
    requires_2307: bool = False


class MatchSuggestionsResponse(BaseModel):
    transaction: BankTransactionPublic
    suggestions: List[MatchSuggestion]


class ReconcileRequest(BaseModel):
    receipt_id: int
    match_score: Optional[float] = None
    requires_2307: bool = False


class ReconciliationPublic(BaseModel):
    id: int
    client_id: int
    user_id: int
    receipt_id: int
    bank_transaction_id: int
    status: str
    match_score: Optional[float] = None
    requires_2307: str
    form_2307_status: str = "missing"
    form_2307_original_name: Optional[str] = None
    form_2307_mime_type: Optional[str] = None
    form_2307_uploaded_at: Optional[datetime] = None
    form_2307_requested_at: Optional[datetime] = None
    form_2307_received_at: Optional[datetime] = None
    form_2307_notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReconciliationDetailPublic(ReconciliationPublic):
    receipt: ReceiptPublic
    bank_transaction: BankTransactionPublic
    has_form_2307_file: bool = False


class ReconciliationsResponse(BaseModel):
    reconciliations: List[ReconciliationDetailPublic]


class Form2307UpdateRequest(BaseModel):
    status: Optional[str] = Field(None, pattern=r"^(missing|requested|received|attached)$")
    notes: Optional[str] = Field(None, max_length=2000)


class BulkCategorizeRequest(BaseModel):
    transaction_ids: List[int]
    category: str = Field(min_length=1, max_length=100)


class BulkCategorizeResponse(BaseModel):
    updated: int
    transactions: List[BankTransactionPublic]


class UploadLinkCreateRequest(BaseModel):
    label: Optional[str] = Field(None, max_length=255)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)
    max_uploads: Optional[int] = Field(None, ge=1, le=1000)


class UploadLinkPublic(BaseModel):
    id: int
    client_id: int
    token: str
    label: Optional[str] = None
    max_uploads: Optional[int] = None
    uploads_count: int
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UploadLinksResponse(BaseModel):
    links: List[UploadLinkPublic]


class PortalInfoResponse(BaseModel):
    client_name: str
    label: Optional[str] = None
    uploads_remaining: Optional[int] = None
    expires_at: Optional[datetime] = None
