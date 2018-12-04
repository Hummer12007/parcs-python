# PARCS Python

You can browse the PDF version at https://git.sr.ht/%7Ehummer12007/parcs-python/tree/master/parcs-python.pdf

Docker image available at https://hub.docker.com/r/hummer12007/parcs-node/

## Google Cloud deployment tutorial

### Preparation

1. Install Google Cloud SDK
2. Login to gcloud: `gcloud auth login`
3. Create a project: `gcloud projects create project-name`. You need to invent your own cute project name here.
4. Select the project: `gcloud config set project parcs-name`.
5. You need to enable Cloud and Billing API using Google Cloud Console here (you will be prompted to do so later otherwise).
5. Set region and zone: `gcloud config set compute/zone europe-north1-a`, `gcloud config set compute/region europe-north1`.
6. Configure firewall: `gcloud compute   firewall-rules create allow-all --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=all --source-ranges=0.0.0.0/0`

### Instance creation

1. Create the master instance: `gcloud compute instances create-with-container master --container-image=registry.hub.docker.com/hummer12007/parcs-node --container-env PARCS_ARGS="master"`

Example output:

```
NAME    ZONE             MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP    STATUS
master  europe-north1-a  n1-standard-1               10.166.0.2   35.228.130.74  RUNNING
```

You need to record the external IP, it will be referred to as `$MASTER_IP` later.

2. Create the workers (you can create as many as you wish): `gcloud compute instances create-with-container worker1 worker2 worker3 --container-image=registry.hub.docker.com/hummer12007/parcs-node --container-env PARCS_ARGS="worker 10.166.0.2"`

3. The PARCS web interface will be available at http://$MASTER_IP:8080

