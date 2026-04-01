from validator_agent import DataValidationRunner
from sample_input import get_sample_inputs


def main():
    runner = DataValidationRunner()
    samples = get_sample_inputs()

    for idx, item in enumerate(samples, start=1):
        print(f"\n{'=' * 80}")
        print(f"RUNNING SAMPLE {idx}: {item['source_name']}")
        print(f"{'=' * 80}")

        result = runner.run_validation(
            source_name=item["source_name"],
            source_type=item["source_type"],
            raw_text=item["raw_text"]
        )

        print("\nVALIDATION RESULT:")
        print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()