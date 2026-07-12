"""
Factory for VM lifecycle controllers.
Returns the right controller class based on instance_data['cloud'].
All data comes from instance_data — no external config files needed.
"""


def _build_params(instance_data):
    """Translate CIV instance_data dict into os-tests params dict format."""
    return {
        'Cloud': {'provider': instance_data.get('cloud', '')},
        'instance_ids': instance_data.get('instance_id', ''),
        'remote_node': instance_data.get('address', ''),
        'username': instance_data.get('username', ''),
        'compartment_id': instance_data.get('compartment_id', ''),
        'availability_domain': instance_data.get('availability_domain', ''),
        'shape': instance_data.get('shape', ''),
        'image_id': instance_data.get('image', ''),
        'region': instance_data.get('region', ''),
        'is_allow_delete': False,
    }


def get(instance_data):
    """Return the right VM controller for the given instance_data['cloud']."""
    cloud = instance_data.get('cloud', '')
    params = _build_params(instance_data)

    if cloud == 'oci':
        from lib.vm_lifecycle.oci import OCIVM
        vm = OCIVM(params)
        vm.id = instance_data['instance_id']
        return vm

    if cloud == 'aws':
        from lib.vm_lifecycle.aws import EC2VM
        vm = EC2VM(params)
        vm.id = instance_data['instance_id']
        return vm

    if cloud == 'azure':
        from lib.vm_lifecycle.azure import AzureVM
        vm = AzureVM(params)
        vm.id = instance_data['instance_id']
        return vm

    if cloud == 'gcloud':
        from lib.vm_lifecycle.gcp import GCPVM
        vm = GCPVM(params)
        vm.id = instance_data['instance_id']
        return vm

    raise ValueError(f"Unsupported cloud: {cloud}. Supported: oci, aws, azure, gcloud")
