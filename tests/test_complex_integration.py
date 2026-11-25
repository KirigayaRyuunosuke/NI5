import pytest

from src.manager import Manager
from src.models import Parameters, ApartmentSettlement, TenantSettlement
from src.models import Bill

def test_apartment_costs():
    manager = Manager(Parameters())
    assert manager.get_apartment_costs('apartment-1', 2024, 1) is None

    assert manager.get_apartment_costs('apart-polanka', 2024, 1) == 0.0

    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == 910.0

