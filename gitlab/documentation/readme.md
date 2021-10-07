### New project on Gitlab
+  create a new project
    + use "Run CI/CD" for external repository
+ Git repository URL
    + https://github.com/FreeCAD/FreeCAD
+ Project name
    + FreeCAD-CI
+ Project slug
    + FreeCAD-CI
+ click on Create Project


### Settings
+ CI/CD --> General pipelines
    + CI/CD configuration file --> "ci/.gitlab-ci.yml"
    + Time out --> 5h


### Start CI
+ CI/CD --> Editor
    + branch master
    + button commit changes


### Watch CI
+ CI/CD --> pipelines
+ the runners time out is 3h
+ which is just to small for FreeCAD with the runner perfomance given


### Integreation to github repo
+ ATM deactivated because it overwrites the links from berndhahnebach/FreeCAD
+ but the above is the main CI for FreeCAD
+ How do choose if more than one repo have Integreation activated


## Use local machine
### Local Workstation
+ get a Computer with Linux OS installed
+ install Docker and test if it works (Link)


### Settings on gitlab
+  Settings --> CI/CD --> Runnerns --> Shared runners --> deactivate


### Docker commands
+ register on gitlab
```bash
docker run --rm -v \
    gitlab-runner-config:/etc/gitlab-runner gitlab/gitlab-runner register \
    --non-interactive \
    --executor "docker" \
    --docker-image gitlab/gitlab-runner \
    --url "https://gitlab.com/" \
    --registration-token "put_in_the_token" \
    --description "local-docker-runner-freecadci" \
    --tag-list "" \
    --run-untagged="true" \
    --locked="true" \
    --access-level="not_protected"

```

+ run
+ name must be unique on local machine
+ gitlab-runner-freecadci --> bernds repo
+ gitlab-runner-freecadci2 --> official repo
```bash
docker run -d --name gitlab-runner-freecadci --restart always -v /var/run/docker.sock:/var/run/docker.sock -v gitlab-runner-config:/etc/gitlab-runner gitlab/gitlab-runner:latest

```


```bash
docker images && docker volume ls && docker container ls
```

+ DANGER ZONE - DO NOT UNCOMMENT UNLESS YOU KNOW WHAT YOU'RE DOING!
```bash
# docker stop container_id
# docker system prune -a

```


### Gitlab helpers
+ delete a pipeline
```bash
curl --header "PRIVATE-TOKEN: <your_access_token>" --request "DELETE" "https://gitlab.example.com/api/v4/projects/1/pipelines/46"

```
