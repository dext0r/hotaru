from zhaquirks.builder import QuirkBuilder
from zigpy.profiles import zha
from zigpy.zcl.clusters.general import OnOff

sw01 = (
    QuirkBuilder(manufacturer="eWeLink/PTVO", model="ZB-SW01")
    .friendly_name(
        model="ZB-SW01",
        manufacturer="eWeLink",
    )
    .replaces_endpoint(1, device_type=zha.DeviceType.ON_OFF_LIGHT)
    .prevent_default_entity_creation(
        endpoint_id=1,
        cluster_id=OnOff.cluster_id,
        function=lambda entity: entity.device_class == "opening",
    )
)
sw01.add_to_registry()

sw02 = (
    sw01.clone()
    .applies_to("eWeLink/PTVO", "ZB-SW02")
    .friendly_name(
        model="ZB-SW02",
        manufacturer="eWeLink",
    )
    .replaces_endpoint(2, device_type=zha.DeviceType.ON_OFF_LIGHT)
    .prevent_default_entity_creation(
        endpoint_id=2,
        cluster_id=OnOff.cluster_id,
        function=lambda entity: entity.device_class == "opening",
    )
)
sw02.add_to_registry()
