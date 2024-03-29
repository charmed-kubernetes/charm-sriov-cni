import logging

import pytest

log = logging.getLogger(__name__)


@pytest.mark.abort_on_fail
@pytest.mark.skip_if_deployed
async def test_build_and_deploy(ops_test, k8s_model):
    log.info("Building charm...")
    charm = await ops_test.build_charm(".")

    k8s_alias = k8s_model[1]
    with ops_test.model_context(k8s_alias) as model:
        await ops_test.juju(
            "deploy",
            "-m",
            model.info.name,
            charm,
            "--trust",
            fail_msg="Deploy charm failed",
        )
        await ops_test.model.block_until(
            lambda: "sriov-cni" in ops_test.model.applications,
            timeout=60,
        )
        await model.wait_for_idle(status="active", timeout=60 * 60)
