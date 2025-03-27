# Pizza Luigi

Pizza Luigi practice site for [Compus IL's WebSec course](https://campus.gov.il/course/cs-gov-cs-websec/).

> [!IMPORTANT]  
> I did not write the code in this repository.
> The only files I created are the `Dockerfile` and `docker-compose.yaml`.  
> The rights to the code are reserved by [The Cyber Education Center](https://cyber.org.il/).

## Motivation

This repository simplifies the installation process of the WebSec course practice site.

The course instructs students to install and run the practice site via Virtual Machines, which are heavy and complicated to set up.

This code base contains an exact replica of the Pizza Luigi site source code, along with a new Docker configuration for running it locally.

## How to Run

> [!TIP]  
> The site is written in Python, but you don’t need to modify any code to run it. It’s actually better to focus on the course material rather than the site’s implementation.

### Prerequisites

Make sure you have the following installed:

- MySQL (local, with Hilma's development credentials)
- Docker ([installation guide](https://docs.docker.com/engine/install/))

### Running the Site

Create a new MySQL database named `pizza_db`.

The first time you run the site, you have to build the image:

```sh
docker build -t pizza-luigi .
```

To expose the site run:

```sh
docker run --network="host" pizza-luigi
```

**That's it!**

The Pizza Luigi site is now exposed at the URL http://localhost:8080/.

---

## Additional Information

- The source code of the Pizza Luigi site was retrieved from the virtual machine image provided for installation here. It was found in the machine under the directory `/opt/pizzaCyber-master`.

- The Docker image is based on `python:2.7` to match the site's code syntax.

- The following parts of the code are not in use but were not removed to maintain the original code without modifications:
  `/infra`, `pizza_site_uwsgi.ini`, `pizza_site-old.py`, `startup.sh`
