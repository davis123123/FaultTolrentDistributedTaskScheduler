# FaultTolrentDistributedTaskScheduler


This is the task scheduler app 
Then populate mongodb:
./populate_db


initialize swarm:
sudo docker swarm init --advertise-addr 2601:982:c100:7160::c5bf 

start local registry:
sudo docker service create --name registry --publish published=5000,target=5000 registry:2

build docker-compose:
sudo docker-compose build

push to registry:
sudo docker-compose push

deploy:
sudo docker stack deploy --compose-file docker-compose.yml taskschedulerapp

see logs:
sudo docker service logs --follow

scale down replicas:
sudo docker service update --force --replicas=5 taskschedulerapp_slave


get list of worker services
sudo docker ps | grep taskschedulerapp_slave


clean out all docker images:

sudo docker rm -f $(sudo docker ps -a -q)

# Delete every Docker image
sudo docker rmi -f $(sudo docker images -q)
