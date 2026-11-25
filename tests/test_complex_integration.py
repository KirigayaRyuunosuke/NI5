import pytest
from src.models import Apartment, ApartmentSettlement, Bill, Parameters, Tenant, TenantSettlement, Transfer
from src.manager import Manager

def test_apartment_costs():
    manager = Manager(Parameters())
    assert manager.get_apartment_costs('apartment-1', 2024, 1) is None

    assert manager.get_apartment_costs('apart-polanka', 2024, 1) == 0.0

    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == 910.0


def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs is None

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0
    
    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0



def test_create_apartment_settlement():
    manager = Manager(Parameters())

    assert manager.create_apartment_settlement('apartment-1', 2024, 1) is None

    settlement_no_bills = manager.create_apartment_settlement('apart-polanka', 2024, 1)
    assert settlement_no_bills is not None
    assert isinstance(settlement_no_bills, ApartmentSettlement)
    assert settlement_no_bills.apartment == 'apart-polanka'
    assert settlement_no_bills.year == 2024
    assert settlement_no_bills.month == 1
    assert settlement_no_bills.total_rent_pln == 0.0
    assert settlement_no_bills.total_bills_pln == 0.0
    assert settlement_no_bills.total_due_pln == 0.0

    settlement_json_bills = manager.create_apartment_settlement('apart-polanka', 2025, 1)
    assert settlement_json_bills is not None
    assert settlement_json_bills.total_bills_pln == 910.0
    assert settlement_json_bills.total_due_pln == -910.0

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-10',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1000.0,
        type='rent'
    ))
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=250.0,
        type='electricity'
    ))
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-04-10',
        settlement_year=2024,
        settlement_month=3,
        amount_pln=500.0,
        type='rent'
    ))

    settlement_feb = manager.create_apartment_settlement('apart-polanka', 2024, 2)
    assert settlement_feb is not None
    assert settlement_feb.total_bills_pln == 1250.0
    assert settlement_feb.total_due_pln == -1250.0

    settlement_mar = manager.create_apartment_settlement('apart-polanka', 2024, 3)
    assert settlement_mar is not None
    assert settlement_mar.total_bills_pln == 500.0
    assert settlement_mar.total_due_pln == -500.0


def test_create_tenant_settlements():
    manager = Manager(Parameters())


    manager.apartments['test-apt-0'] = Apartment(
        key='test-apt-0', name='Test 0', location='Test', area_m2=40.0, rooms={}
    )
    manager.apartments['test-apt-1'] = Apartment(
        key='test-apt-1', name='Test 1', location='Test', area_m2=40.0, rooms={}
    )
    manager.apartments['test-apt-2'] = Apartment(
        key='test-apt-2', name='Test 2', location='Test', area_m2=50.0, rooms={}
    )

    manager.bills.append(Bill(
        apartment='test-apt-0', date_due='2024-02-01',
        settlement_year=2024, settlement_month=1, amount_pln=600.0, type='rent'
    ))
    manager.bills.append(Bill(
        apartment='test-apt-1', date_due='2024-02-01',
        settlement_year=2024, settlement_month=1, amount_pln=600.0, type='rent'
    ))
    manager.bills.append(Bill(
        apartment='test-apt-2', date_due='2024-02-01',
        settlement_year=2024, settlement_month=1, amount_pln=900.0, type='rent'
    ))


    apt_settlement_0 = manager.create_apartment_settlement('test-apt-0', 2024, 1)
    tenant_settlements_0 = manager.create_tenant_settlements(apt_settlement_0)
    assert tenant_settlements_0 == []
    assert len(tenant_settlements_0) == 0

    manager.tenants['tenant-solo'] = Tenant(
        name='Jan Solo', apartment='test-apt-1', room='r1',
        rent_pln=1500.0, deposit_pln=1500.0,
        date_agreement_from='2024-01-01', date_agreement_to='2024-12-31'
    )
    apt_settlement_1 = manager.create_apartment_settlement('test-apt-1', 2024, 1)
    tenant_settlements_1 = manager.create_tenant_settlements(apt_settlement_1)
    assert len(tenant_settlements_1) == 1
    assert isinstance(tenant_settlements_1[0], TenantSettlement)
    assert tenant_settlements_1[0].tenant == 'tenant-solo'
    assert tenant_settlements_1[0].apartment_settlement == 'test-apt-1'
    assert tenant_settlements_1[0].year == 2024
    assert tenant_settlements_1[0].month == 1
    assert tenant_settlements_1[0].bills_pln == 600.0

    manager.tenants['tenant-a'] = Tenant(
        name='Anna A', apartment='test-apt-2', room='r1',
        rent_pln=1200.0, deposit_pln=1200.0,
        date_agreement_from='2024-01-01', date_agreement_to='2024-12-31'
    )
    manager.tenants['tenant-b'] = Tenant(
        name='Bartek B', apartment='test-apt-2', room='r2',
        rent_pln=1200.0, deposit_pln=1200.0,
        date_agreement_from='2024-01-01', date_agreement_to='2024-12-31'
    )
    apt_settlement_2 = manager.create_apartment_settlement('test-apt-2', 2024, 1)
    tenant_settlements_2 = manager.create_tenant_settlements(apt_settlement_2)
    assert len(tenant_settlements_2) == 2
    assert tenant_settlements_2[0].bills_pln == 450.0
    assert tenant_settlements_2[1].bills_pln == 450.0
    assert tenant_settlements_2[0].rent_pln == 1200.0
    assert tenant_settlements_2[0].total_due_pln == 1650.0
    assert tenant_settlements_2[0].balance_pln == -1650.0



