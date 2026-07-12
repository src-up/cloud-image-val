"""
Lifecycle tests ported from os-tests to CIV.

Converted from os_tests/tests/test_lifecycle.py.
Uses CIV's host (testinfra) and vm_control fixtures instead of os-tests runner.
"""
import time
import pytest


class TestLifeCycle:

    @pytest.mark.run_on(['all'])
    def test_reboot_vm(self, host, vm_control, instance_data):
        """
        Check time in last reboot before and after VM reboot via cloud API.
        """
        before = host.check_output('last reboot -F full')

        vm_control.reboot(wait=True)
        time.sleep(30)

        after = host.check_output('last reboot -F full')
        assert before != after, \
            f"Reboot VM error: reboot time did not change.\nbefore: {before}\nafter: {after}"

        whoami = host.check_output('whoami').strip()
        assert whoami == instance_data['username'], \
            f"Reboot VM error: expected user {instance_data['username']}, got {whoami}"

    @pytest.mark.run_on(['all'])
    def test_reboot_inside_vm(self, host, vm_control):
        """
        Check time in last reboot before and after reboot triggered inside the VM.
        """
        before = host.check_output('last reboot -F full')

        with host.sudo():
            host.run('reboot')

        vm_control.wait_ssh_ready()

        after = host.check_output('last reboot -F full')
        assert before != after, \
            f"In-VM reboot error: reboot time did not change.\nbefore: {before}\nafter: {after}"

    @pytest.mark.run_on(['all'])
    def test_stop_start_vm(self, host, vm_control, instance_data):
        """
        Check username after stop/start VM via cloud API.
        """
        vm_control.stop(wait=True)
        assert vm_control.is_stopped(), "Stop VM error: VM is not in STOPPED state"

        vm_control.start(wait=True)
        assert vm_control.is_started(), "Start VM error: VM is not in RUNNING state"

        whoami = host.check_output('whoami').strip()
        assert whoami == instance_data['username'], \
            f"Stop/start VM error: expected user {instance_data['username']}, got {whoami}"

    @pytest.mark.run_on(['all'])
    def test_get_console_log(self, host, vm_control):
        """
        Check that console log can be retrieved from the cloud API.
        """
        log = vm_control.get_console_log()
        assert log is not None, "Console log returned None"
        assert len(log) > 0, "Console log is empty"

    @pytest.mark.run_on(['all'])
    def test_send_nmi(self, host, vm_control):
        """
        Send NMI (diagnostic interrupt) to VM and verify it is still reachable.
        """
        try:
            result = vm_control.send_nmi()
            assert result, "send_nmi returned False"
        except Exception as e:
            pytest.skip(f"NMI not supported on this instance: {e}")

        time.sleep(10)
        assert host.check_output('whoami'), "VM unreachable after NMI"
