from models.schema import PaymentIssue, PaymentIssueCreate
from utils.database import supabase


def report_payment_issue_logic(issue_data: PaymentIssueCreate) -> PaymentIssue:
    response = supabase.table("Payment_Issues").insert(issue_data.model_dump()).execute()  # Changed from .dict() to .model_dump()
    if not response.data:
        raise Exception("Failed to report payment issue.")
    return PaymentIssue(**response.data[0])
