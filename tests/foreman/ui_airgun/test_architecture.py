"""Test class for Architecture UI

:Requirement: Architecture

:CaseAutomation: Automated

:CaseLevel: Acceptance

:CaseComponent: UI

:TestType: Functional

:CaseImportance: Low

:Upstream: No
"""
from fauxfactory import gen_string
from nailgun import entities

from robottelo.decorators import fixture, tier2, upgrade


@fixture(scope='module')
def module_org():
    return entities.Organization(id=1, name='Default Organization')


@fixture(scope='module')
def module_loc():
    return entities.Location(id=2, name='Default Location')


@tier2
@upgrade
def test_positive_end_to_end(session, module_org, module_loc):
    """Perform end to end testing for architecture component

    :id: eef14b29-9f5a-41aa-805e-73398ed2b112

    :expectedresults: All expected CRUD actions finished successfully

    :CaseLevel: Integration

    :CaseImportance: High
    """
    name = gen_string('alpha')
    new_name = gen_string('alpha')
    os = entities.OperatingSystem().create()
    os_name = '{} {}'.format(os.name, os.major)
    with session:
        session.organization.select(org_name=module_org.name)
        session.location.select(loc_name=module_loc.name)
        # Create new architecture with assigned operating system
        session.architecture.create({
            'name': name,
            'operatingsystems.assigned': [os_name],
        })
        assert session.architecture.search(name)[0]['Name'] == name
        architecture_values = session.architecture.read(name)
        assert architecture_values['name'] == name
        assert len(architecture_values['operatingsystems']['assigned']) == 1
        assert architecture_values['operatingsystems']['assigned'][0] == os_name
        # Check that architecture is really assigned to operating system
        os_values = session.operatingsystem.read(os_name)
        assert len(
            os_values['operating_system']['architectures']['assigned']) == 1
        assert os_values['operating_system']['architectures']['assigned'][0] == name
        # Update architecture with new name
        session.architecture.update(name, {'name': new_name})
        # seems a bug in widgetastic/airgun => under docker the search box is not cleared before
        # fill
        assert not session.architecture.search(name)
        assert session.architecture.search(new_name)[0]['Name'] == new_name
        # Delete architecture
        session.architecture.delete(new_name)
        assert not session.architecture.search(new_name)
