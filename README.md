# OCF Resource Agent for docker containers

&copy; 2014, Eugene Dementiev

This is an [OCF Resource Agent](http://linux-ha.org/wiki/OCF_Resource_Agents) for docker containers.

## Installation

You have to have [docker-py](https://pypi.python.org/pypi/docker-py/0.5.0) installed.

Copy `ekini` folder to `/usr/lib/ocf/resource.d/`.

## Supported parameters

Should be compatible with `docker run`.

1. container_name - this is the container name,
2. image_name - image to use,
3. volumes - a json-formatted dictionary containing volumes description,
4. ports - Publish a container's port to the host (format: ip:hostPort:containerPort | ip::containerPort | hostPort:containerPort),
5. The command or program to run inside the image.

Here is an example of how to use it:
```
primitive redmine_container ocf:ekini:docker-container \
        params container_name="redmine_web" image_name="redmine" \
               volumes="{\"/var/www/redmine/files\":\"/mnt/shared/data/redmine_files\"}" \
               ports="8000:80" command="/sbin/my_init" \
        op monitor interval="10s"

```

Comments or patches are welcome!