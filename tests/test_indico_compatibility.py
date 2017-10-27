import pytest


def test_class_RHRegistrationsActionBase_exists():
    try:
        from indico.modules.events.registration.controllers.management.reglists import RHRegistrationsActionBase
    except ImportError:
        pytest.fail("Could not find class RHRegistrationsActionBase. Make sure you are in the right virtualenv.")
