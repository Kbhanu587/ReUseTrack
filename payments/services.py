from decimal import Decimal
from django.db.models import Sum
from .models import Transaction


def _total(assignment, kind):
    result = Transaction.objects.filter(assignment=assignment, kind=kind).aggregate(total=Sum('amount'))
    return result['total'] or Decimal('0')


def refundable_balance(assignment):
    deposits = _total(assignment, Transaction.Kind.DEPOSIT)
    refunds = _total(assignment, Transaction.Kind.REFUND)
    return deposits - refunds