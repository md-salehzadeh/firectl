import argparse
import fine_tune
import reset

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="action", required=True, help="Action to run")

# Create subparser for "fine-tune"
fineTuneParser = subparsers.add_parser("fine-tune", help="Fine-tune model")
fineTuneParser.add_argument("--training-file", type=str, required=False, help="Path to the training file")
fineTuneParser.add_argument("--display-name", type=str, required=True, help="Display name")
fineTuneParser.add_argument("--base-model", type=str, required=True, help="Base model")
fineTuneParser.add_argument("--dataset-id", type=str, required=False, help="Dataset ID")
fineTuneParser.add_argument("--job-id", type=str, required=False, help="Job ID")
fineTuneParser.add_argument("--model-id", type=str, required=False, help="Model ID")
fineTuneParser.add_argument("--force-create", type=bool, required=False, help="create dataset and job based on the given parameters")
fineTuneParser.add_argument("--settings-file", type=str, required=False, help="Whether to use settings file or not")
fineTuneParser.add_argument("--epochs", type=int, required=False, help="Number of epochs")

# Create subparser for "reset"
resetParser = subparsers.add_parser("reset", help="Reset all data")
resetParser.add_argument("--seed", action="store_true", required=False, help="Whether to seed resources or not")

args = parser.parse_args()

action = args.action

if action == "fine-tune":
	fine_tune.run(args)
elif action == "reset":
	reset.run(args)
