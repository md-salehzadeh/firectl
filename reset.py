import os, time, subprocess, re
import utils, fine_tune

def parseOutput(output, columns):
	data = []

	if not output.strip():
		return data

	lines = output.splitlines()

	headers = list(columns.keys())

	colLocs = []

	for col in columns.values():
		colLocs.append(lines[0].find(col))

		lines[0] = lines[0].replace(col, ' ' * len(col), 1)

	i = 0

	for line in lines[1:]:
		if len(line) < colLocs[len(colLocs) - 1]:
			continue

		line = line.strip()

		for index, colLoc in enumerate(colLocs):
			nextColLoc = (len(colLocs) > index + 1 and colLocs[index + 1]) or 1000

			col = line[colLoc:nextColLoc - 1].strip()

			if index == 0:
				data.append({})

			data[i][headers[index]] = col

		i += 1

	return data

def listDatasets():
	command = ["firectl", "list", "datasets"]

	result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	if result.returncode == 0:
		datasets = parseOutput(result.stdout, {
			"id": "NAME",
			"created": "CREATE TIME",
			"state": "STATE",
			"display_name": "DISPLAY_NAME"
		})

		return {"status": True, "msg": result.stdout, "data": datasets}
	else:
		return {"status": False, "msg": result.stderr}

def deleteDatasets(datasets):
	for dataset in datasets:
		if not dataset["id"]:
			continue;

		status = False

		tries = 0

		while tries < 5:
			tries += 1

			if tries == 1:
				print(f"\ndeleting dataset with id `{dataset['id']}` ...")
			else:
				time.sleep(5)

				print("retrying ...")

			result = deleteDataset(dataset["id"])

			if result["status"]:
				print(result["msg"])

				status = True

				break
			else:
				utils.printError(result["msg"])

		if not status:
			exit(1)

def deleteDataset(id):
	command = ["firectl", "delete", "dataset", id]

	result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	if result.returncode == 0:
		return {"status": True, "msg": 'dataset deleted successfully'}
	else:
		return {"status": False, "msg": result.stderr}

def listJobs():
	command = ["firectl", "list", "fine-tuning-jobs"]

	result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	if result.returncode == 0:
		jobs = parseOutput(result.stdout, {
			"id": "NAME",
			"created": "CREATE TIME",
			"state": "STATE",
			"display_name": "DISPLAY_NAME"
		})

		for job in jobs:
			match = re.search(r'\((.*)\)', job["id"])

			if match:
				job["id"] = match.group(1)

		return {"status": True, "msg": result.stdout, "data": jobs}
	else:
		return {"status": False, "msg": result.stderr}

def deleteJobs(jobs):
	for job in jobs:
		if not job["id"]:
			continue;

		status = False

		tries = 0

		while tries < 5:
			tries += 1

			if tries == 1:
				print(f"\ndeleting job with id `{job['id']}` ...")
			else:
				time.sleep(5)

				print("retrying ...")

			result = deleteJob(job["id"])

			if result["status"]:
				print(result["msg"])

				status = True

				break
			else:
				utils.printError(result["msg"])

		if not status:
			exit(1)

def deleteJob(id):
	command = ["firectl", "delete", "fine-tuning-job", id]

	result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	if result.returncode == 0:
		return {"status": True, "msg": 'job deleted successfully'}
	else:
		return {"status": False, "msg": result.stderr}

def listModels():
	command = ["firectl", "list", "models"]

	result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	if result.returncode == 0:
		models = parseOutput(result.stdout, {
			"id": "NAME",
			"created": "CREATE TIME",
			"kind": "KIND",
			"chat": "CHAT",
			"public": "PUBLIC",
			"state": "STATE",
			"status_message": "STATUS MESSAGE",
		})

		return {"status": True, "msg": result.stdout, "data": models}
	else:
		return {"status": False, "msg": result.stderr}

def deleteModels(models):
	for model in models:
		if not model["id"]:
			continue;

		status = False

		tries = 0

		while tries < 5:
			tries += 1

			if tries == 1:
				print(f"\ndeleting model with id `{model['id']}` ...")
			else:
				time.sleep(5)

				print("retrying ...")

			result = deleteModel(model["id"])

			if result["status"]:
				print(result["msg"])

				status = True

				break
			else:
				utils.printError(result["msg"])

		if not status:
			exit(1)

def deleteModel(id):
	command = ["firectl", "delete", "model", id]

	result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	if result.returncode == 0:
		return {"status": True, "msg": 'model deleted successfully'}
	else:
		return {"status": False, "msg": result.stderr}

def undeployModels(models):
	for model in models:
		if not model["id"] or model["state"] != "DEPLOYED":
			continue;

		status = False

		tries = 0

		while tries < 5:
			tries += 1

			if tries == 1:
				print(f"\nundeploying model with id `{model['id']}` ...")
			else:
				time.sleep(5)

				print("retrying ...")

			result = undeployModel(model["id"])

			if result["status"]:
				print(result["msg"])

				status = True

				break
			else:
				utils.printError(result["msg"])

		if not status:
			exit(1)

def undeployModel(id):
	command = ["firectl", "undeploy", id, "--wait"]

	result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	if result.returncode == 0:
		return {"status": True, "msg": 'model undeployed successfully'}
	else:
		return {"status": False, "msg": result.stderr}

def seeds():
	print("\nseeding ...")

	datasets = {}

	datasetsPath = os.path.join(os.getcwd(), "datasets")

	for f in os.listdir(datasetsPath):
		if f.endswith(".jsonl"):
			name = f"dataset-{f[:-6]}"

			path = os.path.join(datasetsPath, f)

			datasets[name] = path

	if datasets:
		for key, value in datasets.items():
			tries = 0

			while tries < 5:
				tries += 1

				if tries == 1:
					print(f"\nuploading dataset file with id `{key}` ...")
				else:
					time.sleep(5)

					print("retrying ...")

				result = fine_tune.uploadDataset({
					"dataset_id": key,
					"training_file": value,
				})

				if result["status"]:
					print(result["msg"])

					status = True

					break
				else:
					utils.printError(result["msg"])

			if not status:
				exit(1)
	else:
		print("nothing to do")

def run(args):
	# Dataset
	status = False

	tries = 0

	while tries < 5:
		tries += 1

		if tries == 1:
			print("getting list of datasets ...")
		else:
			time.sleep(5)

			print("retrying ...")

		result = listDatasets()

		if result["status"]:
			if len(result["data"]):
				deleteDatasets(result["data"])
			else:
				print("no datasets found")

			status = True

			break
		else:
			utils.printError(result["msg"])

	if not status:
		exit(1)

	# Jobs
	status = False

	tries = 0

	while tries < 5:
		tries += 1

		if tries == 1:
			print("\ngetting list of jobs ...")
		else:
			time.sleep(5)

			print("retrying ...")

		result = listJobs()

		if result["status"]:
			if len(result["data"]):
				deleteJobs(result["data"])
			else:
				print("no jobs found")

			status = True

			break
		else:
			utils.printError(result["msg"])

	if not status:
		exit(1)

	# Models
	status = False

	tries = 0

	while tries < 5:
		tries += 1

		if tries == 1:
			print("\ngetting list of models ...")
		else:
			time.sleep(5)

			print("retrying ...")

		result = listModels()

		if result["status"]:
			if len(result["data"]):
				undeployModels(result["data"])

				deleteModels(result["data"])
			else:
				print("no models found")

			status = True

			break
		else:
			utils.printError(result["msg"])

	if not status:
		exit(1)

	# Seeds
	if args.seed:
		seeds()