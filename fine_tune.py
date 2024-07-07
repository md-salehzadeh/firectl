import time
import subprocess
import utils

def uploadDataset(data):
	command = ["firectl", "create", "dataset", data["dataset_id"], data["training_file"]]

	result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	if result.returncode == 0:
		return {"status": True, "msg": "dataset uploaded successfully"}
	else:
		return {"status": False, "msg": result.stderr}

def createFinetuningJob(data):
	command = [
		'firectl', 'create', 'fine-tuning-job',
		f'--dataset={data["dataset_id"]}',
		f'--job-id={data["job_id"]}',
		f'--model-id={data["model_id"]}',
		f'--display-name={data["display_name"].replace(" ", "_")}',
		f'--base-model={data["base_model"]}',
		f'--epochs={data["epochs"]}',
	]

	if data["settings_file"]:
		command.append(f'--settings-file={data["settings_file"]}')
	else:
		command.append('--kind=conversation')

	_command = [' '.join(command[:3])] + command[3:]

	print(' \\\n    '.join(_command))

	result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	if result.returncode == 0:
		return {"status": True, "msg": "fine-tuning job created successfully"}
	else:
		return {"status": False, "msg": result.stderr}

def trackFinetuningJob(data):
	command = ["firectl", "get", "fine-tuning-job", data["job_id"]]

	result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	if result.returncode == 0:
		jobResult = {
			"state": "",
			"status": {
				"code": "",
				"message": "",
			},
		}

		for line in result.stdout.split('\n'):
			if line.startswith('State: '):
				jobResult["state"] = line.split('State:')[1].strip().upper()

			elif line.strip().startswith('Code: '):
				jobResult["status"]["code"] = line.strip().split('Code:')[1].strip().upper()

			elif line.strip().startswith('Message: '):
				jobResult["status"]["message"] = line.strip().split('Message:')[1].strip().upper()

		return {"status": True, "msg": "", "data": jobResult}
	else:
		return {"status": False, "msg": result.stderr}

def deployModel(data):
	command = ["firectl", "deploy", data['model_id']]

	result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	if result.returncode == 0:
		return {"status": True, "msg": "model deployed successfully"}
	else:
		return {"status": False, "msg": result.stderr}

def run(args):
	data = {
		"dataset_id": args.dataset_id or f"dataset-{utils.uuid(12)}",
		"job_id": args.job_id or f"job-{utils.uuid(12)}",
		"model_id": args.model_id or f"model-{utils.uuid(12)}",
		"display_name": args.display_name,
		"training_file": args.training_file,
		"settings_file": args.settings_file,
		"base_model": args.base_model,
		"epochs": args.epochs or 0,
	}

	if data["base_model"].endswith("llama-v3-8b-instruct"):
		data["base_model"] = "meta-llama/Meta-Llama-3-8B-Instruct"
	elif data["base_model"].endswith("llama-v3-70b-instruct"):
		data["base_model"] = "meta-llama/Meta-Llama-3-70B-Instruct"

	print("\n=====================================")
	print(f"datasetId: {data['dataset_id']}")
	print(f"jobId: {data['job_id']}")
	print(f"modelId: {data['model_id']}")
	print("=====================================\n")

	# Dataset
	if not args.dataset_id or args.force_create:
		status = False

		tries = 0

		while tries < 5:
			tries += 1

			if tries == 1:
				print(f"uploading dataset file with id `{data['dataset_id']}` ...")
			else:
				time.sleep(5)

				print("retrying ...")

			result = uploadDataset(data)

			if result["status"]:
				print(result["msg"])

				status = True

				break
			else:
				utils.printError(result["msg"])

		if not status:
			exit(1)

	# Fine tuning job
	if not args.job_id or args.force_create:
		status = False

		tries = 0

		while tries < 5:
			tries += 1

			if tries == 1:
				print(f"\ncreating fine-tuning job with id `{data['job_id']}` ...")
			else:
				time.sleep(5)

				print("retrying ...")

			result = createFinetuningJob(data)

			if result["status"]:
				print(f"{result['msg']}\n")

				status = True

				break
			else:
				utils.printError(result["msg"])

		if not status:
			exit(1)

	# Track fine-tuning job
	jobSuccess = False

	retries = 0

	while True:
		result = trackFinetuningJob(data)

		if result["status"]:
			retries = 0

			print("-------------------------------------")
			print(f"state: {result['data']['state']}")
			print(f"status: {result['data']['status']['code']}")
			print(f"data: {result['data']['status']['message'] or '-'}")

			if result["data"]["state"] == "COMPLETED" and result["data"]["status"]["code"] == "OK":
				jobSuccess = True

			if result["data"]["state"] in ["COMPLETED", "FAILED"]:
				break
		else:
			retries += 1

			utils.printError(result["msg"])

			if retries >= 5:
				break

		if not jobSuccess:
			time.sleep(5)

	print("-------------------------------------\n")

	if jobSuccess:
		print("fine-tuning job completed\n")
	else:
		utils.printError("fine-tuning job failed")

		exit(1)

	# Model
	if jobSuccess:
		status = False

		tries = 0

		while tries < 5:
			tries += 1

			if tries == 1:
				print(f"deploying model with id `{data['model_id']}` ...")
			else:
				time.sleep(5)

				print("retrying ...")

			result = deployModel(data)

			if result["status"]:
				print(result["msg"])

				status = True

				break
			else:
				utils.printError(result["msg"])

		if not status:
			exit(1)

	utils.sendNotification('fine-tuning proccess done successfully')
