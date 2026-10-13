from agents.base import AuditTrail


def test_hmac_detects_mutations_even_when_chain_links_match():
    trail = AuditTrail(secret_key="t" * 32)
    first = trail.log("worker", "system", "EVENT", {"success": True})
    trail.log("worker", "system", "EVENT", {"success": False})
    assert trail.verify_integrity()
    exposed = trail.get_trail()
    exposed[0]["actor"] = "modified"
    assert trail.verify_integrity()
    trail.logs[0]["actor"] = "modified"
    assert not trail.verify_integrity()


def test_hmac_detects_modified_signature():
    trail = AuditTrail(secret_key="x" * 32)
    trail.log("worker", "system", "EVENT", {"success": True})
    trail.logs[0]["current_hash"] = "0" * 64
    assert not trail.verify_integrity()
