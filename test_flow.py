
from pipeline_unit import PipelineUnit

def run_tests():
    pipeline = PipelineUnit()

    e1 = pipeline.create_entry("Test feature", "high")
    assert e1["priority"] == "high"

    e2 = pipeline.update_status(e1["id"], "closed")
    assert e2["status"] == "closed"

    print("All tests passed!")

if __name__ == "__main__":
    run_tests()
